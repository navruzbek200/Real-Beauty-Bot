"""
The "rate a product" flow: picking a product, the full handler pipeline
(rating -> optional comment -> save -> admin notification), and the
top-products fallback for customers who haven't bought anything yet.
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock

from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.memory import MemoryStorage
from asgiref.sync import async_to_sync
from django.test import TestCase

from apps.analytics.models import UserFeedback
from apps.products.models import Product
from apps.support.models import SupportSettings
from apps.users.models import TelegramUser, UserProduct
from bot.handlers import feedback, menu
from bot.keyboards import inline

BOT_ID = 1


class FakeUser(SimpleNamespace):
    pass


class FakeChat(SimpleNamespace):
    pass


class FakeMessage(SimpleNamespace):
    def __init__(self, *, chat_id: int, username: str | None = None, text: str = ""):
        super().__init__(
            chat=FakeChat(id=chat_id, username=username),
            from_user=FakeUser(id=chat_id, username=username, language_code="uz"),
            text=text,
            bot=None,
        )
        self.answer = AsyncMock(side_effect=self._record)
        self.sent: list[dict] = []

    async def _record(self, text="", **kwargs):
        self.sent.append({"text": text, **kwargs})
        return self


class FakeCallback(SimpleNamespace):
    def __init__(self, *, data: str, message: FakeMessage, bot):
        super().__init__(data=data, message=message, from_user=message.from_user, bot=bot)
        self.answer = AsyncMock()


class FakeBot:
    def __init__(self):
        self.sent: list[dict] = []

    async def send_message(self, chat_id, text, parse_mode=None, reply_markup=None):
        self.sent.append({"chat_id": chat_id, "text": text})


def fsm_for(chat_id: int) -> FSMContext:
    storage = MemoryStorage()
    key = StorageKey(bot_id=BOT_ID, chat_id=chat_id, user_id=chat_id)
    return FSMContext(storage=storage, key=key)


class MenuFeedbackFallbackTests(TestCase):
    """
    A customer with no purchase on file used to hit a flat "you have no
    products" dead end on the «⭐️ Mahsulotga baho» button — useless for
    exactly the people browsing the top list. It must fall back to the top
    products instead of stopping the flow.
    """

    def setUp(self):
        self.user = TelegramUser.objects.create(
            telegram_id=2001,
            full_name="Sinov",
            registration_status=TelegramUser.RegistrationStatus.COMPLETED,
        )

    def _run(self, chat_id: int):
        state = fsm_for(chat_id)
        msg = FakeMessage(chat_id=chat_id)
        async_to_sync(menu.menu_feedback)(msg, state, "uz")
        return msg

    def test_falls_back_to_top_products_when_nothing_was_purchased(self):
        top = Product.objects.create(name="Top serum", is_top=True, top_order=1)

        msg = self._run(2001)

        self.assertEqual(len(msg.sent), 1)
        keyboard = msg.sent[0]["reply_markup"]
        callbacks = [
            btn.callback_data for row in keyboard.inline_keyboard for btn in row
        ]
        self.assertEqual(callbacks, [f"{inline.CB_SUBMIT_FEEDBACK}{inline.SEP}1{inline.SEP}{top.pk}"])

    def test_owned_products_take_priority_over_the_top_list(self):
        owned = Product.objects.create(name="Sotib olingan")
        Product.objects.create(name="Top serum", is_top=True, top_order=1)
        UserProduct.objects.create(user=self.user, product=owned)

        msg = self._run(2001)

        keyboard = msg.sent[0]["reply_markup"]
        callbacks = [
            btn.callback_data for row in keyboard.inline_keyboard for btn in row
        ]
        self.assertEqual(callbacks, [f"{inline.CB_SUBMIT_FEEDBACK}{inline.SEP}1{inline.SEP}{owned.pk}"])

    def test_nothing_purchased_and_no_top_list_shows_the_empty_state(self):
        msg = self._run(2001)
        self.assertIn("mahsulot", msg.sent[0]["text"].lower())


class FeedbackAdminNotificationTests(TestCase):
    """
    The instant a customer rates a product, the shop's Telegram group must
    hear about it — this is the whole point of collecting ratings at all.
    """

    def setUp(self):
        self.user = TelegramUser.objects.create(
            telegram_id=3001,
            full_name="Malika",
            username="malika01",
            registration_status=TelegramUser.RegistrationStatus.COMPLETED,
        )
        self.product = Product.objects.create(name="Vitamin C serum")
        SupportSettings.objects.update_or_create(pk=1, defaults={"group_chat_id": 555})

    def _submit(self, *, rating: int, text: str, skip_text: bool = False):
        bot = FakeBot()
        state = fsm_for(3001)
        msg = FakeMessage(chat_id=3001, username="malika01")
        msg.bot = bot

        cb1 = FakeCallback(
            data=f"{inline.CB_SUBMIT_FEEDBACK}{inline.SEP}1{inline.SEP}{self.product.pk}", message=msg, bot=bot
        )
        async_to_sync(feedback.start_feedback)(cb1, state, "uz")

        cb2 = FakeCallback(
            data=f"{inline.CB_FEEDBACK_RATING}{inline.SEP}{rating}", message=msg, bot=bot
        )
        async_to_sync(feedback.feedback_rating)(cb2, state, "uz")

        if skip_text:
            cb3 = FakeCallback(data=inline.CB_SKIP_FEEDBACK_TEXT, message=msg, bot=bot)
            async_to_sync(feedback.feedback_skip_text)(cb3, state, "uz")
        else:
            msg2 = FakeMessage(chat_id=3001, username="malika01", text=text)
            msg2.bot = bot
            async_to_sync(feedback.feedback_text)(msg2, state, "uz")

        return bot

    def test_the_rating_and_comment_are_saved(self):
        self._submit(rating=5, text="Juda yaxshi mahsulot!")
        saved = UserFeedback.objects.get()
        self.assertEqual(saved.rating, 5)
        self.assertEqual(saved.text, "Juda yaxshi mahsulot!")
        self.assertEqual(saved.product_id, self.product.pk)
        self.assertEqual(saved.user_id, self.user.pk)

    def test_the_admin_group_gets_notified_with_the_rating_and_comment(self):
        bot = self._submit(rating=4, text="Yaxshi, lekin qadoq buzilgan edi.")

        self.assertEqual(len(bot.sent), 1)
        notification = bot.sent[0]
        self.assertEqual(notification["chat_id"], 555)
        self.assertIn("⭐️⭐️⭐️⭐️", notification["text"])
        self.assertIn("Vitamin C serum", notification["text"])
        self.assertIn("Malika", notification["text"])
        self.assertIn("Yaxshi, lekin qadoq buzilgan edi.", notification["text"])

    def test_skipping_the_written_comment_still_notifies_with_just_the_rating(self):
        bot = self._submit(rating=3, text="", skip_text=True)

        self.assertEqual(len(bot.sent), 1)
        self.assertIn("⭐️⭐️⭐️", bot.sent[0]["text"])
        saved = UserFeedback.objects.get()
        self.assertEqual(saved.text, "")

    def test_no_group_configured_does_not_break_saving(self):
        SupportSettings.objects.update_or_create(pk=1, defaults={"group_chat_id": None})
        bot = self._submit(rating=2, text="Yomon")

        self.assertEqual(UserFeedback.objects.count(), 1)
        self.assertEqual(bot.sent, [])
