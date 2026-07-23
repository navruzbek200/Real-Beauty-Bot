from __future__ import annotations

import html
import logging
from datetime import date, datetime

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from apps.users.models import TelegramUser
from bot.i18n import normalize, t
from bot.keyboards import inline, reply
from bot.services import product_service, template_service, user_service
from bot.states.registration import AdminAssistedReg, SelfReg

logger = logging.getLogger(__name__)
router = Router(name="auth")
# Registration only makes sense in a 1:1 chat with the bot — without this an
# admin typing /start in the support group drags them into the reg flow.
router.message.filter(F.chat.type == "private")

DATE_FORMAT = "%d.%m.%Y"
MAX_AGE_YEARS = 120


def face_choices(lang: str) -> list[tuple[str, str]]:
    """(value, label) skin types in the customer's language."""
    return [(c.value, t(f"skin.type.{c.value}", lang)) for c in TelegramUser.FaceCondition]


# ---------------------------------------------------------------------------
# /start entry — routes to self or admin-assisted flow
# ---------------------------------------------------------------------------
@router.message(CommandStart(deep_link=True))
async def start_with_payload(
    message: Message, command: CommandObject, state: FSMContext, bot: Bot, lang: str
) -> None:
    if await _handled_as_returning(message, state, lang):
        return
    payload = command.args or ""
    if payload.startswith("ref_"):
        await _begin_admin_assisted(message, state, bot, payload, lang)
    elif payload.startswith("inv_"):
        await _begin_customer_referral(message, state, payload, lang)
    else:
        await _begin_self(message, state, lang)


@router.message(CommandStart())
async def start_plain(message: Message, state: FSMContext, lang: str) -> None:
    if await _handled_as_returning(message, state, lang):
        return
    await _begin_self(message, state, lang)


async def _handled_as_returning(
    message: Message, state: FSMContext, lang: str
) -> bool:
    """
    Deal with someone we already know, and report whether we did.

    Telegram keeps handing us the same chat id forever, so deleting the chat or
    blocking the bot loses nothing on our side. Sending such a customer back
    through registration would make them retype what we have and, worse, look
    like their history was gone — so /start just greets them instead.
    """
    username = message.from_user.username if message.from_user else None
    user = await user_service.refresh_on_start(
        telegram_id=message.chat.id, username=username
    )
    if user is None:
        return False

    if not user.is_active:
        await state.clear()
        await message.answer(
            t("user.disabled", lang), reply_markup=reply.remove_keyboard()
        )
        return True

    if user.registration_status != TelegramUser.RegistrationStatus.COMPLETED:
        # Started once but never finished — let the flow run again.
        return False

    await state.clear()
    await message.answer(
        t("user.welcome_back", user.language, name=html.escape(user.full_name)),
        reply_markup=reply.main_menu_keyboard(user.language),
    )
    return True


async def _begin_self(message: Message, state: FSMContext, lang: str) -> None:
    await state.clear()
    await user_service.ensure_pending_user(
        telegram_id=message.chat.id,
        username=message.from_user.username if message.from_user else None,
        source=TelegramUser.RegistrationSource.SELF,
    )
    await _ask_language(message, state, SelfReg.language)


async def _begin_customer_referral(
    message: Message, state: FSMContext, payload: str, lang: str
) -> None:
    """
    Someone arrived through another customer's invite link.

    The inviter is only remembered when the link resolves to a real, finished
    customer — a mistyped id must degrade into a plain signup, not block one.
    """
    await _begin_self(message, state, lang)
    try:
        inviter_telegram_id = int(payload.removeprefix("inv_"))
    except ValueError:
        return
    if inviter_telegram_id == message.chat.id:
        return  # inviting yourself
    inviter = await user_service.get_user_by_telegram_id(inviter_telegram_id)
    if inviter is not None:
        await state.update_data(registered_by_id=inviter.pk)


async def _begin_admin_assisted(
    message: Message, state: FSMContext, bot: Bot, payload: str, lang: str
) -> None:
    try:
        admin_telegram_id = int(payload.removeprefix("ref_"))
    except ValueError:
        await _begin_self(message, state, lang)
        return

    seller = await user_service.get_seller_by_telegram_id(admin_telegram_id)
    if seller is None:
        await message.answer(t("reg.invalid_ref", lang))
        await _begin_self(message, state, lang)
        return

    await state.clear()
    await state.update_data(
        seller_id=seller.pk,
        admin_telegram_id=admin_telegram_id,
        admin_name=seller.display_name or str(admin_telegram_id),
    )
    # Create the pending row immediately so the seller sees the user in CRM.
    await user_service.ensure_pending_user(
        telegram_id=message.chat.id,
        username=message.from_user.username if message.from_user else None,
        source=TelegramUser.RegistrationSource.ADMIN,
        referred_by_seller_id=seller.pk,
    )
    # Notify the referring seller that a user started.
    await _safe_send(
        bot,
        admin_telegram_id,
        t("admin.user_started", "uz", telegram_id=message.chat.id),
        "HTML",
    )
    await _ask_language(message, state, AdminAssistedReg.language)


async def _ask_language(message: Message, state: FSMContext, target_state) -> None:
    """
    The first question, before anything else is asked.

    Deliberately not translated — a customer who reads only Russian has to be
    able to find their own option on a screen written in a language they don't
    have yet.
    """
    await state.set_state(target_state)
    await message.answer(
        t("lang.choose", "uz"),
        parse_mode="HTML",
        reply_markup=inline.language_keyboard(),
    )


@router.callback_query(
    SelfReg.language, F.data.startswith(f"{inline.CB_LANGUAGE}{inline.SEP}")
)
@router.callback_query(
    AdminAssistedReg.language,
    F.data.startswith(f"{inline.CB_LANGUAGE}{inline.SEP}"),
)
async def step_language(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    chosen = normalize((callback.data or "").split(inline.SEP, 1)[1])
    await state.update_data(language=chosen)
    await user_service.set_language(callback.from_user.id, chosen)

    data = await state.get_data()
    if "seller_id" in data:
        await state.set_state(AdminAssistedReg.full_name)
        greeting = t(
            "reg.greeting_admin",
            chosen,
            admin_name=html.escape(str(data.get("admin_name") or "Admin")),
        )
    else:
        await state.set_state(SelfReg.full_name)
        greeting = t("reg.greeting_self", chosen)
    await callback.message.answer(
        greeting, parse_mode="HTML", reply_markup=reply.remove_keyboard()
    )


# ---------------------------------------------------------------------------
# Shared step handlers
# ---------------------------------------------------------------------------
@router.message(SelfReg.full_name)
@router.message(AdminAssistedReg.full_name)
async def step_full_name(message: Message, state: FSMContext) -> None:
    lang = await _reg_language(state)
    name = " ".join((message.text or "").split())
    if not name:
        await message.answer(t("reg.ask_name", lang))
        return
    if len(name) < 3:
        await message.answer(t("reg.name_short", lang))
        return
    # "<" or ">" in a name breaks every later HTML-mode message that embeds
    # it (welcome, campaigns, profile) — Telegram rejects the whole send.
    if "<" in name or ">" in name:
        await message.answer(t("reg.name_invalid", lang))
        return
    await state.update_data(full_name=name)
    await _advance(state, SelfReg.birth_date, AdminAssistedReg.birth_date)
    await message.answer(t("reg.ask_birth", lang))


@router.message(SelfReg.birth_date)
@router.message(AdminAssistedReg.birth_date)
async def step_birth_date(message: Message, state: FSMContext) -> None:
    lang = await _reg_language(state)
    raw = (message.text or "").strip()
    try:
        birth_date = datetime.strptime(raw, DATE_FORMAT).date()
    except ValueError:
        await message.answer(t("reg.invalid_date", lang), parse_mode="HTML")
        return
    # A typo here is silent otherwise: the birthday campaign would simply never
    # fire, or fire on a date nobody expects.
    today = date.today()
    if birth_date > today:
        await message.answer(t("reg.date_future", lang))
        return
    if birth_date.year < today.year - MAX_AGE_YEARS:
        await message.answer(t("reg.date_old", lang))
        return
    await state.update_data(birth_date=birth_date.isoformat())
    await _advance(state, SelfReg.phone, AdminAssistedReg.phone)
    await message.answer(
        t("reg.ask_phone", lang), reply_markup=reply.share_contact_keyboard(lang)
    )


@router.message(SelfReg.phone, F.contact)
@router.message(AdminAssistedReg.phone, F.contact)
async def step_phone_contact(message: Message, state: FSMContext) -> None:
    lang = await _reg_language(state)
    # The contact picker will happily send a friend's card; that number would
    # then link this customer to somebody else's pre-registered card.
    if message.from_user and message.contact.user_id != message.from_user.id:
        await message.answer(
            t("reg.contact_not_yours", lang),
            reply_markup=reply.share_contact_keyboard(lang),
        )
        return
    phone = TelegramUser.normalize_phone(message.contact.phone_number)
    if phone is None:
        await message.answer(t("reg.invalid_phone", lang), parse_mode="HTML")
        return
    await state.update_data(phone_number=phone)
    await ask_skin_step(message, state, lang)


@router.message(SelfReg.phone)
@router.message(AdminAssistedReg.phone)
async def step_phone_text(message: Message, state: FSMContext) -> None:
    lang = await _reg_language(state)
    raw = (message.text or "").strip()
    if not raw:
        await message.answer(t("reg.ask_phone_again", lang))
        return
    phone = TelegramUser.normalize_phone(raw)
    if phone is None:
        await message.answer(
            t("reg.invalid_phone", lang),
            parse_mode="HTML",
            reply_markup=reply.share_contact_keyboard(lang),
        )
        return
    await state.update_data(phone_number=phone)
    await ask_skin_step(message, state, lang)


async def ask_skin_step(message: Message, state: FSMContext, lang: str) -> None:
    """
    "Do you know your skin type?" — the fork into either a direct pick or the
    quiz. Asking the type outright used to make people guess; this way the
    ones who don't know get an answer instead of a coin flip.
    """
    await _advance(state, SelfReg.face_condition, AdminAssistedReg.face_condition)
    await message.answer(
        t("skin.know_question", lang),
        parse_mode="HTML",
        reply_markup=inline.know_skin_keyboard(lang),
    )


@router.callback_query(
    SelfReg.face_condition, F.data.startswith(f"{inline.CB_FACE_CONDITION}{inline.SEP}")
)
@router.callback_query(
    AdminAssistedReg.face_condition,
    F.data.startswith(f"{inline.CB_FACE_CONDITION}{inline.SEP}"),
)
async def step_face_condition(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    value = (callback.data or "").split(inline.SEP, 1)[1]
    await state.update_data(face_condition=value)
    await continue_after_skin(callback.message, state, callback.bot)


async def continue_after_skin(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Next step once the skin type is settled — however it was settled.

    Both the "I know it" branch and the quiz land here, which is why it lives
    in this module rather than in either of them.
    """
    lang = await _reg_language(state)
    data = await state.get_data()
    if "seller_id" in data:
        # Admin-assisted: photo filled by admin from CRM — finish now
        await _finalize_registration(message, state, bot, photo_bytes=None)
        return
    await state.set_state(SelfReg.photo)
    await message.answer(
        t("reg.ask_photo", lang), reply_markup=inline.skip_photo_keyboard(lang)
    )


@router.message(SelfReg.photo, F.photo)
async def step_photo_upload(message: Message, state: FSMContext, bot: Bot) -> None:
    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    buffer = await bot.download_file(file.file_path)
    photo_bytes = buffer.read() if buffer is not None else None
    await _finalize_registration(message, state, bot, photo_bytes=photo_bytes)


@router.callback_query(SelfReg.photo, F.data == inline.CB_SKIP_PHOTO)
async def step_photo_skip(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await _finalize_registration(callback.message, state, callback.bot, photo_bytes=None)


@router.message(SelfReg.photo)
async def step_photo_not_a_photo(message: Message, state: FSMContext) -> None:
    # Without this the last step of registration answers nothing at all when
    # the customer types instead of attaching.
    lang = await _reg_language(state)
    await message.answer(
        t("reg.ask_photo", lang), reply_markup=inline.skip_photo_keyboard(lang)
    )


# ---------------------------------------------------------------------------
# Finalization
# ---------------------------------------------------------------------------
async def _finalize_registration(
    message: Message, state: FSMContext, bot: Bot, photo_bytes: bytes | None
) -> None:
    data = await state.get_data()
    await state.clear()

    lang = normalize(data.get("language"))
    is_admin_flow = "seller_id" in data
    source = (
        TelegramUser.RegistrationSource.ADMIN
        if is_admin_flow
        else TelegramUser.RegistrationSource.SELF
    )
    chat = message.chat

    try:
        user = await user_service.complete_user(
            telegram_id=chat.id,
            username=chat.username,
            full_name=data["full_name"],
            birth_date=datetime.fromisoformat(data["birth_date"]).date(),
            phone_number=data["phone_number"],
            face_condition=data["face_condition"],
            source=source,
            language=lang,
            referred_by_seller_id=data.get("seller_id"),
            registered_by_id=data.get("registered_by_id"),
        )
        if photo_bytes:
            await user_service.set_user_photo(
                user.pk, photo_bytes, f"user_{user.telegram_id}.jpg"
            )
    except Exception:  # noqa: BLE001
        logger.exception("Failed to persist registration for %s", chat.id)
        await message.answer(t("reg.error", lang))
        return

    # 1. Welcome message (template) + show persistent main menu
    text, parse_mode = await template_service.render_template(
        "welcome", {"user": user}, lang
    )
    await _safe_send(
        bot,
        chat.id,
        text or t("reg.saved_fallback", lang),
        parse_mode,
        reply.main_menu_keyboard(lang),
    )

    # 2. Immediately send product instructions + inline video buttons
    await send_tutorial_intros(bot, user.telegram_id, lang)

    # 3. Notify the referring seller
    if is_admin_flow and data.get("admin_telegram_id"):
        await _safe_send(
            bot,
            int(data["admin_telegram_id"]),
            t("admin.user_registered", "uz", full_name=html.escape(user.full_name)),
            "HTML",
        )


async def send_tutorial_intros(bot: Bot, telegram_id: int, lang: str) -> None:
    """Send one intro message + inline step buttons per owned product."""
    from core.i18n import pick

    user_products = await user_service.get_user_products(telegram_id)
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
        await _safe_send(bot, telegram_id, body, parse_mode, keyboard)


async def _safe_send(
    bot: Bot, chat_id: int, text: str, parse_mode: str, reply_markup=None
) -> None:
    try:
        await bot.send_message(
            chat_id=chat_id, text=text, parse_mode=parse_mode, reply_markup=reply_markup
        )
    except TelegramAPIError:
        logger.exception("Failed to send message to %s", chat_id)
    except Exception:  # noqa: BLE001
        logger.exception("Unexpected error sending message to %s", chat_id)


async def _reg_language(state: FSMContext) -> str:
    """
    The language picked at the top of this registration.

    Read from FSM data, not from the middleware: mid-registration the customer
    row may still be the pending one created before the pick was saved.
    """
    data = await state.get_data()
    return normalize(data.get("language"))


async def _advance(state: FSMContext, self_state, admin_state) -> None:
    current = await state.get_state()
    if current is not None and current.startswith("AdminAssistedReg"):
        await state.set_state(admin_state)
    else:
        await state.set_state(self_state)


# ---------------------------------------------------------------------------
# /mylink — seller referral link generator
# ---------------------------------------------------------------------------
@router.message(F.text == "/mylink")
async def my_link(message: Message, lang: str) -> None:
    if message.from_user is None:
        return
    seller = await user_service.get_seller_by_telegram_id(message.from_user.id)
    if seller is None:
        await message.answer(t("seller.only", lang))
        return
    await message.answer(
        t("seller.link", lang, link=seller.invite_link), parse_mode="HTML"
    )
