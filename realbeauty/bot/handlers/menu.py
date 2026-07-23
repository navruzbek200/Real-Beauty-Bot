from __future__ import annotations

import html
import logging

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, Message

from bot.filters.menu import MenuText
from bot.handlers.auth import send_tutorial_intros
from bot.i18n import normalize, t
from bot.keyboards import inline, reply
from bot.services import (
    discount_service,
    loyalty_service,
    product_service,
    user_service,
)
from core.i18n import pick

logger = logging.getLogger(__name__)
router = Router(name="menu")
# Customer menu only — a group admin's /menu or button taps must not fire this.
router.message.filter(F.chat.type == "private")

# Telegram's caption limit; a longer caption is rejected outright rather than
# truncated, taking the whole product card with it.
CAPTION_LIMIT = 1024
CATALOG_PAGE = 10

_MONTHS = {
    "uz": (
        "Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun",
        "Iyul", "Avgust", "Sentabr", "Oktabr", "Noyabr", "Dekabr",
    ),
    "ru": (
        "январь", "февраль", "март", "апрель", "май", "июнь",
        "июль", "август", "сентябрь", "октябрь", "ноябрь", "декабрь",
    ),
    "en": (
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    ),
}


def month_name(lang: str) -> str:
    from django.utils import timezone

    return _MONTHS[normalize(lang)][timezone.localdate().month - 1]


@router.message(Command("menu"))
async def open_menu(message: Message, state: FSMContext, lang: str) -> None:
    await state.clear()
    if message.from_user is not None:
        user = await user_service.get_user(message.from_user.id)
        # Showing the menu to somebody unregistered just leads every button to
        # "register first" — send them to /start once, up front.
        if user is None or not user.full_name:
            await message.answer(t("user.not_registered", lang))
            return
    await message.answer(
        t("menu.opened", lang), reply_markup=reply.main_menu_keyboard(lang)
    )


@router.message(MenuText("menu.ingredients", "menu.legacy_tutorials"))
async def menu_ingredients(
    message: Message, bot: Bot, state: FSMContext, lang: str
) -> None:
    """The ingredient lessons — one card per product the customer owns."""
    await state.clear()
    if message.from_user is None:
        return
    products = await user_service.get_user_products(message.from_user.id)
    if not products:
        await message.answer(t("product.none", lang))
        return
    await send_tutorial_intros(bot, message.from_user.id, lang)


@router.message(MenuText("menu.feedback", "menu.legacy_feedback"))
async def menu_feedback(message: Message, state: FSMContext, lang: str) -> None:
    await state.clear()
    if message.from_user is None:
        return
    products = await user_service.get_user_products(message.from_user.id)
    if not products:
        await message.answer(t("product.none", lang))
        return
    keyboard = inline.feedback_products_keyboard(
        [(up.product_id, pick(up.product, "name", lang)) for up in products], week=1
    )
    await message.answer(t("feedback.pick_product", lang), reply_markup=keyboard)


@router.message(MenuText("menu.catalog"))
async def menu_catalog(message: Message, state: FSMContext, lang: str) -> None:
    """Every active product — the shop window, not just what this user owns."""
    await state.clear()
    products = await product_service.get_active_products()
    if not products:
        await message.answer(t("catalog.empty", lang))
        return
    await message.answer(t("catalog.header", lang), parse_mode="HTML")
    for product in products[:CATALOG_PAGE]:
        await _send_product_card(message, product, lang)
    await message.answer(t("catalog.footer", lang))


@router.message(MenuText("menu.top", "menu.legacy_tips"))
async def menu_top_products(message: Message, state: FSMContext, lang: str) -> None:
    """This month's curated picks, in the order the shop arranged them."""
    await state.clear()
    products = await product_service.get_top_products()
    if not products:
        await message.answer(t("top.empty", lang))
        return
    await message.answer(
        t("top.header", lang, month=month_name(lang)), parse_mode="HTML"
    )
    for rank, product in enumerate(products[:CATALOG_PAGE], start=1):
        await _send_product_card(message, product, lang, rank=rank)
    await message.answer(t("top.footer", lang))


async def _send_product_card(
    message: Message, product, lang: str, rank: int | None = None
) -> None:
    title = html.escape(pick(product, "name", lang))
    if rank is not None:
        title = f"{t('top.rank', lang, rank=rank)} {title}"
    caption = f"<b>{title}</b>"

    note = pick(product, "top_note", lang) if rank is not None else ""
    if note:
        caption += f"\n🏷 <i>{html.escape(note)}</i>"
    description = pick(product, "description", lang)
    if description:
        caption += f"\n\n{html.escape(description)}"
    caption = caption[:CAPTION_LIMIT]

    try:
        if product.photo and product.photo.name:
            await message.answer_photo(
                FSInputFile(product.photo.path), caption=caption, parse_mode="HTML"
            )
        else:
            await message.answer(caption, parse_mode="HTML")
    except (TelegramAPIError, OSError, ValueError):
        # A missing file on disk must not take the rest of the list with it.
        logger.exception("Failed to send product card %s", product.pk)


@router.message(MenuText("menu.discounts"))
async def menu_discounts(message: Message, state: FSMContext, lang: str) -> None:
    await state.clear()
    await _show_discounts(message, lang)


@router.callback_query(F.data == inline.CB_OPEN_DISCOUNTS)
async def open_discounts_from_button(callback: CallbackQuery, lang: str) -> None:
    """The «see the discounts» button an automatic message can carry."""
    await callback.answer()
    await _show_discounts(callback.message, lang)


async def _show_discounts(message: Message, lang: str) -> None:
    discounts = await discount_service.get_active_discounts()
    if not discounts:
        await message.answer(t("discount.none", lang))
        return
    lines = [t("discount.header", lang)]
    for d in discounts:
        line = f"\n• <b>{html.escape(d.title)}</b> — {d.percent}%"
        if d.description:
            line += f"\n  {html.escape(d.description)}"
        if d.promo_code:
            line += f"\n  🔑 <code>{html.escape(d.promo_code)}</code>"
        if d.valid_until:
            line += "\n  " + t(
                "discount.until", lang, date=d.valid_until.strftime("%d.%m.%Y")
            )
        lines.append(line)
    await message.answer("\n".join(lines), parse_mode="HTML")


@router.message(MenuText("menu.profile"))
async def menu_profile(message: Message, state: FSMContext, lang: str) -> None:
    await state.clear()
    if message.from_user is None:
        return
    user = await user_service.get_user(message.from_user.id)
    if user is None or not user.full_name:
        await message.answer(t("user.not_registered", lang))
        return
    products = await user_service.get_user_products(message.from_user.id)
    product_names = (
        html.escape(", ".join(pick(up.product, "name", lang) for up in products)) or "—"
    )
    face = t(f"skin.type.{user.face_condition}", lang) if user.face_condition else "—"
    points, tier_key = await loyalty_service.get_summary(message.from_user.id)
    await message.answer(
        t(
            "profile.template",
            lang,
            full_name=html.escape(user.full_name),
            phone=user.phone_number or "—",
            birth_date=user.birth_date.strftime("%d.%m.%Y") if user.birth_date else "—",
            face=face,
            products=product_names,
            points=points,
            tier=t(tier_key, lang),
        ),
        parse_mode="HTML",
        reply_markup=inline.profile_keyboard(lang),
    )


@router.message(MenuText("menu.help"))
@router.message(Command("help"))
async def menu_help(message: Message, state: FSMContext, lang: str) -> None:
    await state.clear()
    await message.answer(t("help.text", lang), parse_mode="HTML")


# ---------------------------------------------------------------------------
# Changing language after registration
# ---------------------------------------------------------------------------
@router.message(Command("language"))
@router.callback_query(F.data == inline.CB_LANGUAGE)
async def open_language_picker(event: Message | CallbackQuery, lang: str) -> None:
    message = event if isinstance(event, Message) else event.message
    if isinstance(event, CallbackQuery):
        await event.answer()
    await message.answer(
        t("lang.choose", lang),
        parse_mode="HTML",
        reply_markup=inline.language_keyboard(),
    )


@router.callback_query(F.data.startswith(f"{inline.CB_LANGUAGE}{inline.SEP}"))
async def change_language(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Language switch outside registration.

    Registration has its own handler filtered on the reg state, and routers are
    included in order, so a mid-signup pick never reaches this one.
    """
    await callback.answer()
    chosen = normalize((callback.data or "").split(inline.SEP, 1)[1])
    await user_service.set_language(callback.from_user.id, chosen)
    await state.clear()
    await callback.message.answer(
        t("lang.changed", chosen), reply_markup=reply.main_menu_keyboard(chosen)
    )
