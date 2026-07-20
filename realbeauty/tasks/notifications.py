from __future__ import annotations

import asyncio
import logging
from typing import Any

from aiogram.types import InlineKeyboardMarkup
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)


def _fresh_bot():
    """A Bot bound to the current asyncio.run() loop; caller closes its session."""
    import os

    from aiogram import Bot
    from aiogram.client.default import DefaultBotProperties
    from aiogram.enums import ParseMode

    return Bot(
        token=os.environ["BOT_TOKEN"],
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


@sync_to_async
def _render(template_type: str, context: dict[str, Any]) -> tuple[Any, str, str]:
    """Load active template + render. Returns (template_obj, text, parse_mode)."""
    from apps.campaigns.models import MessageTemplate

    template = MessageTemplate.objects.filter(
        template_type=template_type, is_active=True
    ).first()
    if template is None:
        return (None, "", "HTML")
    return (template, template.render(context), template.parse_mode)


@sync_to_async
def _log(user_id: int, template_obj: Any, success: bool, error: str = "") -> None:
    from apps.campaigns.models import CampaignLog

    CampaignLog.objects.create(
        user_id=user_id,
        template=template_obj,
        success=success,
        error_detail=error,
    )


async def _send_templated_message(
    telegram_id: int,
    user_id: int,
    template_type: str,
    context: dict[str, Any],
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    """Core async sender. Called from sync Celery task via asyncio.run()."""
    template_obj, text, parse_mode = await _render(template_type, context)
    # A fresh Bot owned by this asyncio.run() loop, closed after — the shared
    # polling singleton would leak an aiohttp session per scheduled send in the
    # Celery worker.
    bot = _fresh_bot()
    try:
        if text:
            await bot.send_message(
                chat_id=telegram_id,
                text=text,
                parse_mode=parse_mode,
                reply_markup=reply_markup,
            )
        await _log(user_id, template_obj, success=True)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to send %s to %s", template_type, telegram_id)
        await _log(user_id, template_obj, success=False, error=str(exc))
        raise
    finally:
        await bot.session.close()


def send_templated_message_sync(
    telegram_id: int,
    user_id: int,
    template_type: str,
    context: dict[str, Any],
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    """Sync entry point for Celery tasks."""
    asyncio.run(
        _send_templated_message(
            telegram_id, user_id, template_type, context, reply_markup
        )
    )
