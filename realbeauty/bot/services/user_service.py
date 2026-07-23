from __future__ import annotations

from datetime import date
from typing import Any

from asgiref.sync import sync_to_async
from django.db import transaction

from apps.users.models import SellerProfile, TelegramUser, UserProduct


@sync_to_async
def get_user(telegram_id: int) -> TelegramUser | None:
    return TelegramUser.objects.filter(telegram_id=telegram_id).first()


@sync_to_async
def refresh_on_start(*, telegram_id: int, username: str | None) -> TelegramUser | None:
    """
    Fetch the sender's card, keeping their username current.

    People rename themselves on Telegram, and /start is the one moment we are
    guaranteed to hear about it — a stale @handle in the CRM is how staff lose
    track of who they are talking to.
    """
    user = TelegramUser.objects.filter(telegram_id=telegram_id).first()
    if user is None:
        return None
    if username != user.username:
        user.username = username
        user.save(update_fields=["username"])
    return user


@sync_to_async
def set_language(telegram_id: int, language: str) -> None:
    """Persist the language the customer picked, if we know them at all."""
    TelegramUser.objects.filter(telegram_id=telegram_id).update(language=language)


@sync_to_async
def set_face_condition(telegram_id: int, face_condition: str) -> None:
    TelegramUser.objects.filter(telegram_id=telegram_id).update(
        face_condition=face_condition
    )


@sync_to_async
def get_seller_by_telegram_id(telegram_id: int) -> SellerProfile | None:
    return (
        SellerProfile.objects.select_related("user")
        .filter(telegram_id=telegram_id, is_active=True)
        .first()
    )


def _find_preregistered(
    *, username: str | None, phone_number: str | None = None
) -> TelegramUser | None:
    """
    Find a card staff created ahead of time for this person, so the customer
    keeps the products and notes already entered instead of splitting into a
    second, empty card.

    Matched on username first (exact, cheap), then on the phone number's last
    9 digits so formatting differences don't break the link.
    """
    unlinked = TelegramUser.objects.filter(telegram_id__isnull=True)

    if username:
        match = unlinked.filter(username__iexact=username).first()
        if match is not None:
            return match

    tail = TelegramUser.phone_tail_of(phone_number)
    if tail:
        return unlinked.filter(phone_tail=tail).first()
    return None


@sync_to_async
def get_user_by_telegram_id(telegram_id: int) -> TelegramUser | None:
    """A completed customer, or None — used to validate a customer invite link."""
    return TelegramUser.objects.filter(
        telegram_id=telegram_id,
        registration_status=TelegramUser.RegistrationStatus.COMPLETED,
    ).first()


@sync_to_async
def ensure_pending_user(
    *,
    telegram_id: int,
    username: str | None,
    source: str,
    referred_by_seller_id: int | None = None,
) -> TelegramUser:
    """
    Create (or fetch) a user row as soon as they press /start, with status
    PENDING — so admin-referred users appear in the CRM immediately, flagged
    as "needs to fill". Never downgrades an already-completed registration.
    """
    if not TelegramUser.objects.filter(telegram_id=telegram_id).exists():
        # Only a username can be matched this early — the phone comes later.
        claimed = _find_preregistered(username=username)
        if claimed is not None:
            claimed.telegram_id = telegram_id
            claimed.username = username or claimed.username
            claimed.save(update_fields=["telegram_id", "username"])
            return claimed

    user, created = TelegramUser.objects.get_or_create(
        telegram_id=telegram_id,
        defaults={
            "username": username,
            "source": source,
            "referred_by_seller_id": referred_by_seller_id,
            "registration_status": TelegramUser.RegistrationStatus.PENDING,
        },
    )
    if not created and user.registration_status == TelegramUser.RegistrationStatus.PENDING:
        # keep referral/source fresh while still pending
        user.username = username or user.username
        if referred_by_seller_id:
            user.referred_by_seller_id = referred_by_seller_id
            user.source = source
        user.save(update_fields=["username", "referred_by_seller", "source"])
    return user


@sync_to_async
def complete_user(
    *,
    telegram_id: int,
    username: str | None,
    full_name: str,
    birth_date: date,
    phone_number: str,
    face_condition: str,
    source: str,
    language: str = "uz",
    referred_by_seller_id: int | None = None,
    registered_by_id: int | None = None,
) -> TelegramUser:
    """Fill in registration data and mark the user COMPLETED (idempotent)."""
    from django.utils import timezone

    with transaction.atomic():
        # The phone is only known now, so this is the last chance to notice the
        # customer already has a card that staff filled in by hand.
        preregistered = _find_preregistered(
            username=username, phone_number=phone_number
        )
        if preregistered is not None:
            # Free the telegram_id from the empty row /start made before we knew
            # who this was, then move it onto the card staff prepared.
            TelegramUser.objects.filter(telegram_id=telegram_id).exclude(
                pk=preregistered.pk
            ).delete()
            preregistered.telegram_id = telegram_id
            preregistered.save(update_fields=["telegram_id"])

        defaults: dict[str, Any] = {
            "username": username,
            "full_name": full_name,
            "birth_date": birth_date,
            "phone_number": phone_number,
            "face_condition": face_condition,
            "language": language,
            "registration_status": TelegramUser.RegistrationStatus.COMPLETED,
        }
        # A pre-registered card already carries the seller who created it —
        # don't overwrite that attribution with the deep link's.
        if preregistered is None:
            defaults["source"] = source
            defaults["referred_by_seller_id"] = referred_by_seller_id
        if registered_by_id is not None:
            defaults["registered_by_id"] = registered_by_id

        existing = TelegramUser.objects.filter(telegram_id=telegram_id).first()
        # Only the first completion sets this: re-running registration must not
        # restart every "N days after signing up" campaign for this customer.
        if existing is None or existing.registered_at is None:
            defaults["registered_at"] = timezone.now()

        user, _ = TelegramUser.objects.update_or_create(
            telegram_id=telegram_id, defaults=defaults
        )

    _award_registration_points(user)
    return user


def _award_registration_points(user: TelegramUser) -> None:
    """
    Welcome bonus for the customer, referral bonus for whoever brought them.

    Runs after the transaction commits so a loyalty problem can never undo a
    registration — the customer being in the CRM matters more than the points.
    """
    from apps.loyalty.models import PointsTransaction
    from apps.loyalty.services import award

    award(
        user,
        PointsTransaction.Reason.REGISTRATION,
        reference=f"registration:{user.pk}",
        notify=False,  # the welcome message lands in the same second
    )
    if user.registered_by_id:
        award(
            user.registered_by,
            PointsTransaction.Reason.REFERRAL,
            reference=f"referral:{user.pk}",
            note=user.full_name[:200],
        )


@sync_to_async
def set_user_photo(user_id: int, file_bytes: bytes, filename: str) -> None:
    from django.core.files.base import ContentFile

    user = TelegramUser.objects.get(pk=user_id)
    user.photo.save(filename, ContentFile(file_bytes), save=True)


@sync_to_async
def get_user_products(telegram_id: int) -> list[UserProduct]:
    return list(
        UserProduct.objects.select_related("product").filter(
            user__telegram_id=telegram_id
        )
    )
