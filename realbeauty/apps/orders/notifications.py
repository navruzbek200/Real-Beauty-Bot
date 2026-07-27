"""
Telegram side of a new order: the card in the staff group, the confirmation
in the customer's chat.

Both sends are best-effort — a Telegram hiccup must never lose the order
itself, which is already committed by the time these run.
"""

from __future__ import annotations

import html
import logging

from core import telegram

from .models import Order

logger = logging.getLogger(__name__)

_STATUS_LABELS = dict(Order.Status.choices)
_DELIVERY_LABELS = dict(Order.Delivery.choices)

_CUSTOMER_TEXTS = {
    "uz": (
        "🛍 <b>Buyurtmangiz qabul qilindi!</b>\n\n{lines}\n"
        "💵 Jami: <b>{total} so'm</b>\n{delivery}\n\n"
        "Operatorimiz tez orada qo'ng'iroq qilib tasdiqlaydi. Rahmat! 🌸"
    ),
    "ru": (
        "🛍 <b>Ваш заказ принят!</b>\n\n{lines}\n"
        "💵 Итого: <b>{total} сум</b>\n{delivery}\n\n"
        "Наш оператор скоро позвонит для подтверждения. Спасибо! 🌸"
    ),
    "en": (
        "🛍 <b>Your order has been received!</b>\n\n{lines}\n"
        "💵 Total: <b>{total} UZS</b>\n{delivery}\n\n"
        "Our operator will call you shortly to confirm. Thank you! 🌸"
    ),
}


def _money(value: int) -> str:
    return f"{value:,}".replace(",", " ")


def _item_lines(order: Order) -> str:
    return "\n".join(
        f"• {html.escape(item.product_name)} × {item.quantity} — "
        f"{_money(item.subtotal)} so'm"
        for item in order.items.all()
    )


def group_card(order: Order) -> str:
    """The staff-group message: everything the operator needs to call back."""
    username = f"@{html.escape(order.user.username)}" if order.user.username else "—"
    return (
        f"🛒 <b>Yangi buyurtma #{order.pk}</b>\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"👤 {html.escape(order.customer_name)}\n"
        f"📞 {html.escape(order.phone_number)}\n"
        f"💬 Telegram: {username}\n"
        f"{_DELIVERY_LABELS[order.delivery_method]}\n"
        f"📍 {html.escape(order.address)}\n"
        + (f"📝 {html.escape(order.comment)}\n" if order.comment else "")
        + "━━━━━━━━━━━━━━━━━━\n"
        f"{_item_lines(order)}\n\n"
        f"💵 Jami: <b>{_money(order.total)} so'm</b>"
    )


def notify_new_order(order: Order) -> None:
    """Post the order card to the support group and confirm to the customer."""
    from apps.support.models import SupportSettings

    settings_obj = SupportSettings.get()
    if settings_obj.group_chat_id:
        try:
            telegram.send_message(
                settings_obj.group_chat_id, group_card(order), parse_mode="HTML"
            )
        except telegram.TelegramError:
            logger.exception("Order %s: group notification failed", order.pk)
    else:
        logger.warning("Order %s: support group not configured", order.pk)

    lang = order.user.language if order.user.language in _CUSTOMER_TEXTS else "uz"
    text = _CUSTOMER_TEXTS[lang].format(
        lines=_item_lines(order),
        total=_money(order.total),
        delivery=_DELIVERY_LABELS[order.delivery_method],
    )
    try:
        telegram.send_message(order.user.telegram_id, text, parse_mode="HTML")
    except telegram.TelegramError:
        logger.exception("Order %s: customer confirmation failed", order.pk)
