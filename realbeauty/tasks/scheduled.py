from __future__ import annotations

import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def send_week1_checkins(self) -> int:
    """Send week-1 check-in to eligible purchases. Returns count sent."""
    from apps.bot_settings.models import GlobalSettings
    from apps.users.models import UserProduct
    from bot.keyboards import inline
    from tasks.notifications import send_templated_message_sync

    settings = GlobalSettings.get()
    cutoff = timezone.now() - timedelta(days=settings.week1_delay_days)

    qs = UserProduct.objects.select_related("user", "product").filter(
        purchased_at__lte=cutoff, week1_sent=False
    )
    sent = 0
    for up in qs:
        context = {"user": up.user, "product": up.product, "week": 1}
        keyboard = inline.feedback_button_keyboard(
            settings.feedback_button_label, 1, up.product_id
        )
        try:
            send_templated_message_sync(
                up.user.telegram_id,
                up.user_id,
                "week1_checkin",
                context,
                keyboard,
            )
            up.week1_sent = True
            up.save(update_fields=["week1_sent"])
            sent += 1
        except Exception as exc:  # noqa: BLE001
            logger.exception("week1 send failed for user_product %s", up.pk)
            try:
                self.retry(exc=exc)
            except self.MaxRetriesExceededError:
                logger.error("week1 max retries exceeded for %s", up.pk)
    return sent


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def send_week2_progress(self) -> int:
    """Send week-2 progress request to eligible purchases. Returns count sent."""
    from apps.bot_settings.models import GlobalSettings
    from apps.users.models import UserProduct
    from bot.keyboards import inline
    from tasks.notifications import send_templated_message_sync

    settings = GlobalSettings.get()
    cutoff = timezone.now() - timedelta(days=settings.week2_delay_days)

    qs = UserProduct.objects.select_related("user", "product").filter(
        purchased_at__lte=cutoff, week2_sent=False
    )
    sent = 0
    for up in qs:
        context = {"user": up.user, "product": up.product, "week": 2}
        keyboard = inline.progress_button_keyboard(
            settings.before_after_button_label, up.product_id
        )
        try:
            send_templated_message_sync(
                up.user.telegram_id,
                up.user_id,
                "week2_progress",
                context,
                keyboard,
            )
            up.week2_sent = True
            up.save(update_fields=["week2_sent"])
            sent += 1
        except Exception as exc:  # noqa: BLE001
            logger.exception("week2 send failed for user_product %s", up.pk)
            try:
                self.retry(exc=exc)
            except self.MaxRetriesExceededError:
                logger.error("week2 max retries exceeded for %s", up.pk)
    return sent


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def send_birthday_messages(self) -> int:
    """Send birthday-sale message to users whose birthday is today (Asia/Tashkent)."""
    from apps.bot_settings.models import GlobalSettings
    from apps.campaigns.models import CampaignLog
    from apps.users.models import TelegramUser
    from tasks.notifications import send_templated_message_sync

    settings = GlobalSettings.get()
    today = timezone.localdate()

    # Skip anyone already congratulated today: a beat restart or a partial
    # failure re-running the task must not send the greeting twice.
    already_sent = set(
        CampaignLog.objects.filter(
            template__template_type="birthday_sale",
            success=True,
            sent_at__date=today,
        ).values_list("user_id", flat=True)
    )

    qs = TelegramUser.objects.filter(
        is_active=True,
        birth_date__day=today.day,
        birth_date__month=today.month,
    ).exclude(pk__in=already_sent)
    sent = 0
    for user in qs:
        context = {"user": user, "discount": settings.birthday_discount_percent}
        try:
            send_templated_message_sync(
                user.telegram_id, user.pk, "birthday_sale", context
            )
            sent += 1
        except Exception as exc:  # noqa: BLE001
            logger.exception("birthday send failed for user %s", user.pk)
            try:
                self.retry(exc=exc)
            except self.MaxRetriesExceededError:
                logger.error("birthday max retries exceeded for %s", user.pk)
    return sent


@shared_task
def purge_old_campaign_logs(days: int = 90) -> int:
    """
    Drop delivery logs older than `days`.

    Logs exist to answer "did this customer get the message?", which stops
    being a live question after a few months. Without this the table grows
    forever — ~30k rows/month at 10k customers.
    """
    from apps.campaigns.models import CampaignLog

    cutoff = timezone.now() - timedelta(days=days)
    deleted, _ = CampaignLog.objects.filter(sent_at__lt=cutoff).delete()
    logger.info("Purged %s campaign logs older than %s days", deleted, days)
    return deleted


@shared_task
def purge_old_progress_thumbnails(days: int = 180) -> int:
    """
    Delete thumbnails of old progress photos from disk.

    Nothing is lost: the full-size original lives on Telegram and stays
    reachable through `file_id`, so an old photo simply costs one API call
    to view instead of being served straight from our media directory.
    """
    from apps.analytics.models import ProgressPhoto

    cutoff = timezone.now() - timedelta(days=days)
    qs = ProgressPhoto.objects.filter(
        submitted_at__lt=cutoff, thumbnail_purged=False
    ).exclude(file_id="")

    purged = 0
    for photo in qs.iterator(chunk_size=200):
        if photo.thumbnail:
            photo.thumbnail.delete(save=False)
        photo.thumbnail_purged = True
        photo.save(update_fields=["thumbnail", "thumbnail_purged"])
        purged += 1
    logger.info("Purged %s progress thumbnails older than %s days", purged, days)
    return purged


@shared_task
def purge_old_admin_log(days: int = 90) -> int:
    """
    Trim Django's admin action log.

    It records every save/delete made in the CRM and nothing ever removes a
    row, so it grows for the life of the project. Recent entries answer "who
    changed this?"; year-old ones just cost disk.
    """
    from django.contrib.admin.models import LogEntry

    cutoff = timezone.now() - timedelta(days=days)
    deleted, _ = LogEntry.objects.filter(action_time__lt=cutoff).delete()
    logger.info("Purged %s admin log entries older than %s days", deleted, days)
    return deleted
