from __future__ import annotations

import html
import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot import texts
from bot.services import settings_service, template_service, user_service

logger = logging.getLogger(__name__)
router = Router(name="birthday")


@router.message(Command("birthday"))
async def birthday_preview(message: Message) -> None:
    """
    Let a registered user preview their birthday-sale message on demand.
    The scheduled delivery is handled by the Celery beat task.
    """
    if message.from_user is None:
        return
    user = await user_service.get_user(message.from_user.id)
    if user is None or not user.full_name:
        await message.answer(texts.NOT_REGISTERED)
        return

    settings = await settings_service.get_settings()
    context = {"user": user, "discount": settings.birthday_discount_percent}
    text, parse_mode = await template_service.render_template("birthday_sale", context)
    body = text or (
        f"🎉 Tug'ilgan kuningiz muborak, {html.escape(user.full_name)}! "
        f"Bugun siz uchun {settings.birthday_discount_percent}% chegirma."
    )
    await message.answer(body, parse_mode=parse_mode)
