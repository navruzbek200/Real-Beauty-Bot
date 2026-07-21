from __future__ import annotations

import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from core.telegram import TelegramError

logger = logging.getLogger(__name__)

# A purchase this much older than the campaign delay predates the customer
# linking their Telegram (staff enter purchases before the customer ever opens
# the bot). Greeting them with "it's been a week — how is it going?" months
# later reads as a broken bot, so such rows are marked done without sending.
_STALE_GRACE_DAYS = 30


def _mark(up, week: int) -> None:
    field = "week1_sent" if week == 1 else "week2_sent"
    setattr(up, field, True)
    up.save(update_fields=[field])


def _send_checkin_batch(week: int) -> int:
    """
    Shared engine for the week-1/week-2 check-ins.

    Every recipient is handled independently: one dead chat (customer blocked
    the bot, deleted Telegram…) must not abort the rest of the batch — the
    first version called self.retry() inside the loop, which raised out of it
    and starved everyone queued after the failing row, every single day.
    """
    from apps.bot_settings.models import GlobalSettings
    from apps.users.models import UserProduct
    from bot.keyboards.inline import CB_SEND_PROGRESS, CB_SUBMIT_FEEDBACK, SEP
    from tasks.notifications import send_templated_message_sync

    settings = GlobalSettings.get()
    delay_days = settings.week1_delay_days if week == 1 else settings.week2_delay_days
    template_type = "week1_checkin" if week == 1 else "week2_progress"
    sent_flag = "week1_sent" if week == 1 else "week2_sent"

    now = timezone.now()
    cutoff = now - timedelta(days=delay_days)
    stale_cutoff = now - timedelta(days=delay_days + _STALE_GRACE_DAYS)

    qs = UserProduct.objects.select_related("user", "product").filter(
        purchased_at__lte=cutoff,
        # Only customers the bot can actually reach; unlinked cards used to
        # produce a guaranteed-failing send that blocked the whole batch.
        user__telegram_id__isnull=False,
        user__is_active=True,
        **{sent_flag: False},
    )

    sent = 0
    for up in qs:
        if up.purchased_at < stale_cutoff:
            _mark(up, week)
            continue

        if week == 1:
            label = settings.feedback_button_label
            callback = f"{CB_SUBMIT_FEEDBACK}{SEP}1{SEP}{up.product_id}"
        else:
            label = settings.before_after_button_label
            callback = f"{CB_SEND_PROGRESS}{SEP}{up.product_id}"
        keyboard = {
            "inline_keyboard": [[{"text": label, "callback_data": callback}]]
        }
        context = {"user": up.user, "product": up.product, "week": week}

        try:
            send_templated_message_sync(
                up.user.telegram_id, up.user_id, template_type, context, keyboard
            )
        except TelegramError as exc:
            # Permanent failures (blocked bot, deleted account) are marked done
            # so they stop being retried forever; transient ones stay unsent
            # and tomorrow's run picks them up again.
            if exc.is_permanent:
                _mark(up, week)
            continue
        except Exception:  # noqa: BLE001
            logger.exception("week%s send crashed for user_product %s", week, up.pk)
            continue
        _mark(up, week)
        sent += 1
    return sent


@shared_task
def send_week1_checkins() -> int:
    """Send week-1 check-in to eligible purchases. Returns count sent."""
    return _send_checkin_batch(week=1)


@shared_task
def send_week2_progress() -> int:
    """Send week-2 progress request to eligible purchases. Returns count sent."""
    return _send_checkin_batch(week=2)


@shared_task
def send_birthday_messages() -> int:
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
        telegram_id__isnull=False,
        birth_date__day=today.day,
        birth_date__month=today.month,
    ).exclude(pk__in=already_sent)

    sent = 0
    for user in qs:
        context = {"user": user, "discount": settings.birthday_discount_percent}
        try:
            if send_templated_message_sync(
                user.telegram_id, user.pk, "birthday_sale", context
            ):
                sent += 1
        except TelegramError:
            continue  # logged by the sender; nothing more to do for this user
        except Exception:  # noqa: BLE001
            logger.exception("birthday send crashed for user %s", user.pk)
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
