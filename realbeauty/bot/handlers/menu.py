from __future__ import annotations

import logging

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot import texts
from bot.handlers.auth import send_tutorial_intros
from bot.keyboards import inline, reply
from bot.services import discount_service, user_service

logger = logging.getLogger(__name__)
router = Router(name="menu")


@router.message(Command("menu"))
async def open_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
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


@router.message(F.text == texts.MENU_FEEDBACK)
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
    product_names = ", ".join(up.product.name for up in products) or "—"
    face = user.get_face_condition_display() if user.face_condition else "—"
    await message.answer(
        texts.PROFILE_TEMPLATE.format(
            full_name=user.full_name,
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
