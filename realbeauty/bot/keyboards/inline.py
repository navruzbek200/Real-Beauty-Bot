from __future__ import annotations

from typing import Iterable

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.i18n import language_choices, t

# --- Callback data prefixes (no magic strings in handlers) ---
CB_LANGUAGE = "lang"                # lang:<code>
CB_FACE_CONDITION = "face"          # face:<value>
CB_KNOW_SKIN = "know_skin"          # know_skin:yes | know_skin:no
CB_QUIZ_START = "quiz_start"
CB_QUIZ_ANSWER = "quiz_ans"         # quiz_ans:<question_id>:<0..5>
CB_QUIZ_BACK = "quiz_back"
CB_QUIZ_RETAKE = "quiz_retake"
CB_SKIP_PHOTO = "skip_photo"
CB_TUTORIAL_STEP = "tutorial_step"  # tutorial_step:<product_id>:<step_id>
CB_SUBMIT_FEEDBACK = "submit_feedback"  # submit_feedback:<week>:<product_id>
CB_FEEDBACK_RATING = "feedback_rating"  # feedback_rating:<value>
CB_SKIP_FEEDBACK_TEXT = "skip_fb_text"  # rating saved, no written comment
CB_SEND_PROGRESS = "send_progress"  # send_progress:<product_id>
CB_SUPPORT_REPLY = "support_reply"  # attached to admin replies in the bot
CB_OPEN_DISCOUNTS = "open_discounts"
CB_LOYALTY_REWARDS = "loy_rewards"
CB_LOYALTY_HISTORY = "loy_history"
CB_LOYALTY_BACK = "loy_back"
CB_LOYALTY_REDEEM = "loy_redeem"    # loy_redeem:<reward_id>

SEP = ":"


def language_keyboard() -> InlineKeyboardMarkup:
    """The very first screen — deliberately not translated."""
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
            text="⭐️" * value, callback_data=f"{CB_FEEDBACK_RATING}{SEP}{value}"
        )
    builder.adjust(1)
    return builder.as_markup()


def skip_feedback_text_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("reg.skip", lang), callback_data=CB_SKIP_FEEDBACK_TEXT
                )
            ]
        ]
    )


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


def loyalty_keyboard(lang: str, *, has_rewards: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if has_rewards:
        builder.button(
            text=t("loyalty.rewards_btn", lang), callback_data=CB_LOYALTY_REWARDS
        )
    builder.button(
        text=t("loyalty.history_btn", lang), callback_data=CB_LOYALTY_HISTORY
    )
    builder.adjust(1)
    return builder.as_markup()


def rewards_keyboard(
    rewards: Iterable[tuple[int, str]], lang: str
) -> InlineKeyboardMarkup:
    """rewards: iterable of (reward_id, button_label)."""
    builder = InlineKeyboardBuilder()
    for reward_id, label in rewards:
        builder.button(
            text=label, callback_data=f"{CB_LOYALTY_REDEEM}{SEP}{reward_id}"
        )
    builder.adjust(1)
    builder.row(
        InlineKeyboardButton(text=t("quiz.back", lang), callback_data=CB_LOYALTY_BACK)
    )
    return builder.as_markup()


def back_to_loyalty_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("quiz.back", lang), callback_data=CB_LOYALTY_BACK
                )
            ]
        ]
    )
