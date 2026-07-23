from __future__ import annotations

import logging

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.i18n import t
from bot.keyboards import inline
from bot.services import analytics_service
from bot.states.registration import ProgressState

logger = logging.getLogger(__name__)
router = Router(name="progress")
router.message.filter(F.chat.type == "private")


@router.callback_query(F.data.startswith(f"{inline.CB_SEND_PROGRESS}{inline.SEP}"))
async def start_progress(
    callback: CallbackQuery, state: FSMContext, lang: str
) -> None:
    await callback.answer()
    product_id = int((callback.data or "").split(inline.SEP, 1)[1])
    await state.set_state(ProgressState.before_photo)
    await state.update_data(product_id=product_id)
    await callback.message.answer(t("progress.ask_before", lang))


@router.message(ProgressState.before_photo, F.photo)
async def before_photo(
    message: Message, state: FSMContext, bot: Bot, lang: str
) -> None:
    data = await state.get_data()
    ok = await _save_photo(message, bot, data.get("product_id"), "before")
    if not ok:
        await message.answer(t("progress.save_error", lang))
        return
    await state.set_state(ProgressState.after_photo)
    await message.answer(t("progress.ask_after", lang))


@router.message(ProgressState.after_photo, F.photo)
async def after_photo(
    message: Message, state: FSMContext, bot: Bot, lang: str
) -> None:
    data = await state.get_data()
    ok = await _save_photo(message, bot, data.get("product_id"), "after")
    await state.clear()
    if not ok:
        await message.answer(t("progress.save_error", lang))
        return
    await message.answer(t("progress.done", lang))


@router.message(ProgressState.before_photo)
@router.message(ProgressState.after_photo)
async def not_a_photo(message: Message, lang: str) -> None:
    await message.answer(t("progress.not_photo", lang))


async def _save_photo(
    message: Message, bot: Bot, product_id: int | None, label: str
) -> bool:
    try:
        photo = message.photo[-1]
        file = await bot.get_file(photo.file_id)
        buffer = await bot.download_file(file.file_path)
        photo_bytes = buffer.read() if buffer is not None else None
        if not photo_bytes:
            return False
        await analytics_service.save_progress_photo(
            telegram_id=message.chat.id,
            product_id=product_id,
            file_bytes=photo_bytes,
            file_id=photo.file_id,
            filename=f"{label}_{message.chat.id}.jpg",
            label=label,
        )
        if product_id is not None and label == "after":
            await analytics_service.mark_week_sent(message.chat.id, product_id, week=2)
        return True
    except Exception:  # noqa: BLE001
        logger.exception("Failed to save %s photo for %s", label, message.chat.id)
        return False
