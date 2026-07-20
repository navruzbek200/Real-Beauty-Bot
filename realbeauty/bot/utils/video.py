from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from aiogram.types import FSInputFile

from bot import texts
from bot.services import product_service

if TYPE_CHECKING:
    from apps.products.models import ProductTutorialStep

logger = logging.getLogger(__name__)


async def send_protected_video(
    bot: Bot, chat_id: int, step: "ProductTutorialStep"
) -> None:
    """
    Send a tutorial step: intro text, then its protected video.

    protect_content=True prevents forwarding AND disables the "Save to
    Downloads" button. Source resolution:
      1. cached Telegram file_id  → send by id (fast, no re-upload)
      2. uploaded local file      → send file, then cache the returned file_id
      3. nothing                  → "coming soon" placeholder
    """
    try:
        await bot.send_message(chat_id=chat_id, text=step.intro_text, parse_mode="HTML")

        if step.video_file_id:
            await bot.send_video(
                chat_id=chat_id,
                video=step.video_file_id,
                caption=step.button_label,
                protect_content=step.protect_content,
            )
        elif step.video_file and step.video_file.name:
            sent = await bot.send_video(
                chat_id=chat_id,
                video=FSInputFile(step.video_file.path),
                caption=step.button_label,
                protect_content=step.protect_content,
            )
            if sent.video:
                await product_service.cache_video_file_id(step.pk, sent.video.file_id)
        else:
            await bot.send_message(chat_id=chat_id, text=texts.VIDEO_COMING_SOON)
    except TelegramAPIError:
        logger.exception("Failed to send protected video to %s", chat_id)
    except Exception:  # noqa: BLE001
        logger.exception("Unexpected error sending protected video to %s", chat_id)
