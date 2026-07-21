from __future__ import annotations

import html
import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot import texts
from bot.keyboards import inline
from bot.services import support_service, user_service
from bot.states.registration import SupportState

logger = logging.getLogger(__name__)
router = Router(name="support")


@router.message(F.text == texts.MENU_SUPPORT)
async def open_support(message: Message, state: FSMContext) -> None:
    if message.from_user is None:
        return
    user = await user_service.get_user(message.from_user.id)
    if user is None or not user.full_name:
        await message.answer(texts.NOT_REGISTERED)
        return
    await state.set_state(SupportState.message)
    await message.answer(texts.SUPPORT_ASK, parse_mode="HTML")


@router.callback_query(F.data == inline.CB_SUPPORT_REPLY)
async def reply_from_admin_message(callback: CallbackQuery, state: FSMContext) -> None:
    """
    "✍️ Javob yozish" under an admin reply.

    Without it the customer reads the answer, types their follow-up, and the
    fallback tells them to use the menu — the natural next action has to work
    from the message itself.
    """
    await callback.answer()
    await state.set_state(SupportState.message)
    if callback.message:
        await callback.message.answer(texts.SUPPORT_ASK, parse_mode="HTML")


@router.message(SupportState.message, F.photo)
async def support_photo(message: Message, state: FSMContext) -> None:
    await _save(message, state, photo_file_id=message.photo[-1].file_id)


@router.message(SupportState.message, F.text)
async def support_text(message: Message, state: FSMContext) -> None:
    await _save(message, state)


@router.message(SupportState.message)
async def support_unsupported(message: Message) -> None:
    await message.answer(texts.SUPPORT_EMPTY)


async def _save(
    message: Message, state: FSMContext, photo_file_id: str = ""
) -> None:
    text = (message.text or message.caption or "").strip()
    if not text and not photo_file_id:
        await message.answer(texts.SUPPORT_EMPTY)
        return
    try:
        thread = await support_service.add_user_message(
            telegram_id=message.chat.id,
            text=text,
            photo_file_id=photo_file_id,
        )
    except Exception:  # noqa: BLE001
        logger.exception("Failed to save support message for %s", message.chat.id)
        await message.answer(texts.SUPPORT_SAVE_ERROR)
        return
    await _notify_staff(message, thread, text)
    # Deliberately keep the state: a question usually comes in several messages,
    # and forcing the button press between each one reads as the bot ignoring
    # them. Menu buttons and /menu still exit (their handlers clear state).
    await message.answer(texts.SUPPORT_SAVED)


async def _notify_staff(message: Message, thread, text: str) -> None:
    """
    Ping active sellers about the new message.

    The CRM badge only helps somebody already looking at the CRM; the shop
    lives in Telegram, so that is where "a customer is waiting" has to arrive.
    """
    try:
        staff_ids = await support_service.get_staff_telegram_ids()
        # Escaped: the bot's default parse mode is HTML, and a customer typing
        # "<" would otherwise make Telegram reject the whole notification.
        preview = html.escape(text[:100]) if text else "📷 rasm"
        who = html.escape(str(thread.user.full_name or thread.user.telegram_id))
        note = (
            f"🔔 Yangi murojaat\n"
            f"👤 {who}\n"
            f"💬 {preview}\n\n"
            f"Javob berish: CRM → Murojaatlar"
        )
        for staff_id in staff_ids:
            if staff_id == message.chat.id:
                continue  # staff member testing the bot on themselves
            try:
                await message.bot.send_message(chat_id=staff_id, text=note)
            except Exception:  # noqa: BLE001 — one blocked staff chat is not an error
                logger.info("Could not notify staff %s", staff_id)
    except Exception:  # noqa: BLE001 — notification must never break the save
        logger.exception("Staff notification failed")
