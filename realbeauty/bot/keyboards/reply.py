from __future__ import annotations

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

from bot.i18n import DEFAULT_LANGUAGE, t

# The main menu, as (i18n key) pairs per row. Kept as data so the layout is
# read in one glance and every language renders the same shape.
_MAIN_MENU_ROWS: tuple[tuple[str, ...], ...] = (
    ("menu.ingredients", "menu.catalog"),
    ("menu.top", "menu.feedback"),
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


def main_menu_keyboard(lang: str = DEFAULT_LANGUAGE) -> ReplyKeyboardMarkup:
    """Persistent main menu shown after registration, in the customer's language."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(key, lang)) for key in row]
            for row in _MAIN_MENU_ROWS
        ],
        resize_keyboard=True,
    )


def remove_keyboard() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()
