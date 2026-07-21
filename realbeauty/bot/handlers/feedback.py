from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot import texts
from bot.keyboards import inline
from bot.services import analytics_service, template_service
from bot.states.registration import FeedbackState

logger = logging.getLogger(__name__)
router = Router(name="feedback")

# Rating comes first (one tap, nobody drops off), the written comment second
# and skippable — the reverse order lost customers who didn't feel like
# composing a text just to leave 5 stars.


@router.callback_query(F.data.startswith(f"{inline.CB_SUBMIT_FEEDBACK}{inline.SEP}"))
async def start_feedback(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    try:
        _, week, product_id = (callback.data or "").split(inline.SEP)
    except ValueError:
        return

    await state.set_state(FeedbackState.rating)
    await state.update_data(week=int(week), product_id=int(product_id))
    await callback.message.answer(
        texts.FEEDBACK_ASK_RATING, reply_markup=inline.rating_keyboard()
    )


@router.callback_query(
    FeedbackState.rating, F.data.startswith(f"{inline.CB_FEEDBACK_RATING}{inline.SEP}")
)
async def feedback_rating(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    rating = int((callback.data or "").split(inline.SEP, 1)[1])
    await state.update_data(rating=rating)
    await state.set_state(FeedbackState.text)
    await callback.message.answer(
        texts.FEEDBACK_ASK_TEXT, reply_markup=inline.skip_feedback_text_keyboard()
    )


@router.message(FeedbackState.text, F.text)
async def feedback_text(message: Message, state: FSMContext) -> None:
    await _finish(message, state, text=(message.text or "").strip())


@router.callback_query(FeedbackState.text, F.data == inline.CB_SKIP_FEEDBACK_TEXT)
async def feedback_skip_text(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await _finish(callback.message, state, text="")


async def _finish(message: Message, state: FSMContext, text: str) -> None:
    data = await state.get_data()
    await state.clear()

    try:
        await analytics_service.save_feedback(
            telegram_id=message.chat.id,
            product_id=data.get("product_id"),
            week=data.get("week", 1),
            text=text,
            rating=data.get("rating"),
        )
        if data.get("product_id"):
            # Mark the week this feedback answered — hardcoding 1 here left
            # week-2 check-ins "unsent", so the scheduler re-asked forever.
            await analytics_service.mark_week_sent(
                message.chat.id,
                data["product_id"],
                week=data.get("week", 1),
            )
    except Exception:  # noqa: BLE001
        logger.exception("Failed to save feedback for %s", message.chat.id)
        await message.answer(texts.FEEDBACK_SAVE_ERROR)
        return

    thanks, parse_mode = await template_service.render_template("feedback_thanks", {})
    try:
        await message.answer(
            thanks or texts.FEEDBACK_THANKS_FALLBACK, parse_mode=parse_mode
        )
    except TelegramAPIError:
        logger.exception("Failed to send thanks to %s", message.chat.id)
