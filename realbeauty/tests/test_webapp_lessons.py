"""
The Mini App's «Darslar» tab and its deep links back into the chat.

Three seams matter here:

* `verified_telegram_id` — the HMAC check that decides whether the lessons
  endpoint may personalize. A forged or tampered initData must read as nobody.
* The lessons endpoint itself — public fallback vs. the customer's own shelf.
* The `/start ask_… | lesson_… | support` deep links — the path the Mini App
  uses when it was NOT opened from the reply keyboard (where sendData is dead).
"""

from __future__ import annotations

import hashlib
import hmac
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from urllib.parse import urlencode

from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.memory import MemoryStorage
from asgiref.sync import async_to_sync
from django.test import TestCase, override_settings

from apps.api.views.webapp import verified_telegram_id
from apps.products.models import Product, ProductTutorialStep
from apps.users.models import TelegramUser, UserProduct
from bot.handlers import auth
from bot.states.registration import SupportState

TOKEN = "12345:TESTTOKEN"


def make_init_data(user_id: int, token: str = TOKEN) -> str:
    """A minimal initData string signed exactly the way Telegram signs it."""
    pairs = {
        "auth_date": "1700000000",
        "user": json.dumps({"id": user_id, "first_name": "T"}),
    }
    check_string = "\n".join(f"{k}={v}" for k, v in sorted(pairs.items()))
    secret = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
    pairs["hash"] = hmac.new(secret, check_string.encode(), hashlib.sha256).hexdigest()
    return urlencode(pairs)


@override_settings(BOT_TOKEN=TOKEN)
class VerifiedTelegramIdTests(TestCase):
    def test_valid_signature_yields_the_user_id(self):
        self.assertEqual(verified_telegram_id(make_init_data(777)), 777)

    def test_tampered_payload_is_rejected(self):
        data = make_init_data(777).replace("1700000000", "1700000001")
        self.assertIsNone(verified_telegram_id(data))

    def test_signature_from_another_bot_is_rejected(self):
        self.assertIsNone(verified_telegram_id(make_init_data(777, token="999:OTHER")))

    def test_garbage_and_empty_are_rejected(self):
        self.assertIsNone(verified_telegram_id(""))
        self.assertIsNone(verified_telegram_id("hash=zz&user=nope"))

    @override_settings(BOT_TOKEN="")
    def test_no_token_configured_never_personalizes(self):
        self.assertIsNone(verified_telegram_id(make_init_data(777)))


@override_settings(BOT_TOKEN=TOKEN)
class WebAppLessonsViewTests(TestCase):
    def setUp(self):
        self.with_lesson = Product.objects.create(name="Serum", is_top=True)
        ProductTutorialStep.objects.create(
            product=self.with_lesson, order=1, button_label="1-qadam"
        )
        Product.objects.create(name="Lessonless")  # must not appear in fallback

    def test_fallback_lists_only_products_that_have_lessons(self):
        response = self.client.get("/api/v1/webapp/lessons/")
        self.assertEqual(response.status_code, 200)
        names = [p["name"] for p in response.json()["products"]]
        self.assertEqual(names, ["Serum"])
        self.assertFalse(response.json()["personalized"])
        steps = response.json()["products"][0]["steps"]
        self.assertEqual(steps[0]["label"], "1-qadam")
        self.assertFalse(steps[0]["has_video"])

    def test_verified_customer_sees_their_own_shelf_first(self):
        owned = Product.objects.create(name="Sotib olingan")
        user = TelegramUser.objects.create(
            telegram_id=555,
            full_name="Mijoz",
            registration_status=TelegramUser.RegistrationStatus.COMPLETED,
        )
        UserProduct.objects.create(user=user, product=owned)

        response = self.client.get(
            "/api/v1/webapp/lessons/", {"init_data": make_init_data(555)}
        )
        names = [p["name"] for p in response.json()["products"]]
        self.assertEqual(names, ["Sotib olingan"])
        self.assertTrue(response.json()["personalized"])

    def test_forged_init_data_falls_back_to_the_public_list(self):
        owned = Product.objects.create(name="Sotib olingan")
        user = TelegramUser.objects.create(
            telegram_id=556,
            full_name="Mijoz",
            registration_status=TelegramUser.RegistrationStatus.COMPLETED,
        )
        UserProduct.objects.create(user=user, product=owned)

        forged = make_init_data(556, token="999:OTHER")
        response = self.client.get("/api/v1/webapp/lessons/", {"init_data": forged})
        names = [p["name"] for p in response.json()["products"]]
        self.assertEqual(names, ["Serum"])
        self.assertFalse(response.json()["personalized"])


# ---------------------------------------------------------------------------
# Deep links
# ---------------------------------------------------------------------------
BOT_ID = 1


class FakeMessage(SimpleNamespace):
    def __init__(self, chat_id: int):
        super().__init__(
            chat=SimpleNamespace(id=chat_id, username=None),
            from_user=SimpleNamespace(id=chat_id, username=None, language_code="uz"),
            text="/start",
        )
        self.answer = AsyncMock(side_effect=self._record)
        self.sent: list[dict] = []

    async def _record(self, text="", **kwargs):
        self.sent.append({"text": text, **kwargs})
        return self


def fsm_for(chat_id: int) -> FSMContext:
    return FSMContext(
        storage=MemoryStorage(),
        key=StorageKey(bot_id=BOT_ID, chat_id=chat_id, user_id=chat_id),
    )


class DeepLinkActionTests(TestCase):
    def setUp(self):
        self.user = TelegramUser.objects.create(
            telegram_id=6001,
            full_name="Mijoz",
            language="uz",
            registration_status=TelegramUser.RegistrationStatus.COMPLETED,
        )
        self.product = Product.objects.create(name="Krem")

    def _run(self, payload: str, chat_id: int = 6001):
        msg = FakeMessage(chat_id)
        state = fsm_for(chat_id)
        handled = async_to_sync(auth._handled_as_action)(msg, state, None, payload)
        return handled, msg, state

    def test_ask_payload_opens_support_with_the_product_named(self):
        handled, msg, state = self._run(f"ask_{self.product.pk}")
        self.assertTrue(handled)
        self.assertEqual(async_to_sync(state.get_state)(), SupportState.message)
        self.assertIn("Krem", msg.sent[0]["text"])

    def test_ask_payload_for_a_dead_product_still_opens_support(self):
        handled, msg, state = self._run("ask_999999")
        self.assertTrue(handled)
        self.assertEqual(async_to_sync(state.get_state)(), SupportState.message)
        self.assertEqual(len(msg.sent), 1)

    def test_support_payload_opens_the_plain_support_flow(self):
        handled, msg, state = self._run("support")
        self.assertTrue(handled)
        self.assertEqual(async_to_sync(state.get_state)(), SupportState.message)

    def test_lesson_payload_sends_the_protected_video(self):
        step = ProductTutorialStep.objects.create(
            product=self.product, order=1, button_label="1-qadam"
        )
        with patch("bot.utils.video.send_protected_video", new=AsyncMock()) as sent:
            handled, msg, state = self._run(f"lesson_{step.pk}")
        self.assertTrue(handled)
        sent.assert_awaited_once()
        self.assertEqual(sent.await_args.args[2].pk, step.pk)

    def test_unregistered_visitor_falls_through_to_registration(self):
        handled, msg, state = self._run(f"ask_{self.product.pk}", chat_id=6999)
        self.assertFalse(handled)
        self.assertEqual(msg.sent, [])

    def test_referral_payload_is_not_treated_as_an_action(self):
        handled, msg, state = self._run("ref_12345")
        self.assertFalse(handled)
