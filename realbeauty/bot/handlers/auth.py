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
from bot import texts
from bot.keyboards import inline, reply
from bot.services import product_service, template_service, user_service
from bot.states.registration import AdminAssistedReg, SelfReg

logger = logging.getLogger(__name__)
router = Router(name="auth")

DATE_FORMAT = "%d.%m.%Y"
MAX_AGE_YEARS = 120
FACE_CHOICES = [(c.value, c.label) for c in TelegramUser.FaceCondition]


# ---------------------------------------------------------------------------
# /start entry — routes to self or admin-assisted flow
# ---------------------------------------------------------------------------
@router.message(CommandStart(deep_link=True))
async def start_with_payload(
    message: Message, command: CommandObject, state: FSMContext, bot: Bot
) -> None:
    if await _handled_as_returning(message, state):
        return
    payload = command.args or ""
    if payload.startswith("ref_"):
        await _begin_admin_assisted(message, state, bot, payload)
    else:
        await _begin_self(message, state)


@router.message(CommandStart())
async def start_plain(message: Message, state: FSMContext) -> None:
    if await _handled_as_returning(message, state):
        return
    await _begin_self(message, state)


async def _handled_as_returning(message: Message, state: FSMContext) -> bool:
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
            texts.ACCOUNT_DISABLED, reply_markup=reply.remove_keyboard()
        )
        return True

    if user.registration_status != TelegramUser.RegistrationStatus.COMPLETED:
        # Started once but never finished — let the flow run again.
        return False

    await state.clear()
    await message.answer(
        texts.WELCOME_BACK.format(name=html.escape(user.full_name)),
        reply_markup=reply.main_menu_keyboard(),
    )
    return True


async def _begin_self(message: Message, state: FSMContext) -> None:
    await state.clear()
    await user_service.ensure_pending_user(
        telegram_id=message.chat.id,
        username=message.from_user.username if message.from_user else None,
        source=TelegramUser.RegistrationSource.SELF,
    )
    await state.set_state(SelfReg.full_name)
    await message.answer(texts.GREETING_SELF, reply_markup=reply.remove_keyboard())


async def _begin_admin_assisted(
    message: Message, state: FSMContext, bot: Bot, payload: str
) -> None:
    try:
        admin_telegram_id = int(payload.removeprefix("ref_"))
    except ValueError:
        await _begin_self(message, state)
        return

    seller = await user_service.get_seller_by_telegram_id(admin_telegram_id)
    if seller is None:
        await message.answer(
            "Referal havola yaroqsiz. O'zingiz ro'yxatdan o'tishingiz mumkin."
        )
        await _begin_self(message, state)
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
        texts.ADMIN_USER_STARTED.format(telegram_id=message.chat.id),
        "HTML",
    )

    await state.set_state(AdminAssistedReg.full_name)
    await message.answer(
        texts.GREETING_ADMIN.format(
            admin_name=html.escape(seller.display_name or "Admin")
        ),
        reply_markup=reply.remove_keyboard(),
    )


# ---------------------------------------------------------------------------
# Shared step handlers
# ---------------------------------------------------------------------------
@router.message(SelfReg.full_name)
@router.message(AdminAssistedReg.full_name)
async def step_full_name(message: Message, state: FSMContext) -> None:
    name = " ".join((message.text or "").split())
    if not name:
        await message.answer(texts.ASK_FULL_NAME)
        return
    if len(name) < 3:
        await message.answer(texts.NAME_TOO_SHORT)
        return
    # "<" or ">" in a name breaks every later HTML-mode message that embeds
    # it (welcome, campaigns, profile) — Telegram rejects the whole send.
    if "<" in name or ">" in name:
        await message.answer(texts.NAME_INVALID)
        return
    await state.update_data(full_name=name)
    await _advance(state, SelfReg.birth_date, AdminAssistedReg.birth_date)
    await message.answer(texts.ASK_BIRTH_DATE)


@router.message(SelfReg.birth_date)
@router.message(AdminAssistedReg.birth_date)
async def step_birth_date(message: Message, state: FSMContext) -> None:
    raw = (message.text or "").strip()
    try:
        birth_date = datetime.strptime(raw, DATE_FORMAT).date()
    except ValueError:
        await message.answer(texts.INVALID_DATE)
        return
    # A typo here is silent otherwise: the birthday campaign would simply never
    # fire, or fire on a date nobody expects.
    today = date.today()
    if birth_date > today:
        await message.answer(texts.DATE_IN_FUTURE)
        return
    if birth_date.year < today.year - MAX_AGE_YEARS:
        await message.answer(texts.DATE_TOO_OLD)
        return
    await state.update_data(birth_date=birth_date.isoformat())
    await _advance(state, SelfReg.phone, AdminAssistedReg.phone)
    await message.answer(texts.ASK_PHONE, reply_markup=reply.share_contact_keyboard())


@router.message(SelfReg.phone, F.contact)
@router.message(AdminAssistedReg.phone, F.contact)
async def step_phone_contact(message: Message, state: FSMContext) -> None:
    # The contact picker will happily send a friend's card; that number would
    # then link this customer to somebody else's pre-registered card.
    if message.from_user and message.contact.user_id != message.from_user.id:
        await message.answer(
            texts.CONTACT_NOT_YOURS, reply_markup=reply.share_contact_keyboard()
        )
        return
    phone = TelegramUser.normalize_phone(message.contact.phone_number)
    if phone is None:
        await message.answer(texts.INVALID_PHONE, parse_mode="HTML")
        return
    await state.update_data(phone_number=phone)
    await _ask_face_condition(message, state)


@router.message(SelfReg.phone)
@router.message(AdminAssistedReg.phone)
async def step_phone_text(message: Message, state: FSMContext) -> None:
    raw = (message.text or "").strip()
    if not raw:
        await message.answer(texts.ASK_PHONE_AGAIN)
        return
    phone = TelegramUser.normalize_phone(raw)
    if phone is None:
        await message.answer(
            texts.INVALID_PHONE,
            parse_mode="HTML",
            reply_markup=reply.share_contact_keyboard(),
        )
        return
    await state.update_data(phone_number=phone)
    await _ask_face_condition(message, state)


async def _ask_face_condition(message: Message, state: FSMContext) -> None:
    await _advance(state, SelfReg.face_condition, AdminAssistedReg.face_condition)
    await message.answer(
        texts.ASK_FACE_CONDITION,
        reply_markup=inline.face_condition_keyboard(FACE_CHOICES),
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

    current = await state.get_state()
    if current == SelfReg.face_condition.state:
        await state.set_state(SelfReg.photo)
        await callback.message.answer(
            texts.ASK_PHOTO, reply_markup=inline.skip_photo_keyboard()
        )
    else:
        # Admin-assisted: photo filled by admin from CRM — finish now
        await _finalize_registration(
            callback.message, state, callback.bot, photo_bytes=None
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
async def step_photo_not_a_photo(message: Message) -> None:
    # Without this the last step of registration answers nothing at all when
    # the customer types instead of attaching.
    await message.answer(texts.ASK_PHOTO, reply_markup=inline.skip_photo_keyboard())


# ---------------------------------------------------------------------------
# Finalization
# ---------------------------------------------------------------------------
async def _finalize_registration(
    message: Message, state: FSMContext, bot: Bot, photo_bytes: bytes | None
) -> None:
    data = await state.get_data()
    await state.clear()

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
            referred_by_seller_id=data.get("seller_id"),
        )
        if photo_bytes:
            await user_service.set_user_photo(
                user.pk, photo_bytes, f"user_{user.telegram_id}.jpg"
            )
    except Exception:  # noqa: BLE001
        logger.exception("Failed to persist registration for %s", chat.id)
        await message.answer(texts.REG_ERROR)
        return

    # 1. Welcome message (template) + show persistent main menu
    text, parse_mode = await template_service.render_template("welcome", {"user": user})
    await _safe_send(
        bot,
        chat.id,
        text or texts.REG_SAVED_FALLBACK,
        parse_mode,
        reply.main_menu_keyboard(),
    )

    # 2. Immediately send product instructions + inline video buttons
    await send_tutorial_intros(bot, user.telegram_id)

    # 3. Notify the referring seller
    if is_admin_flow and data.get("admin_telegram_id"):
        await _safe_send(
            bot,
            int(data["admin_telegram_id"]),
            texts.ADMIN_USER_REGISTERED.format(
                full_name=html.escape(user.full_name)
            ),
            "HTML",
        )


async def send_tutorial_intros(bot: Bot, telegram_id: int) -> None:
    """Send one intro message + inline step buttons per owned product."""
    user_products = await user_service.get_user_products(telegram_id)
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
async def my_link(message: Message) -> None:
    if message.from_user is None:
        return
    seller = await user_service.get_seller_by_telegram_id(message.from_user.id)
    if seller is None:
        await message.answer(texts.SELLER_ONLY)
        return
    await message.answer(texts.MY_LINK.format(link=seller.invite_link))
