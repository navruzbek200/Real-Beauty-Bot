from __future__ import annotations

import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from core.telegram import TelegramError, send_message

logger = logging.getLogger(__name__)


def _due_purchases(rule, window):
    """(anchor key, user, product) for purchases inside this rule's window."""
    from apps.users.models import UserProduct

    oldest, newest = window
    qs = UserProduct.objects.select_related("user", "product").filter(
        purchased_at__lte=newest,
        purchased_at__gte=oldest,
        # Only customers the bot can actually reach; unlinked cards used to
        # produce a guaranteed-failing send that blocked the whole batch.
        user__telegram_id__isnull=False,
        user__is_active=True,
    )
    if rule.is_test_mode:
        qs = qs.filter(user_id=rule.test_user_id) if rule.test_user_id else qs.none()
    return [(f"up:{up.pk}", up.user, up.product) for up in qs]


def _due_registrations(rule, window):
    from apps.users.models import TelegramUser

    oldest, newest = window
    qs = TelegramUser.objects.filter(
        registered_at__lte=newest,
        registered_at__gte=oldest,
        telegram_id__isnull=False,
        is_active=True,
    )
    if rule.is_test_mode:
        qs = qs.filter(pk=rule.test_user_id) if rule.test_user_id else qs.none()
    return [(f"user:{user.pk}", user, None) for user in qs]


_ANCHORS = {
    "after_purchase": _due_purchases,
    "after_registration": _due_registrations,
}


def _dispatch_rule(rule) -> int:
    """
    Send one auto-message to everyone it has come due for.

    The candidate window has a floor as well as a ceiling. Without the floor
    this task would re-read every purchase ever made, once a minute, forever —
    and on the day a new rule is created it would greet customers who bought
    two years ago with "how was your first week?". `stale_grace` past the delay
    is where a message stops being welcome and starts reading as a broken bot.

    Every recipient is handled independently: one dead chat (customer blocked
    the bot, deleted Telegram…) must not abort the rest of the batch — an
    earlier version raised out of the loop and starved everyone queued behind
    the failing row, every single day.
    """
    from apps.campaigns.models import AutoMessageLog

    now = timezone.now()
    newest = now - rule.delay
    window = (newest - rule.stale_grace, newest)

    candidates = _ANCHORS[rule.trigger](rule, window)
    if not candidates:
        return 0

    already = set(
        AutoMessageLog.objects.filter(
            auto_message=rule, anchor__in=[anchor for anchor, _u, _p in candidates]
        ).values_list("anchor", flat=True)
    )

    sent = 0
    for anchor, user, product in candidates:
        if anchor in already:
            continue

        lang = user.language
        text = rule.render({"user": user, "product": product}, lang)
        if not text.strip():
            continue
        keyboard = rule.keyboard_for(lang, product.pk if product else None)

        try:
            send_message(
                user.telegram_id, text, parse_mode="HTML", reply_markup=keyboard
            )
        except TelegramError as exc:
            # Permanent failures (blocked bot, deleted account) are logged as
            # done so they stop being retried forever; transient ones are left
            # alone and the next run picks them up again.
            if exc.is_permanent:
                AutoMessageLog.objects.get_or_create(
                    auto_message=rule,
                    anchor=anchor,
                    defaults={
                        "user": user,
                        "success": False,
                        "error_detail": str(exc)[:500],
                    },
                )
            continue
        except Exception:  # noqa: BLE001
            logger.exception("auto-message %s crashed on %s", rule.pk, anchor)
            continue

        AutoMessageLog.objects.get_or_create(
            auto_message=rule, anchor=anchor, defaults={"user": user}
        )
        sent += 1
    return sent


@shared_task
def dispatch_auto_messages() -> int:
    """
    Fire every automatic message that has come due. Returns the count sent.

    Runs once a minute rather than once a day: the delay is admin-editable
    down to a single minute, and a daily beat would silently turn "1 daqiqa"
    into "tomorrow at 10:00" — which is exactly what makes a campaign
    impossible to test.
    """
    from apps.campaigns.models import AutoMessage

    total = 0
    for rule in AutoMessage.objects.filter(is_active=True).select_related("test_user"):
        try:
            total += _dispatch_rule(rule)
        except Exception:  # noqa: BLE001 — one bad rule must not stop the rest
            logger.exception("auto-message rule %s failed", rule.pk)
    return total


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
            delivered = send_templated_message_sync(
                user.telegram_id, user.pk, "birthday_sale", context, lang=user.language
            )
        except TelegramError:
            delivered = False  # logged by the sender
        except Exception:  # noqa: BLE001
            logger.exception("birthday send crashed for user %s", user.pk)
            delivered = False
        if not delivered:
            # Blocked the bot, deleted their account, or the send otherwise
            # failed — nobody actually saw a birthday greeting, so there is
            # nothing to reward. Next year's run tries again from scratch.
            continue
        sent += 1
        _credit_birthday_points(user, today)
    return sent


def _credit_birthday_points(user, today) -> None:
    """
    The birthday bonus, once a year — only for a greeting that actually landed.

    Keyed on the year so a beat restart cannot pay twice.
    """
    from apps.loyalty.models import PointsTransaction
    from apps.loyalty.services import award

    try:
        award(
            user,
            PointsTransaction.Reason.BIRTHDAY,
            reference=f"birthday:{today.year}",
        )
    except Exception:  # noqa: BLE001
        logger.exception("birthday points failed for user %s", user.pk)


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
