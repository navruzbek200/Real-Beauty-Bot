from __future__ import annotations

from .models import TelegramUser


class InvalidPhoneNumber(ValueError):
    pass


def register_app_user(*, full_name: str, phone_number: str) -> TelegramUser:
    """
    Record (or update) a mobile-app signup as a customer card.

    Matched by phone_tail against the same pool of cards the Telegram bot
    reads from, so a person who later opens the bot with this number links
    onto this exact card instead of getting a duplicate — the phone_tail
    matching is what the bot's own /start flow already relies on.
    """
    normalized = TelegramUser.normalize_phone(phone_number)
    if normalized is None:
        raise InvalidPhoneNumber("Telefon raqam noto'g'ri formatda")

    tail = TelegramUser.phone_tail_of(normalized)
    existing = TelegramUser.objects.filter(phone_tail=tail).first()
    if existing is not None:
        # A card that already has a name (typed by staff, or completed via the
        # bot) knows more about this person than a bare app signup does —
        # don't clobber it. Only fill in what's missing.
        if full_name and not existing.full_name:
            existing.full_name = full_name
            existing.save(update_fields=["full_name"])
        return existing

    return TelegramUser.objects.create(
        full_name=full_name,
        phone_number=normalized,
        source=TelegramUser.RegistrationSource.APP,
        registration_status=TelegramUser.RegistrationStatus.PENDING,
    )
