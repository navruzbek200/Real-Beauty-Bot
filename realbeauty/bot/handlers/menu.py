from __future__ import annotations

import html
import logging

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, Message

from bot import texts
from bot.handlers.auth import send_tutorial_intros
from bot.keyboards import inline, reply
from bot.services import discount_service, product_service, user_service

logger = logging.getLogger(__name__)
router = Router(name="menu")


@router.message(Command("menu"))
async def open_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    if message.from_user is not None:
        user = await user_service.get_user(message.from_user.id)
        # Showing the menu to somebody unregistered just leads every button to
        # "avval ro'yxatdan o'ting" — send them to /start once, up front.
        if user is None or not user.full_name:
            await message.answer(texts.NOT_REGISTERED)
            return
    await message.answer(texts.MENU_OPENED, reply_markup=reply.main_menu_keyboard())


@router.message(F.text == texts.MENU_TUTORIALS)
async def menu_tutorials(message: Message, bot: Bot, state: FSMContext) -> None:
    await state.clear()
    if message.from_user is None:
        return
    products = await user_service.get_user_products(message.from_user.id)
    if not products:
        await message.answer(texts.NO_PRODUCTS)
        return
    await send_tutorial_intros(bot, message.from_user.id)


@router.message(F.text.in_({texts.MENU_FEEDBACK, texts.MENU_FEEDBACK_LEGACY}))
async def menu_feedback(message: Message, state: FSMContext) -> None:
    await state.clear()
    if message.from_user is None:
        return
    products = await user_service.get_user_products(message.from_user.id)
    if not products:
        await message.answer(texts.NO_PRODUCTS)
        return
    keyboard = inline.feedback_products_keyboard(
        [(up.product_id, up.product.name) for up in products], week=1
    )
    await message.answer(texts.FEEDBACK_PICK_PRODUCT, reply_markup=keyboard)


@router.message(F.text == texts.MENU_CATALOG)
async def menu_catalog(message: Message, state: FSMContext) -> None:
    """Every active product — the shop window, not just what this user owns."""
    await state.clear()
    products = await product_service.get_active_products()
    if not products:
        await message.answer(texts.CATALOG_EMPTY)
        return
    await message.answer(texts.CATALOG_HEADER, parse_mode="HTML")
    for product in products[:10]:
        caption = f"<b>{html.escape(product.name)}</b>"
        if product.description:
            caption += f"\n\n{html.escape(product.description)}"
        caption = caption[:1024]  # Telegram caption limit
        try:
            if product.photo and product.photo.name:
                await message.answer_photo(
                    FSInputFile(product.photo.path),
                    caption=caption,
                    parse_mode="HTML",
                )
            else:
                await message.answer(caption, parse_mode="HTML")
        except TelegramAPIError:
            logger.exception("Failed to send catalog item %s", product.pk)
    await message.answer(texts.CATALOG_FOOTER)


@router.message(F.text == texts.MENU_TIPS)
async def menu_tips(message: Message, state: FSMContext) -> None:
    """Skin-care tips matched to the customer's stored skin type."""
    await state.clear()
    if message.from_user is None:
        return
    user = await user_service.get_user(message.from_user.id)
    if user is None or not user.full_name:
        await message.answer(texts.NOT_REGISTERED)
        return
    body = texts.TIPS_BY_SKIN.get(user.face_condition, texts.TIPS_GENERIC)
    await message.answer(body + texts.TIPS_FOOTER, parse_mode="HTML")


@router.message(F.text == texts.MENU_DISCOUNTS)
async def menu_discounts(message: Message, state: FSMContext) -> None:
    await state.clear()
    discounts = await discount_service.get_active_discounts()
    if not discounts:
        await message.answer(texts.NO_DISCOUNTS)
        return
    lines = [texts.DISCOUNTS_HEADER]
    for d in discounts:
        line = f"\n• <b>{d.title}</b> — {d.percent}%"
        if d.description:
            line += f"\n  {d.description}"
        if d.promo_code:
            line += f"\n  🔑 <code>{d.promo_code}</code>"
        if d.valid_until:
            line += f"\n  ⏳ {d.valid_until.strftime('%d.%m.%Y')} gacha"
        lines.append(line)
    await message.answer("\n".join(lines), parse_mode="HTML")


@router.message(F.text == texts.MENU_PROFILE)
async def menu_profile(message: Message, state: FSMContext) -> None:
    await state.clear()
    if message.from_user is None:
        return
    user = await user_service.get_user(message.from_user.id)
    if user is None or not user.full_name:
        await message.answer(texts.NOT_REGISTERED)
        return
    products = await user_service.get_user_products(message.from_user.id)
    product_names = (
        html.escape(", ".join(up.product.name for up in products)) or "—"
    )
    face = user.get_face_condition_display() if user.face_condition else "—"
    await message.answer(
        texts.PROFILE_TEMPLATE.format(
            full_name=html.escape(user.full_name),
            phone=user.phone_number or "—",
            birth_date=user.birth_date.strftime("%d.%m.%Y") if user.birth_date else "—",
            face=face,
            products=product_names,
        ),
        parse_mode="HTML",
    )


@router.message(F.text == texts.MENU_HELP)
@router.message(Command("help"))
async def menu_help(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(texts.HELP_TEXT, parse_mode="HTML")
