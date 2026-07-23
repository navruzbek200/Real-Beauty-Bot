from __future__ import annotations

from datetime import date
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from apps.bot_settings.models import GlobalSettings
from apps.campaigns.models import MessageTemplate
from apps.loyalty.models import LoyaltyAccount, LoyaltySettings, PointsTransaction
from apps.users.models import TelegramUser
from tasks.scheduled import send_birthday_messages


class BirthdayFlowTests(TestCase):
    """
    Full birthday pipeline: today's message goes out, mentions the discount,
    200 points land in the account, and the customer is told about both.

    Two independent `send_message` call sites are in play here and each needs
    its own patch target: the templated birthday_sale message goes out
    through `tasks.notifications.send_message` (bound at module import time,
    so patching `core.telegram.send_message` after the fact would silently
    miss it), while the loyalty "+200 points" notification re-imports
    `core.telegram.send_message` fresh on every call and so *is* reachable
    that way.
    """

    def setUp(self):
        today = timezone.localdate()
        self.user = TelegramUser.objects.create(
            telegram_id=6001,
            full_name="Tug'ilgan Kun Egasi",
            is_active=True,
            language="uz",
            birth_date=date(1995, today.month, today.day),
        )
        GlobalSettings.objects.update_or_create(
            pk=1, defaults={"birthday_discount_percent": 30}
        )
        MessageTemplate.objects.filter(template_type="birthday_sale").update(
            body=(
                "🎂 <b>{{ user.full_name }}</b>, tug'ilgan kuningiz muborak!\n\n"
                "Sizga sovg'a — barcha mahsulotlarga <b>{{ discount }}%</b> "
                "chegirma! 🎁"
            ),
            is_active=True,
        )

    def _run(self):
        with patch("tasks.notifications.send_message") as templated, patch(
            "core.telegram.send_message"
        ) as loyalty:
            sent = send_birthday_messages()
        return sent, templated, loyalty

    def test_todays_birthday_gets_a_message_naming_the_discount(self):
        sent, templated, _loyalty = self._run()

        self.assertEqual(sent, 1)
        templated.assert_called_once()
        text = templated.call_args.args[1]
        self.assertIn("30%", text)
        self.assertIn("tug'ilgan kuningiz muborak", text)

    def test_200_points_are_credited(self):
        conf = LoyaltySettings.get()
        self._run()

        account = LoyaltyAccount.objects.get(user=self.user)
        self.assertEqual(account.balance, conf.points_birthday)
        self.assertEqual(conf.points_birthday, 200)  # the number the shop asked for
        self.assertTrue(
            PointsTransaction.objects.filter(
                user=self.user,
                reason=PointsTransaction.Reason.BIRTHDAY,
                points=200,
            ).exists()
        )

    def test_the_customer_is_separately_told_about_their_points(self):
        # The birthday_sale template is the discount announcement; the points
        # notification is a second, distinct message from the loyalty system.
        _sent, _templated, loyalty = self._run()

        loyalty.assert_called_once()
        text = loyalty.call_args.args[1]
        self.assertIn("Tug'ilgan kun", text)
        self.assertIn("200", text)

    def test_running_twice_in_one_day_does_not_double_pay(self):
        self._run()
        second_sent, second_templated, second_loyalty = self._run()

        self.assertEqual(second_sent, 0)
        second_templated.assert_not_called()
        second_loyalty.assert_not_called()
        self.assertEqual(
            LoyaltyAccount.objects.get(user=self.user).balance,
            LoyaltySettings.get().points_birthday,
        )

    def test_someone_whose_birthday_is_not_today_is_skipped(self):
        not_today = date(1990, 6, 15)
        if timezone.localdate().month == 6 and timezone.localdate().day == 15:
            not_today = date(1990, 6, 16)
        TelegramUser.objects.create(
            telegram_id=6002, full_name="Boshqa Kun", is_active=True, birth_date=not_today
        )
        sent, templated, _loyalty = self._run()

        self.assertEqual(sent, 1)  # only today's user
        templated.assert_called_once()

    def test_a_customer_who_blocked_the_bot_earns_nothing(self):
        # Nobody actually saw the greeting, so there is nothing to reward —
        # and next year's run will try again from a clean slate.
        from core.telegram import TelegramError

        with patch(
            "tasks.notifications.send_message",
            side_effect=TelegramError("Forbidden: bot was blocked by the user"),
        ) as templated, patch("core.telegram.send_message") as loyalty:
            sent = send_birthday_messages()

        self.assertEqual(sent, 0)
        self.assertFalse(LoyaltyAccount.objects.filter(user=self.user).exists())
        loyalty.assert_not_called()
        templated.assert_called_once()

    def test_a_transient_delivery_failure_also_credits_nothing(self):
        # Distinguishing "blocked forever" from "network hiccup" would need a
        # retry story this task doesn't have; until it does, no message
        # delivered means no points, full stop — same rule either way.
        from core.telegram import TelegramError

        with patch(
            "tasks.notifications.send_message",
            side_effect=TelegramError("Bad Gateway"),
        ):
            sent = send_birthday_messages()

        self.assertEqual(sent, 0)
        self.assertFalse(LoyaltyAccount.objects.filter(user=self.user).exists())

    def test_inactive_customers_are_not_messaged_or_paid(self):
        TelegramUser.objects.filter(pk=self.user.pk).update(is_active=False)
        sent, templated, _loyalty = self._run()

        self.assertEqual(sent, 0)
        templated.assert_not_called()
        self.assertFalse(LoyaltyAccount.objects.filter(user=self.user).exists())
