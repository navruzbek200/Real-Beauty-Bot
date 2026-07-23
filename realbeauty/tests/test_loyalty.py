from __future__ import annotations

from django.test import TestCase

from apps.analytics.models import ProgressPhoto, UserFeedback
from apps.loyalty.models import (
    LoyaltyAccount,
    LoyaltySettings,
    PointsTransaction,
    Reward,
    RewardRedemption,
)
from apps.loyalty.services import RedeemError, award, redeem, spend, tier_for
from apps.products.models import Product
from apps.users.models import TelegramUser, UserProduct


class TierTests(TestCase):
    def test_thresholds_pick_the_right_tier(self):
        conf = LoyaltySettings.get()
        cases = [
            (0, "bronze"),
            (conf.silver_from - 1, "bronze"),
            (conf.silver_from, "silver"),
            (conf.gold_from, "gold"),
            (conf.platinum_from, "platinum"),
            (conf.platinum_from * 10, "platinum"),
        ]
        for lifetime, expected in cases:
            with self.subTest(lifetime=lifetime):
                self.assertEqual(tier_for(lifetime).code, expected)

    def test_cashback_rises_with_the_tier(self):
        conf = LoyaltySettings.get()
        self.assertEqual(tier_for(0).cashback, conf.bronze_cashback)
        self.assertEqual(tier_for(conf.platinum_from).cashback, conf.platinum_cashback)

    def test_remaining_counts_down_to_the_next_tier(self):
        conf = LoyaltySettings.get()
        info = tier_for(conf.silver_from - 100)
        self.assertEqual(info.next_code, "silver")
        self.assertEqual(info.remaining, 100)

    def test_top_tier_has_nowhere_left_to_go(self):
        info = tier_for(LoyaltySettings.get().platinum_from)
        self.assertIsNone(info.next_at)
        self.assertEqual(info.remaining, 0)
        self.assertEqual(info.progress, 1.0)


class AwardTests(TestCase):
    def setUp(self):
        self.user = TelegramUser.objects.create(
            telegram_id=2001, full_name="Nodira"
        )
        self.conf = LoyaltySettings.get()

    def test_points_land_on_the_balance_and_the_lifetime_total(self):
        result = award(
            self.user, PointsTransaction.Reason.PURCHASE, reference="x:1"
        )
        account = LoyaltyAccount.objects.get(user=self.user)

        self.assertTrue(result.awarded)
        self.assertEqual(account.balance, self.conf.points_purchase)
        self.assertEqual(account.lifetime_points, self.conf.points_purchase)

    def test_the_same_reference_is_only_paid_once(self):
        award(self.user, PointsTransaction.Reason.PURCHASE, reference="x:1")
        second = award(self.user, PointsTransaction.Reason.PURCHASE, reference="x:1")

        self.assertFalse(second.awarded)
        self.assertEqual(
            LoyaltyAccount.objects.get(user=self.user).balance,
            self.conf.points_purchase,
        )

    def test_different_references_both_pay(self):
        award(self.user, PointsTransaction.Reason.PURCHASE, reference="x:1")
        award(self.user, PointsTransaction.Reason.PURCHASE, reference="x:2")
        self.assertEqual(
            LoyaltyAccount.objects.get(user=self.user).balance,
            self.conf.points_purchase * 2,
        )

    def test_crossing_a_threshold_reports_a_tier_change(self):
        result = award(
            self.user,
            PointsTransaction.Reason.MANUAL,
            points=self.conf.silver_from,
            reference="jump",
        )
        self.assertTrue(result.tier_changed)
        self.assertEqual(result.tier.code, "silver")
        self.assertEqual(LoyaltyAccount.objects.get(user=self.user).tier, "silver")

    def test_a_switched_off_program_credits_nothing(self):
        LoyaltySettings.objects.filter(pk=1).update(is_enabled=False)
        result = award(self.user, PointsTransaction.Reason.PURCHASE, reference="x:9")

        self.assertFalse(result.awarded)
        self.assertEqual(PointsTransaction.objects.count(), 0)

    def test_a_zero_valued_reason_credits_nothing(self):
        LoyaltySettings.objects.filter(pk=1).update(points_feedback=0)
        result = award(self.user, PointsTransaction.Reason.FEEDBACK, reference="f:1")
        self.assertFalse(result.awarded)


class SpendTests(TestCase):
    def setUp(self):
        self.user = TelegramUser.objects.create(telegram_id=2002, full_name="Malika")
        award(self.user, PointsTransaction.Reason.MANUAL, points=300, reference="seed")

    def test_spending_within_the_balance_works(self):
        self.assertTrue(
            spend(self.user, 100, reason=PointsTransaction.Reason.MANUAL)
        )
        self.assertEqual(LoyaltyAccount.objects.get(user=self.user).balance, 200)

    def test_a_balance_can_never_go_negative(self):
        self.assertFalse(
            spend(self.user, 1000, reason=PointsTransaction.Reason.MANUAL)
        )
        self.assertEqual(LoyaltyAccount.objects.get(user=self.user).balance, 300)

    def test_spending_does_not_cost_the_customer_their_tier(self):
        # Otherwise redeeming a reward would be a punishment and nobody would.
        before = LoyaltyAccount.objects.get(user=self.user).lifetime_points
        spend(self.user, 300, reason=PointsTransaction.Reason.MANUAL)
        after = LoyaltyAccount.objects.get(user=self.user)

        self.assertEqual(after.balance, 0)
        self.assertEqual(after.lifetime_points, before)


class RedeemTests(TestCase):
    def setUp(self):
        self.user = TelegramUser.objects.create(telegram_id=2003, full_name="Sevara")
        self.reward = Reward.objects.create(
            title="Mini krem", cost_points=200, code_prefix="MINI", stock=1
        )

    def _fund(self, points: int) -> None:
        award(
            self.user,
            PointsTransaction.Reason.MANUAL,
            points=points,
            reference=f"seed:{points}",
        )

    def test_a_successful_claim_deducts_points_and_issues_a_code(self):
        self._fund(500)
        redemption = redeem(self.user, self.reward.pk)

        self.assertTrue(redemption.code.startswith("MINI-"))
        self.assertEqual(redemption.points_spent, 200)
        self.assertEqual(LoyaltyAccount.objects.get(user=self.user).balance, 300)
        self.assertTrue(
            PointsTransaction.objects.filter(
                user=self.user, reason=PointsTransaction.Reason.REDEEM, points=-200
            ).exists()
        )

    def test_claiming_decrements_the_stock(self):
        self._fund(500)
        redeem(self.user, self.reward.pk)
        self.reward.refresh_from_db()

        self.assertEqual(self.reward.stock, 0)
        self.assertFalse(self.reward.is_available)

    def test_too_few_points_claims_nothing(self):
        self._fund(50)
        with self.assertRaises(RedeemError) as ctx:
            redeem(self.user, self.reward.pk)

        self.assertEqual(ctx.exception.code, "not_enough")
        self.assertEqual(RewardRedemption.objects.count(), 0)
        self.assertEqual(LoyaltyAccount.objects.get(user=self.user).balance, 50)

    def test_a_sold_out_reward_cannot_be_claimed(self):
        self._fund(500)
        Reward.objects.filter(pk=self.reward.pk).update(stock=0)

        with self.assertRaises(RedeemError) as ctx:
            redeem(self.user, self.reward.pk)
        self.assertEqual(ctx.exception.code, "unavailable")

    def test_a_switched_off_reward_cannot_be_claimed(self):
        self._fund(500)
        Reward.objects.filter(pk=self.reward.pk).update(is_active=False)

        with self.assertRaises(RedeemError):
            redeem(self.user, self.reward.pk)

    def test_unlimited_stock_stays_unlimited(self):
        Reward.objects.filter(pk=self.reward.pk).update(stock=None)
        self._fund(500)
        redeem(self.user, self.reward.pk)
        self.reward.refresh_from_db()

        self.assertIsNone(self.reward.stock)
        self.assertTrue(self.reward.is_available)

    def test_codes_are_unique(self):
        self._fund(2000)
        Reward.objects.filter(pk=self.reward.pk).update(stock=None)
        codes = {redeem(self.user, self.reward.pk).code for _ in range(5)}
        self.assertEqual(len(codes), 5)


class EarningSignalTests(TestCase):
    """Points are credited where the thing happens, whoever made it happen."""

    def setUp(self):
        self.user = TelegramUser.objects.create(telegram_id=2004, full_name="Zilola")
        self.product = Product.objects.create(name="Serum")
        self.conf = LoyaltySettings.get()

    def _balance(self) -> int:
        account = LoyaltyAccount.objects.filter(user=self.user).first()
        return account.balance if account else 0

    def test_recording_a_purchase_credits_points(self):
        UserProduct.objects.create(user=self.user, product=self.product)
        self.assertEqual(self._balance(), self.conf.points_purchase)

    def test_re_saving_a_purchase_does_not_credit_again(self):
        up = UserProduct.objects.create(user=self.user, product=self.product)
        up.week1_sent = True
        up.save()
        self.assertEqual(self._balance(), self.conf.points_purchase)

    def test_leaving_feedback_credits_points(self):
        UserFeedback.objects.create(user=self.user, product=self.product, week=1)
        self.assertEqual(self._balance(), self.conf.points_feedback)

    def test_only_the_after_photo_pays(self):
        # A before/after pair is one submission; paying per photo would double
        # the reward for sending the same thing twice.
        ProgressPhoto.objects.create(
            user=self.user, product=self.product, label=ProgressPhoto.Label.BEFORE
        )
        self.assertEqual(self._balance(), 0)

        ProgressPhoto.objects.create(
            user=self.user, product=self.product, label=ProgressPhoto.Label.AFTER
        )
        self.assertEqual(self._balance(), self.conf.points_progress)


class RegistrationRewardTests(TestCase):
    def test_signing_up_pays_the_customer_and_whoever_invited_them(self):
        from asgiref.sync import async_to_sync

        from bot.services import user_service

        inviter = TelegramUser.objects.create(
            telegram_id=3001,
            full_name="Taklif qilgan",
            registration_status=TelegramUser.RegistrationStatus.COMPLETED,
        )
        conf = LoyaltySettings.get()

        joined = async_to_sync(user_service.complete_user)(
            telegram_id=3002,
            username=None,
            full_name="Yangi mijoz",
            birth_date="1995-05-05",
            phone_number="+998901112233",
            face_condition="normal",
            source=TelegramUser.RegistrationSource.SELF,
            language="ru",
            registered_by_id=inviter.pk,
        )

        self.assertEqual(joined.language, "ru")
        self.assertIsNotNone(joined.registered_at)
        self.assertEqual(
            LoyaltyAccount.objects.get(user=joined).balance, conf.points_registration
        )
        self.assertEqual(
            LoyaltyAccount.objects.get(user=inviter).balance, conf.points_referral
        )


class TierValidatorTests(TestCase):
    """Admin-facing guard rails on the tier ladder itself."""

    def test_cashback_over_100_is_rejected(self):
        from django.core.exceptions import ValidationError

        settings = LoyaltySettings.get()
        settings.bronze_cashback = 150
        with self.assertRaises(ValidationError):
            settings.full_clean()

    def test_cashback_at_exactly_100_is_allowed(self):
        settings = LoyaltySettings.get()
        settings.platinum_cashback = 100
        settings.full_clean()  # must not raise

    def test_thresholds_out_of_order_are_rejected(self):
        from django.core.exceptions import ValidationError

        settings = LoyaltySettings.get()
        settings.gold_from = 500  # below silver_from's default of 1000
        with self.assertRaises(ValidationError):
            settings.full_clean()

    def test_admin_form_surfaces_the_threshold_error(self):
        from django.contrib.auth.models import User
        from django.urls import reverse

        boss = User.objects.create_superuser("boss5", "b5@example.com", "pw")
        self.client.force_login(boss)
        settings = LoyaltySettings.get()

        response = self.client.post(
            reverse("admin:loyalty_loyaltysettings_change", args=[settings.pk]),
            {
                "is_enabled": "on",
                "points_registration": 50,
                "points_purchase": 100,
                "points_feedback": 30,
                "points_progress": 50,
                "points_referral": 150,
                "points_birthday": 200,
                "points_quiz": 20,
                "bronze_cashback": 3,
                "silver_from": 1000,
                "silver_cashback": 5,
                "gold_from": 500,  # invalid: below silver_from
                "gold_cashback": 7,
                "platinum_from": 7000,
                "platinum_cashback": 10,
            },
        )
        self.assertEqual(response.status_code, 200)  # re-rendered with errors
        self.assertContains(response, "ortib borishi kerak")
