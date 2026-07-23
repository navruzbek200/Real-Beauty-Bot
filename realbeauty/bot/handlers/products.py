from __future__ import annotations

import html
import logging

from aiogram import F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.i18n import t
from bot.keyboards import inline
from bot.services import product_service, template_service, user_service
from bot.utils.video import send_protected_video
from core.i18n import pick

logger = logging.getLogger(__name__)
router = Router(name="products")
router.message.filter(F.chat.type == "private")


@router.message(Command("products"))
async def list_products(message: Message, lang: str) -> None:
    """Show tutorial intros for every product the user owns."""
    if message.from_user is None:
        return
    user_products = await user_service.get_user_products(message.from_user.id)
    if not user_products:
        await message.answer(t("product.none", lang))
        return

    for up in user_products:
        product = up.product
        text, parse_mode = await template_service.render_template(
            "product_intro", {"product": product}, lang
        )
        steps = await product_service.get_tutorial_steps(product.pk)
        keyboard = inline.tutorial_steps_keyboard(
            product.pk, [(s.pk, pick(s, "button_label", lang)) for s in steps]
        )
        body = text or t(
            "tutorial.intro_fallback",
            lang,
            product=html.escape(pick(product, "name", lang)),
        )
        try:
            await message.answer(body, parse_mode=parse_mode, reply_markup=keyboard)
        except TelegramAPIError:
            logger.exception("Failed to send product intro to %s", message.from_user.id)


@router.callback_query(F.data.startswith(f"{inline.CB_TUTORIAL_STEP}{inline.SEP}"))
async def tutorial_step(callback: CallbackQuery, lang: str) -> None:
    await callback.answer()  # remove loading spinner
    try:
        _, _product_id, step_id = (callback.data or "").split(inline.SEP)
    except ValueError:
        return

    step = await product_service.get_tutorial_step(int(step_id))
    if step is None:
        await callback.message.answer(t("tutorial.step_not_found", lang))
        return

    await send_protected_video(callback.bot, callback.message.chat.id, step, lang)
