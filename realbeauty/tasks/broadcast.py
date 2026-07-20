from __future__ import annotations

import asyncio
import logging

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)

# Telegram allows ~30 messages/second to distinct users before it starts
# replying 429. Staying at 20/s leaves headroom and still clears 10k users in
# under nine minutes.
_PER_SECOND = 20
_DELAY = 1.0 / _PER_SECOND


async def _deliver_one(bot, chat_id: int, text: str, photo_path: str | None):
    """Send one broadcast message. Returns (ok, error_str)."""
    from aiogram.exceptions import TelegramRetryAfter
    from aiogram.types import FSInputFile

    try:
        if photo_path:
            await bot.send_photo(
                chat_id=chat_id,
                photo=FSInputFile(photo_path),
                caption=text or None,
                parse_mode="HTML",
            )
        else:
            await bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML")
        return True, ""
    except TelegramRetryAfter as exc:
        # Flood limit hit — wait exactly as long as Telegram asks, then retry
        # this one recipient so nobody is silently skipped.
        await asyncio.sleep(exc.retry_after + 1)
        return await _deliver_one(bot, chat_id, text, photo_path)
    except Exception as exc:  # noqa: BLE001 — blocked bot, deleted account, etc.
        return False, str(exc)


def _fresh_bot():
    """
    A Bot for one task run, owned by this event loop.

    The polling process's shared get_bot() singleton binds its aiohttp session
    to that process's loop; reusing it from asyncio.run() here would leak a
    session per call in the Celery worker. A local Bot we close in `finally`
    does not.
    """
    import os

    from aiogram import Bot
    from aiogram.client.default import DefaultBotProperties
    from aiogram.enums import ParseMode

    return Bot(
        token=os.environ["BOT_TOKEN"],
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


async def _run(broadcast_id: int) -> None:
    from asgiref.sync import sync_to_async

    from apps.campaigns.models import Broadcast, CampaignLog

    broadcast = await sync_to_async(Broadcast.objects.get)(pk=broadcast_id)

    recipients = await sync_to_async(
        lambda: list(broadcast.recipients().values_list("pk", "telegram_id"))
    )()
    photo_path = await sync_to_async(
        lambda: broadcast.photo.path if broadcast.photo else None
    )()

    bot = _fresh_bot()
    sent = failed = 0
    fail_logs: list[CampaignLog] = []

    try:
        for user_pk, chat_id in recipients:
            ok, error = await _deliver_one(bot, chat_id, broadcast.body, photo_path)
            if ok:
                sent += 1
            else:
                failed += 1
                # Log only failures: a full per-recipient log of a 10k blast
                # would bury the table, but "who didn't get it and why" is
                # worth keeping.
                fail_logs.append(
                    CampaignLog(user_id=user_pk, template=None, success=False,
                                error_detail=error[:500])
                )
            await asyncio.sleep(_DELAY)
    finally:
        await bot.session.close()

    if fail_logs:
        await sync_to_async(CampaignLog.objects.bulk_create)(fail_logs)

    def _finalize() -> None:
        broadcast.sent_count = sent
        broadcast.failed_count = failed
        broadcast.status = Broadcast.Status.SENT
        broadcast.finished_at = timezone.now()
        broadcast.save(
            update_fields=["sent_count", "failed_count", "status", "finished_at"]
        )

    await sync_to_async(_finalize)()
    logger.info("Broadcast %s done: %s sent, %s failed", broadcast_id, sent, failed)


def send_test(broadcast_id: int, chat_id: int) -> tuple[bool, str]:
    """
    Send a broadcast to a single chat (the admin previewing it).

    Runs synchronously — the admin clicks "test" and wants to see the result —
    through the exact same delivery path as the real blast, so the preview is
    faithful.
    """
    from apps.campaigns.models import Broadcast

    broadcast = Broadcast.objects.get(pk=broadcast_id)
    photo_path = broadcast.photo.path if broadcast.photo else None

    async def _once() -> tuple[bool, str]:
        bot = _fresh_bot()
        try:
            return await _deliver_one(bot, chat_id, broadcast.body, photo_path)
        finally:
            await bot.session.close()

    return asyncio.run(_once())


@shared_task
def send_broadcast(broadcast_id: int) -> None:
    """
    Deliver a broadcast to its audience.

    Marks the row SENDING up front so a second click cannot start it twice,
    then runs the whole blast inside one event loop (one Bot HTTP session for
    all recipients, not one per message).
    """
    from apps.campaigns.models import Broadcast

    updated = Broadcast.objects.filter(
        pk=broadcast_id, status__in=[Broadcast.Status.DRAFT, Broadcast.Status.FAILED]
    ).update(status=Broadcast.Status.SENDING, started_at=timezone.now())
    if not updated:
        logger.warning("Broadcast %s already sending/sent — skipped", broadcast_id)
        return

    try:
        asyncio.run(_run(broadcast_id))
    except Exception:  # noqa: BLE001
        logger.exception("Broadcast %s crashed", broadcast_id)
        Broadcast.objects.filter(pk=broadcast_id).update(
            status=Broadcast.Status.FAILED
        )
        raise
