from __future__ import annotations

from typing import Iterable

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- Callback data prefixes (no magic strings in handlers) ---
CB_FACE_CONDITION = "face"          # face:<value>
CB_SKIP_PHOTO = "skip_photo"
CB_TUTORIAL_STEP = "tutorial_step"  # tutorial_step:<product_id>:<step_id>
CB_SUBMIT_FEEDBACK = "submit_feedback"  # submit_feedback:<week>:<product_id>
CB_FEEDBACK_RATING = "feedback_rating"  # feedback_rating:<value>
CB_SEND_PROGRESS = "send_progress"  # send_progress:<product_id>
CB_SUPPORT_REPLY = "support_reply"  # attached to admin replies in the bot

SEP = ":"


def face_condition_keyboard(choices: Iterable[tuple[str, str]]) -> InlineKeyboardMarkup:
    """choices: iterable of (value, label)."""
    builder = InlineKeyboardBuilder()
    for value, label in choices:
        builder.button(text=label, callback_data=f"{CB_FACE_CONDITION}{SEP}{value}")
    builder.adjust(2)
    return builder.as_markup()


def skip_photo_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⏭ Skip", callback_data=CB_SKIP_PHOTO)]
        ]
    )


def tutorial_steps_keyboard(
    product_id: int, steps: Iterable[tuple[int, str]]
) -> InlineKeyboardMarkup:
    """steps: iterable of (step_id, button_label)."""
    builder = InlineKeyboardBuilder()
    for step_id, label in steps:
        builder.button(
            text=label,
            callback_data=f"{CB_TUTORIAL_STEP}{SEP}{product_id}{SEP}{step_id}",
        )
    builder.adjust(1)
    return builder.as_markup()


def feedback_button_keyboard(
    label: str, week: int, product_id: int
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=label,
                    callback_data=f"{CB_SUBMIT_FEEDBACK}{SEP}{week}{SEP}{product_id}",
                )
            ]
        ]
    )


def feedback_products_keyboard(
    products: Iterable[tuple[int, str]], week: int = 1
) -> InlineKeyboardMarkup:
    """products: iterable of (product_id, name). Reuses submit_feedback callback."""
    builder = InlineKeyboardBuilder()
    for product_id, name in products:
        builder.button(
            text=name,
            callback_data=f"{CB_SUBMIT_FEEDBACK}{SEP}{week}{SEP}{product_id}",
        )
    builder.adjust(1)
    return builder.as_markup()


def rating_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for value in range(1, 6):
        builder.button(
            text=str(value), callback_data=f"{CB_FEEDBACK_RATING}{SEP}{value}"
        )
    builder.adjust(5)
    return builder.as_markup()


def progress_button_keyboard(label: str, product_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=label,
                    callback_data=f"{CB_SEND_PROGRESS}{SEP}{product_id}",
                )
            ]
        ]
    )
