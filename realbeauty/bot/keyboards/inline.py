from __future__ import annotations

from typing import Iterable

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.i18n import language_choices, t

# --- Callback data prefixes (no magic strings in handlers) ---
# Two distinct prefixes for what looks like "the same" language picker:
# CB_LANGUAGE_SETUP only ever matches inside the registration FSM states, so a
# stale tap on that first-screen message (Telegram keeps old messages tappable
# forever) cannot do anything once registration has moved on. CB_LANGUAGE is
# the profile "change language" button, which is state-free by design and
# would otherwise catch that stale tap, clear whatever state the customer was
# in, and drop a half-registered person straight onto the main menu.
CB_LANGUAGE_SETUP = "lang_setup"    # lang_setup:<code>
CB_LANGUAGE = "lang"                # lang:<code>
CB_FACE_CONDITION = "face"          # face:<value>
CB_KNOW_SKIN = "know_skin"          # know_skin:yes | know_skin:no
CB_QUIZ_START = "quiz_start"
CB_QUIZ_ANSWER = "quiz_ans"         # quiz_ans:<question_id>:<0..5>
CB_QUIZ_BACK = "quiz_back"
CB_QUIZ_RETAKE = "quiz_retake"
CB_SKIP_PHOTO = "skip_photo"
CB_TUTORIAL_STEP = "tutorial_step"  # tutorial_step:<product_id>:<step_id>
CB_SUPPORT_REPLY = "support_reply"  # attached to admin replies in the bot
CB_OPEN_DISCOUNTS = "open_discounts"

SEP = ":"


def language_setup_keyboard() -> InlineKeyboardMarkup:
    """The very first screen, during registration — deliberately not translated."""
    builder = InlineKeyboardBuilder()
    for code, label in language_choices():
        builder.button(text=label, callback_data=f"{CB_LANGUAGE_SETUP}{SEP}{code}")
    builder.adjust(1)
    return builder.as_markup()


def language_keyboard() -> InlineKeyboardMarkup:
    """The profile "change language" screen — outside registration."""
    builder = InlineKeyboardBuilder()
    for code, label in language_choices():
        builder.button(text=label, callback_data=f"{CB_LANGUAGE}{SEP}{code}")
    builder.adjust(1)
    return builder.as_markup()


def know_skin_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("skin.know_yes", lang),
                    callback_data=f"{CB_KNOW_SKIN}{SEP}yes",
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("skin.know_no", lang),
                    callback_data=f"{CB_KNOW_SKIN}{SEP}no",
                )
            ],
        ]
    )


def face_condition_keyboard(choices: Iterable[tuple[str, str]]) -> InlineKeyboardMarkup:
    """choices: iterable of (value, label)."""
    builder = InlineKeyboardBuilder()
    for value, label in choices:
        builder.button(text=label, callback_data=f"{CB_FACE_CONDITION}{SEP}{value}")
    builder.adjust(2)
    return builder.as_markup()


def quiz_start_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("quiz.start", lang), callback_data=CB_QUIZ_START
                )
            ]
        ]
    )


def quiz_answer_keyboard(
    question_id: str,
    option_labels: list[str],
    *,
    per_row: int,
    show_back: bool,
    lang: str,
) -> InlineKeyboardMarkup:
    """
    The 0–5 scale for one question.

    `per_row` is passed in rather than inferred from the labels: question 1
    carries a sentence per option and needs one per row, the rest are keycap
    digits that fit three across on a narrow phone.
    """
    builder = InlineKeyboardBuilder()
    for value, label in enumerate(option_labels):
        builder.button(
            text=label,
            callback_data=f"{CB_QUIZ_ANSWER}{SEP}{question_id}{SEP}{value}",
        )
    builder.adjust(per_row)
    if show_back:
        builder.row(
            InlineKeyboardButton(text=t("quiz.back", lang), callback_data=CB_QUIZ_BACK)
        )
    return builder.as_markup()


def quiz_retake_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("quiz.retake", lang), callback_data=CB_QUIZ_RETAKE
                )
            ]
        ]
    )


def profile_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("quiz.retake", lang), callback_data=CB_QUIZ_RETAKE
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("lang.button", lang), callback_data=CB_LANGUAGE
                )
            ],
        ]
    )


def support_reply_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    """Attached to a support reply so the customer's next message re-enters the flow."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("support.reply_btn", lang),
                    callback_data=CB_SUPPORT_REPLY,
                )
            ]
        ]
    )


def skip_photo_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("reg.skip", lang), callback_data=CB_SKIP_PHOTO
                )
            ]
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
