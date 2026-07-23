"""The "Bonuslarim" screen: balance, tier, rewards and history."""

from __future__ import annotations

import html
import logging

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from django.conf import settings

from apps.loyalty.services import RedeemError
from bot.filters.menu import MenuText
from bot.i18n import t
from bot.keyboards import inline
from bot.services import loyalty_service, user_service
from core.i18n import pick

logger = logging.getLogger(__name__)
router = Router(name="loyalty")
router.message.filter(F.chat.type == "private")

_BAR_FILLED = "▰"
_BAR_EMPTY = "▱"
_BAR_WIDTH = 10


def _bar(progress: float) -> str:
    filled = max(0, min(_BAR_WIDTH, round(progress * _BAR_WIDTH)))
    return _BAR_FILLED * filled + _BAR_EMPTY * (_BAR_WIDTH - filled)


def _invite_link(telegram_id: int) -> str:
    """
    The customer's own referral link.

    Deliberately a customer link (`inv_`), not the seller one (`ref_`): they
    open two different registration flows, and a customer handing out a
    seller's link would attribute the signup to the wrong person.
    """
    username = getattr(settings, "BOT_USERNAME", "RealBeautyBot")
    return f"https://t.me/{username}?start=inv_{telegram_id}"


def _card_text(card: loyalty_service.LoyaltyCard, lang: str, telegram_id: int) -> str:
    conf = card.settings
    blocks = [
        t("loyalty.header", lang),
        t("loyalty.balance", lang, points=card.balance),
        t(
            "loyalty.tier",
            lang,
            tier=t(card.tier.label_key, lang),
            cashback=card.tier.cashback,
        ),
        t("loyalty.lifetime", lang, lifetime=card.lifetime),
    ]
    if card.tier.next_at is not None:
        blocks.append(
            t(
                "loyalty.next_tier",
                lang,
                next_tier=t(card.tier.next_label_key, lang),
                remaining=card.tier.remaining,
                bar=_bar(card.tier.progress),
            )
        )
    else:
        blocks.append(t("loyalty.max_tier", lang))

    blocks.append(
        t(
            "loyalty.how_to_earn",
            lang,
            purchase=conf.points_purchase,
            feedback=conf.points_feedback,
            progress=conf.points_progress,
            referral=conf.points_referral,
            birthday=conf.points_birthday,
        )
    )
    # The invite link is the one earning action the customer can take right
    # now, so it sits under the list that mentions it — labelled, not just a
    # bare code block nobody would guess the purpose of.
    blocks.append(
        t("loyalty.invite_label", lang) + f"\n<code>{_invite_link(telegram_id)}</code>"
    )
    return "\n\n".join(blocks)


@router.message(MenuText("menu.bonus"))
async def show_card(message: Message, state: FSMContext, lang: str) -> None:
    await state.clear()
    if message.from_user is None:
        return
    user = await user_service.get_user(message.from_user.id)
    if user is None or not user.full_name:
        await message.answer(t("user.not_registered", lang))
        return

    card = await loyalty_service.get_card(message.from_user.id)
    if card is None:
        # Switched off in the CRM. The button stays on the keyboard (it is
        # baked into every message already sent), so it has to say something
        # true rather than "I didn't catch that".
        await message.answer(t("loyalty.disabled", lang))
        return
    await message.answer(
        _card_text(card, lang, message.from_user.id),
        parse_mode="HTML",
        reply_markup=inline.loyalty_keyboard(lang, has_rewards=card.has_rewards),
    )


@router.callback_query(F.data == inline.CB_LOYALTY_BACK)
async def back_to_card(callback: CallbackQuery, lang: str) -> None:
    await callback.answer()
    card = await loyalty_service.get_card(callback.from_user.id)
    if card is None:
        return
    await _edit(
        callback,
        _card_text(card, lang, callback.from_user.id),
        inline.loyalty_keyboard(lang, has_rewards=card.has_rewards),
    )


@router.callback_query(F.data == inline.CB_LOYALTY_HISTORY)
async def show_history(callback: CallbackQuery, lang: str) -> None:
    await callback.answer()
    entries = await loyalty_service.get_history(callback.from_user.id)
    if not entries:
        body = t("loyalty.history_empty", lang)
    else:
        lines = [
            t(
                "loyalty.history_line",
                lang,
                sign="+" if entry.points > 0 else "−",
                points=abs(entry.points),
                reason=t(entry.reason_key, lang),
                date=entry.date,
            )
            for entry in entries
        ]
        body = "\n".join(lines)
    text = f"{t('loyalty.history_header', lang)}\n\n{body}"
    await _edit(callback, text, inline.back_to_loyalty_keyboard(lang))


@router.callback_query(F.data == inline.CB_LOYALTY_REWARDS)
async def show_rewards(callback: CallbackQuery, lang: str) -> None:
    await callback.answer()
    card = await loyalty_service.get_card(callback.from_user.id)
    if card is None:
        return
    rewards = await loyalty_service.get_rewards()
    if not rewards:
        await _edit(
            callback,
            t("loyalty.rewards_empty", lang),
            inline.back_to_loyalty_keyboard(lang),
        )
        return

    lines = [t("loyalty.rewards_header", lang, points=card.balance), ""]
    buttons: list[tuple[int, str]] = []
    for reward in rewards:
        title = pick(reward, "title", lang)
        lines.append(
            t(
                "loyalty.reward_line",
                lang,
                title=html.escape(title),
                cost=reward.cost_points,
            )
        )
        description = pick(reward, "description", lang)
        if description:
            lines.append(f"<i>{html.escape(description)}</i>")
        # Affordability is shown on the button itself, so a customer does not
        # have to compare two numbers on separate lines before tapping.
        mark = "✅" if card.balance >= reward.cost_points else "🔒"
        buttons.append((reward.pk, f"{mark} {title} · {reward.cost_points}"))

    await _edit(
        callback, "\n".join(lines), inline.rewards_keyboard(buttons, lang)
    )


@router.callback_query(F.data.startswith(f"{inline.CB_LOYALTY_REDEEM}{inline.SEP}"))
async def redeem(callback: CallbackQuery, lang: str) -> None:
    try:
        reward_id = int((callback.data or "").split(inline.SEP, 1)[1])
    except ValueError:
        await callback.answer()
        return

    try:
        redemption, balance = await loyalty_service.redeem_reward(
            callback.from_user.id, reward_id
        )
    except RedeemError as exc:
        card = await loyalty_service.get_card(callback.from_user.id)
        balance = card.balance if card else 0
        rewards = {r.pk: r for r in await loyalty_service.get_rewards()}
        reward = rewards.get(reward_id)
        if exc.code == "not_enough" and reward is not None:
            await callback.answer()
            await callback.message.answer(
                t(
                    "loyalty.redeem_not_enough",
                    lang,
                    cost=reward.cost_points,
                    points=balance,
                ),
                parse_mode="HTML",
            )
        else:
            await callback.answer(t("loyalty.redeem_unavailable", lang), show_alert=True)
        return
    except Exception:  # noqa: BLE001
        logger.exception("Redemption failed for %s", callback.from_user.id)
        await callback.answer(t("loyalty.redeem_error", lang), show_alert=True)
        return

    await callback.answer()
    title = pick(redemption.reward, "title", lang) if redemption.reward else ""
    await callback.message.answer(
        t(
            "loyalty.redeem_ok",
            lang,
            title=html.escape(title),
            code=redemption.code,
            points=balance,
        ),
        parse_mode="HTML",
    )


async def _edit(callback: CallbackQuery, text: str, markup) -> None:
    """
    Redraw the bonus screen in place.

    Editing keeps the section to one message instead of a growing stack; if
    the message is too old to edit, a fresh one is still better than silence.
    """
    try:
        await callback.message.edit_text(
            text, parse_mode="HTML", reply_markup=markup
        )
    except TelegramBadRequest:
        await callback.message.answer(text, parse_mode="HTML", reply_markup=markup)
