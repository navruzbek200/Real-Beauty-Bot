from __future__ import annotations

import asyncio
import logging
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.prod")
django.setup()

from aiogram import Bot, Dispatcher  # noqa: E402
from aiogram.client.default import DefaultBotProperties  # noqa: E402
from aiogram.enums import ParseMode  # noqa: E402
from aiogram.fsm.storage.redis import RedisStorage  # noqa: E402

from aiogram.types import BotCommand  # noqa: E402

from bot.handlers import (  # noqa: E402
    auth,
    birthday,
    fallback,
    feedback,
    menu,
    products,
    progress,
    support,
)
from bot.middlewares.active_user import ActiveUserMiddleware  # noqa: E402
from bot.middlewares.db import DBSessionMiddleware  # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_bot: Bot | None = None


def get_bot() -> Bot:
    global _bot
    if _bot is None:
        _bot = Bot(
            token=os.environ["BOT_TOKEN"],
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
    return _bot


async def main() -> None:
    bot = get_bot()
    storage = RedisStorage.from_url(os.environ["REDIS_URL"])
    dp = Dispatcher(storage=storage)

    # DB session hygiene around every update, then the block check — which
    # needs a live connection, so it has to come second.
    dp.update.middleware(DBSessionMiddleware())
    dp.update.middleware(ActiveUserMiddleware())

    dp.include_router(auth.router)
    dp.include_router(menu.router)
    dp.include_router(products.router)
    dp.include_router(feedback.router)
    dp.include_router(progress.router)
    dp.include_router(support.router)
    dp.include_router(birthday.router)
    # Last on purpose: answers whatever nothing above matched.
    dp.include_router(fallback.router)

    # The ☰ command menu next to the input field — without it the only way to
    # rediscover /menu after hiding the keyboard is remembering it.
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Botni ishga tushirish"),
            BotCommand(command="menu", description="Asosiy menyu"),
            BotCommand(command="help", description="Yordam"),
        ]
    )

    logger.info("Starting Real Beauty bot polling…")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
