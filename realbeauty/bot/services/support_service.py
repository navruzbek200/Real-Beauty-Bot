from __future__ import annotations

from asgiref.sync import sync_to_async

from apps.support.models import SupportMessage, SupportThread
from apps.users.models import SellerProfile, TelegramUser

_SUBJECT_MAX = 60


@sync_to_async
def get_staff_telegram_ids() -> list[int]:
    """Telegram ids of staff who should hear about new support messages."""
    return list(
        SellerProfile.objects.filter(is_active=True).values_list(
            "telegram_id", flat=True
        )
    )


@sync_to_async
def add_user_message(
    *, telegram_id: int, text: str, photo_file_id: str = ""
) -> SupportThread:
    """
    Append an incoming message to the user's open thread, creating one if the
    user has none or their previous thread was closed.
    """
    user = TelegramUser.objects.get(telegram_id=telegram_id)
    # select_related: the caller touches thread.user after the sync context
    # closes, where a lazy load would raise SynchronousOnlyOperation.
    thread = (
        SupportThread.objects.select_related("user")
        .filter(user=user)
        .exclude(status=SupportThread.Status.CLOSED)
        .order_by("-last_message_at")
        .first()
    )
    if thread is None:
        subject = text[:_SUBJECT_MAX] or "📷 Rasm"
        thread = SupportThread.objects.create(user=user, subject=subject)

    SupportMessage.objects.create(
        thread=thread,
        direction=SupportMessage.Direction.IN,
        text=text,
        photo_file_id=photo_file_id,
    )
    thread.touch(from_user=True)
    return thread
