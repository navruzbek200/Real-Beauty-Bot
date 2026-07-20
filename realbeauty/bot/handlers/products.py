from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot import texts
from bot.keyboards import inline
from bot.services import product_service, template_service, user_service
from bot.utils.video import send_protected_video

logger = logging.getLogger(__name__)
router = Router(name="products")


@router.message(Command("products"))
async def list_products(message: Message) -> None:
    """Show tutorial intros for every product the user owns."""
    if message.from_user is None:
        return
    user_products = await user_service.get_user_products(message.from_user.id)
    if not user_products:
        await message.answer(texts.NO_PRODUCTS)
        return

    for up in user_products:
        product = up.product
        text, parse_mode = await template_service.render_template(
            "product_intro", {"product": product}
        )
        steps = await product_service.get_tutorial_steps(product.pk)
        keyboard = inline.tutorial_steps_keyboard(
            product.pk, [(s.pk, s.button_label) for s in steps]
        )
        body = text or texts.TUTORIAL_INTRO_FALLBACK.format(product=product.name)
        try:
            await message.answer(body, parse_mode=parse_mode, reply_markup=keyboard)
        except TelegramAPIError:
            logger.exception("Failed to send product intro to %s", message.from_user.id)


@router.callback_query(F.data.startswith(f"{inline.CB_TUTORIAL_STEP}{inline.SEP}"))
async def tutorial_step(callback: CallbackQuery) -> None:
    await callback.answer()  # remove loading spinner
    try:
        _, _product_id, step_id = (callback.data or "").split(inline.SEP)
    except ValueError:
        return

    step = await product_service.get_tutorial_step(int(step_id))
    if step is None:
        await callback.message.answer(texts.STEP_NOT_FOUND)
        return

    await send_protected_video(callback.bot, callback.message.chat.id, step)
