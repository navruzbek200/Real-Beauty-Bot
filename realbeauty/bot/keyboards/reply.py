from __future__ import annotations

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

from bot import texts


def share_contact_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=texts.SHARE_CONTACT, request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Persistent main menu shown after registration."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=texts.MENU_TUTORIALS),
                KeyboardButton(text=texts.MENU_CATALOG),
            ],
            [
                KeyboardButton(text=texts.MENU_FEEDBACK),
                KeyboardButton(text=texts.MENU_SUPPORT),
            ],
            [
                KeyboardButton(text=texts.MENU_DISCOUNTS),
                KeyboardButton(text=texts.MENU_TIPS),
            ],
            [
                KeyboardButton(text=texts.MENU_PROFILE),
                KeyboardButton(text=texts.MENU_HELP),
            ],
        ],
        resize_keyboard=True,
    )


def remove_keyboard() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()
