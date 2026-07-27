"""
Card payments through Telegram's native invoice flow.

Telegram sits between us and the acquirer: BotFather connects the bot to a
payment provider (Click or Payme for Uzbekistan) and hands back a provider
token. We call sendInvoice with that token, Telegram renders the card form and
talks to the provider, and the bot receives `pre_checkout_query` then
`successful_payment` (handled in bot/handlers/payments.py). No card data ever
reaches this server, so there is no PCI surface here.

Everything in this module is inert until PAYMENT_PROVIDER_TOKEN is set: with
no token `payments_enabled()` is False, the Mini App never offers the card
option, and every order stays cash-on-delivery exactly as before.
"""

from __future__ import annotations

import logging

from django.conf import settings

from core import telegram

from .models import Order

logger = logging.getLogger(__name__)

# Telegram takes amounts in the currency's *smallest* unit, scaled by the `exp`
# it publishes for that currency in currencies.json. UZS is listed with exp=2,
# so 250 000 so'm is sent as 25 000 000. If invoices ever come out 100× wrong,
# this constant is the single place to correct.
CURRENCY = "UZS"
CURRENCY_MULTIPLIER = 100

# Ties a Telegram invoice back to the row it was raised for.
PAYLOAD_PREFIX = "order:"

_INVOICE_TEXT = {
    "uz": ("Buyurtma #{id}", "To'lovni karta orqali amalga oshiring 💳"),
    "ru": ("Заказ #{id}", "Оплатите заказ картой 💳"),
    "en": ("Order #{id}", "Pay for your order by card 💳"),
}


def payments_enabled() -> bool:
    """True when a provider token is configured, i.e. cards can be charged."""
    return bool((getattr(settings, "PAYMENT_PROVIDER_TOKEN", "") or "").strip())


def order_id_from_payload(payload: str) -> int | None:
    """The order id carried by an invoice payload, or None if it isn't ours."""
    if not payload.startswith(PAYLOAD_PREFIX):
        return None
    try:
        return int(payload.removeprefix(PAYLOAD_PREFIX))
    except ValueError:
        return None


def send_invoice(order: Order) -> bool:
    """
    Send the card invoice for `order` to the customer's chat.

    Returns whether Telegram accepted it. A False here is not fatal: the order
    is already saved, and the operator can still take payment on delivery.
    """
    if not payments_enabled():
        logger.info("Order %s: no provider token, invoice skipped", order.pk)
        return False

    lang = order.user.language if order.user.language in _INVOICE_TEXT else "uz"
    title, description = _INVOICE_TEXT[lang]
    # One line per product keeps the amounts the customer sees identical to
    # the ones in their confirmation message.
    prices = [
        {
            "label": f"{item.product_name} × {item.quantity}"[:32],
            "amount": item.subtotal * CURRENCY_MULTIPLIER,
        }
        for item in order.items.all()
    ]
    if not prices:
        return False

    try:
        telegram.call(
            "sendInvoice",
            {
                "chat_id": order.user.telegram_id,
                "title": title.format(id=order.pk),
                "description": description,
                "payload": f"{PAYLOAD_PREFIX}{order.pk}",
                "provider_token": settings.PAYMENT_PROVIDER_TOKEN.strip(),
                "currency": CURRENCY,
                "prices": prices,
            },
        )
    except telegram.TelegramError:
        logger.exception("Order %s: sendInvoice failed", order.pk)
        return False

    Order.objects.filter(pk=order.pk).update(
        payment_status=Order.PaymentStatus.PENDING
    )
    return True


def mark_paid(order_id: int, charge_id: str = "") -> Order | None:
    """
    Record a completed payment. Idempotent — Telegram can redeliver the same
    successful_payment update, and a second call must not double-report it.
    """
    from django.utils import timezone

    updated = Order.objects.filter(pk=order_id).exclude(
        payment_status=Order.PaymentStatus.PAID
    ).update(
        payment_status=Order.PaymentStatus.PAID,
        paid_at=timezone.now(),
        provider_charge_id=charge_id[:255],
    )
    if not updated:
        return None
    return Order.objects.filter(pk=order_id).first()
