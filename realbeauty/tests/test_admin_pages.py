"""
Smoke tests for the CRM pages.

`manage.py check` validates admin *declarations*; it does not render anything.
These load each page for real, which is what catches a display method that
raises on live data, a fieldset naming a field the form doesn't have, or a
sidebar link pointing at a url name that no longer exists.
"""

from __future__ import annotations

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.analytics.models import ProgressPhoto, SkinQuizResult, UserFeedback
from apps.analytics.skin_logic import QUESTION_IDS, analyze
from apps.campaigns.models import AutoMessage
from apps.loyalty.models import PointsTransaction, Reward
from apps.loyalty.services import award, redeem
from apps.products.models import Product
from apps.users.models import SellerProfile, TelegramUser, UserProduct

CHANGELISTS = [
    "admin:index",
    "admin:users_telegramuser_changelist",
    "admin:products_product_changelist",
    "admin:products_topproduct_changelist",
    "admin:campaigns_automessage_changelist",
    "admin:campaigns_automessagelog_changelist",
    "admin:campaigns_messagetemplate_changelist",
    "admin:analytics_userfeedback_changelist",
    "admin:analytics_skinquizresult_changelist",
    "admin:analytics_progressphoto_changelist",
    "admin:loyalty_loyaltyaccount_changelist",
    "admin:loyalty_reward_changelist",
    "admin:loyalty_rewardredemption_changelist",
    "admin:loyalty_pointstransaction_changelist",
]


class AdminSmokeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.boss = User.objects.create_superuser("boss", "b@example.com", "pw")

        cls.customer = TelegramUser.objects.create(
            telegram_id=7001,
            full_name="Admin Test",
            phone_number="+998901234567",
            language="ru",
            registration_status=TelegramUser.RegistrationStatus.COMPLETED,
        )
        cls.product = Product.objects.create(
            name="Serum", is_top=True, top_order=1, top_note="Top"
        )
        UserProduct.objects.create(user=cls.customer, product=cls.product)
        UserFeedback.objects.create(user=cls.customer, product=cls.product, week=1, rating=5)
        ProgressPhoto.objects.create(
            user=cls.customer, product=cls.product, label=ProgressPhoto.Label.AFTER
        )

        result = analyze({qid: 4 for qid in QUESTION_IDS})
        SkinQuizResult.objects.create(
            user=cls.customer,
            skin_type=result.skin_type,
            answers=result.answers,
            recommendation_keys=list(result.recommendation_keys),
        )

        cls.reward = Reward.objects.create(title="Kupon", cost_points=10, stock=5)
        award(
            cls.customer,
            PointsTransaction.Reason.MANUAL,
            points=1000,
            reference="admin-test",
        )
        redeem(cls.customer, cls.reward.pk)

        cls.rule = AutoMessage.objects.create(
            name="Sinov qoidasi",
            trigger=AutoMessage.Trigger.AFTER_PURCHASE,
            delay_value=1,
            delay_unit=AutoMessage.Unit.MINUTE,
            body="Salom {{ user.full_name }}",
            button_action=AutoMessage.Action.DISCOUNTS,
            button_label="Chegirmalar",
            is_test_mode=True,
            test_user=cls.customer,
        )

    def setUp(self):
        self.client.force_login(self.boss)

    def test_every_changelist_renders(self):
        for name in CHANGELISTS:
            with self.subTest(page=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 200)

    def test_singleton_settings_pages_redirect_to_their_form(self):
        for name in (
            "admin:bot_settings_globalsettings_changelist",
            "admin:loyalty_loyaltysettings_changelist",
        ):
            with self.subTest(page=name):
                response = self.client.get(reverse(name), follow=True)
                self.assertEqual(response.status_code, 200)

    def test_change_forms_render(self):
        pages = [
            ("admin:campaigns_automessage_change", self.rule.pk),
            ("admin:products_product_change", self.product.pk),
            ("admin:products_topproduct_change", self.product.pk),
            ("admin:users_telegramuser_change", self.customer.pk),
            ("admin:loyalty_reward_change", self.reward.pk),
        ]
        for name, pk in pages:
            with self.subTest(page=name):
                response = self.client.get(reverse(name, args=[pk]))
                self.assertEqual(response.status_code, 200)

    def test_the_summary_escapes_a_customer_name_containing_markup(self):
        # The test-mode line prints the chosen customer; a name is user input.
        TelegramUser.objects.filter(pk=self.customer.pk).update(
            full_name="<script>x</script>"
        )
        response = self.client.get(
            reverse("admin:campaigns_automessage_change", args=[self.rule.pk])
        )
        self.assertNotContains(response, "<script>x</script>")

    def test_adding_products_to_the_top_list_appends_rather_than_collides(self):
        second = Product.objects.create(name="Krem")
        third = Product.objects.create(name="Toner")
        self.client.post(
            reverse("admin:products_product_changelist"),
            {
                "action": "add_to_top",
                "_selected_action": [second.pk, third.pk],
            },
            follow=True,
        )
        second.refresh_from_db()
        third.refresh_from_db()

        self.assertTrue(second.is_top and third.is_top)
        self.assertEqual({second.top_order, third.top_order}, {2, 3})

    def test_manual_point_adjustment_goes_through_the_ledger(self):
        from apps.loyalty.models import LoyaltyAccount

        account = LoyaltyAccount.objects.get(user=self.customer)
        before = account.balance

        self.client.post(
            reverse("admin:loyalty_loyaltyaccount_change", args=[account.pk]),
            {"adjustment": "250", "adjustment_note": "Do'konda berildi"},
            follow=True,
        )
        account.refresh_from_db()

        self.assertEqual(account.balance, before + 250)
        self.assertTrue(
            PointsTransaction.objects.filter(
                user=self.customer,
                reason=PointsTransaction.Reason.MANUAL,
                points=250,
                note="Do'konda berildi",
            ).exists()
        )

    def test_a_negative_adjustment_cannot_overdraw(self):
        from apps.loyalty.models import LoyaltyAccount

        account = LoyaltyAccount.objects.get(user=self.customer)
        before = account.balance

        self.client.post(
            reverse("admin:loyalty_loyaltyaccount_change", args=[account.pk]),
            {"adjustment": str(-(before + 5000)), "adjustment_note": "xato"},
            follow=True,
        )
        account.refresh_from_db()
        self.assertEqual(account.balance, before)


class SellerAccessTests(TestCase):
    """
    A seller runs the counter. They must reach the till pages and nothing that
    changes how the bot behaves.
    """

    @classmethod
    def setUpTestData(cls):
        from apps.users.roles import sync_seller_group

        group = sync_seller_group()
        cls.seller = User.objects.create_user("sotuvchi", password="pw", is_staff=True)
        cls.seller.groups.add(group)
        SellerProfile.objects.create(user=cls.seller, telegram_id=7100)

    def setUp(self):
        self.client.force_login(self.seller)

    def test_seller_can_check_reward_codes(self):
        response = self.client.get(
            reverse("admin:loyalty_rewardredemption_changelist")
        )
        self.assertEqual(response.status_code, 200)

    def test_seller_can_read_quiz_results(self):
        response = self.client.get(
            reverse("admin:analytics_skinquizresult_changelist")
        )
        self.assertEqual(response.status_code, 200)

    def test_seller_cannot_touch_the_points_economy(self):
        for name in (
            "admin:loyalty_loyaltysettings_changelist",
            "admin:loyalty_reward_changelist",
            "admin:campaigns_automessage_changelist",
        ):
            with self.subTest(page=name):
                response = self.client.get(reverse(name))
                self.assertIn(response.status_code, (302, 403))


class RetiredTemplateTests(TestCase):
    """
    The week-1/week-2 wording lives in AutoMessage now.

    Their MessageTemplate rows survive (the migration copied the text across)
    but nothing reads them, so they must not be offered for editing — otherwise
    somebody changes one and waits for a result that never arrives.
    """

    @classmethod
    def setUpTestData(cls):
        cls.boss = User.objects.create_superuser("boss2", "b2@example.com", "pw")

    def setUp(self):
        self.client.force_login(self.boss)

    def test_retired_templates_are_not_listed(self):
        from apps.campaigns.models import MessageTemplate

        response = self.client.get(
            reverse("admin:campaigns_messagetemplate_changelist")
        )
        listed = {obj.template_type for obj in response.context["cl"].result_list}
        self.assertNotIn("week1_checkin", listed)
        self.assertNotIn("week2_progress", listed)
        # The live ones are still there.
        self.assertTrue(
            MessageTemplate.objects.filter(template_type="welcome").exists()
        )
        self.assertIn("welcome", listed)
