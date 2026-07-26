from __future__ import annotations

from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    WebAppInfo,
)

from bot.i18n import DEFAULT_LANGUAGE, t

# The main menu, as (i18n key) pairs per row. Kept as data so the layout is
# read in one glance and every language renders the same shape.
# Six buttons, a clean 2×3 grid. Top products live inside the Mini App's TOP
# filter, retaking the quiz lives in Profil, and /help still works — so those
# older labels keep their handlers (MenuText matches them if an old keyboard is
# still on screen) without cluttering the menu.
_MAIN_MENU_ROWS: tuple[tuple[str, ...], ...] = (
    ("menu.catalog", "menu.discounts"),
    ("menu.ingredients", "menu.bonus"),
    ("menu.support", "menu.profile"),
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
    """The versioned Mini App URL, only if it's a real https one Telegram accepts."""
    from bot.utils.webapp import webapp_url

    return webapp_url()


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
