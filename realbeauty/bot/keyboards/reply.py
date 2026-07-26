from __future__ import annotations

from django.conf import settings
from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    WebAppInfo,
)

from bot.i18n import DEFAULT_LANGUAGE, t

# The main menu, as (i18n key) pairs per row. Kept as data so the layout is
# read in one glance and every language renders the same shape.
_MAIN_MENU_ROWS: tuple[tuple[str, ...], ...] = (
    ("menu.ingredients", "menu.catalog"),
    ("menu.top", "menu.quiz_retake"),
    ("menu.support", "menu.discounts"),
    ("menu.bonus", "menu.profile"),
    ("menu.help",),
)


def share_contact_keyboard(lang: str = DEFAULT_LANGUAGE) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t("reg.share_contact", lang), request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def _webapp_url() -> str:
    """The Mini App URL, but only if it's a real https one Telegram will accept."""
    url = getattr(settings, "WEBAPP_URL", "") or ""
    return url if url.startswith("https://") else ""


def _menu_button(key: str, lang: str) -> KeyboardButton:
    """Build one menu button — «Mahsulotlar» opens the Mini App when available.

    Telegram only allows a web_app button on an https URL, so with no WEBAPP_URL
    the very same label stays an ordinary text button and the in-chat browser
    (menu_catalog) answers it instead. One label, two backends, no dead button.
    """
    if key == "menu.catalog":
        url = _webapp_url()
        if url:
            return KeyboardButton(text=t(key, lang), web_app=WebAppInfo(url=url))
    return KeyboardButton(text=t(key, lang))


def main_menu_keyboard(lang: str = DEFAULT_LANGUAGE) -> ReplyKeyboardMarkup:
    """Persistent main menu shown after registration, in the customer's language."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [_menu_button(key, lang) for key in row]
            for row in _MAIN_MENU_ROWS
        ],
        resize_keyboard=True,
    )


def remove_keyboard() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()
