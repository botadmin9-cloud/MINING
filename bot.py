import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database import init_db
from handlers import (start, mining, shop, profile, inventory,
                       equipment, daily, leaderboard, help,
                       admin, market)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    await init_db()
    logger.info("✅ Database initialized")

    bot = Bot(token=BOT_TOKEN)
    dp  = Dispatcher(storage=MemoryStorage())

    # Register all routers
    dp.include_router(start.router)
    dp.include_router(mining.router)
    dp.include_router(shop.router)
    dp.include_router(profile.router)
    dp.include_router(inventory.router)
    dp.include_router(equipment.router)
    dp.include_router(daily.router)
    dp.include_router(leaderboard.router)
    dp.include_router(help.router)
    dp.include_router(admin.router)
    dp.include_router(market.router)

    logger.info("🤖 Mining Bot v2 starting...")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
