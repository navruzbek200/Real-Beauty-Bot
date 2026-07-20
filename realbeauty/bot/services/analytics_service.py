from __future__ import annotations

from asgiref.sync import sync_to_async
from django.core.files.base import ContentFile

from apps.analytics.imaging import make_thumbnail
from apps.analytics.models import ProgressPhoto, UserFeedback
from apps.users.models import TelegramUser, UserProduct


@sync_to_async
def save_feedback(
    *,
    telegram_id: int,
    product_id: int | None,
    week: int,
    text: str,
    rating: int | None,
) -> None:
    user = TelegramUser.objects.get(telegram_id=telegram_id)
    UserFeedback.objects.create(
        user=user,
        product_id=product_id,
        week=week,
        text=text,
        rating=rating,
    )


@sync_to_async
def save_progress_photo(
    *,
    telegram_id: int,
    product_id: int | None,
    file_bytes: bytes,
    file_id: str,
    filename: str,
    label: str,
) -> None:
    """
    Store a before/after photo.

    Only a thumbnail touches our disk — the original stays on Telegram and is
    reachable via `file_id`, so the media directory grows slowly.
    """
    user = TelegramUser.objects.get(telegram_id=telegram_id)
    photo = ProgressPhoto(
        user=user, product_id=product_id, label=label, file_id=file_id
    )
    thumb = make_thumbnail(file_bytes, ProgressPhoto.THUMBNAIL_SIZE)
    photo.thumbnail.save(filename, ContentFile(thumb), save=True)


@sync_to_async
def mark_week_sent(telegram_id: int, product_id: int, week: int) -> None:
    field = "week1_sent" if week == 1 else "week2_sent"
    UserProduct.objects.filter(
        user__telegram_id=telegram_id, product_id=product_id
    ).update(**{field: True})
