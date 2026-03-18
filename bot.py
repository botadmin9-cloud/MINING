import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat

from config import BOT_TOKEN, ADMIN_IDS
from database import init_db
from handlers import (start, mining, shop, profile, inventory,
                       equipment, daily, leaderboard, help,
                       admin, market, bag, favorite_museum)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

PLAYER_COMMANDS = [
    BotCommand(command="start",       description="🏠 Menu utama"),
    BotCommand(command="mine",        description="⛏️ Mining"),
    BotCommand(command="bag",         description="🎒 Lihat & kelola ore"),
    BotCommand(command="profile",     description="👤 Profil kamu"),
    BotCommand(command="setname",     description="✏️ Ganti nama game"),
    BotCommand(command="shop",        description="🏪 Toko alat & item"),
    BotCommand(command="inventory",   description="🎁 Inventaris item"),
    BotCommand(command="equipment",   description="🔧 Peralatan"),
    BotCommand(command="market",      description="🛒 Market jual beli ore"),
    BotCommand(command="daily",       description="🎁 Bonus harian"),
    BotCommand(command="leaderboard", description="🏆 Papan peringkat"),
    BotCommand(command="favorite",    description="⭐ Ore favorit"),
    BotCommand(command="museum",      description="🏛️ Museum ore langka"),
    BotCommand(command="buyenergy",   description="⚡ Beli tambahan max energy"),
    BotCommand(command="buyslot",     description="🎒 Beli tambahan slot bag"),
    BotCommand(command="energyinfo",  description="⚡ Info harga upgrade energy"),
    BotCommand(command="slotinfo",    description="🎒 Info harga upgrade slot"),
    BotCommand(command="help",        description="❓ Panduan bermain"),
]

ADMIN_EXTRA_COMMANDS = [
    BotCommand(command="adminhelp",             description="🔐 Panel admin"),
    BotCommand(command="admin_stats",           description="📊 Statistik bot"),
    BotCommand(command="admin_users",           description="👥 Daftar user"),
    BotCommand(command="admin_broadcast",       description="📢 Broadcast pesan"),
    BotCommand(command="admin_info",            description="👤 Info user"),
    BotCommand(command="admin_addcoin",         description="💰 Tambah koin user"),
    BotCommand(command="admin_setlevel",        description="⭐ Set level user"),
    BotCommand(command="admin_setenergy",       description="⚡ Set energy user"),
    BotCommand(command="admin_givetool",        description="🔧 Beri alat ke user"),
    BotCommand(command="admin_giveitem",        description="🎁 Beri item ke user"),
    BotCommand(command="admin_giveore",         description="🪨 Beri ore ke user"),
    BotCommand(command="admin_givezone",        description="🌍 Buka zona untuk user"),
    BotCommand(command="admin_reset",           description="🔄 Reset data user"),
    BotCommand(command="admin_setphoto",        description="📸 Upload foto admin"),
    BotCommand(command="admin_myphotos",        description="📸 Lihat foto admin"),
    BotCommand(command="admin_setorephoto",     description="📸 Pasang foto ore"),
    BotCommand(command="admin_listorephoto",    description="📸 Daftar foto ore"),
    BotCommand(command="admin_delorephoto",     description="📸 Hapus foto ore"),
    BotCommand(command="admin_tools",           description="🔧 Daftar tool_id"),
    BotCommand(command="admin_items",           description="🎒 Daftar item_id"),
    BotCommand(command="admin_zones",           description="🌍 Daftar zone_id"),
    BotCommand(command="admin_ores",            description="🪨 Daftar ore_id"),
    BotCommand(command="admin_deletephoto",     description="📸 Hapus foto admin"),
]


async def set_bot_commands(bot: Bot):
    await bot.set_my_commands(PLAYER_COMMANDS, scope=BotCommandScopeDefault())
    for admin_id in ADMIN_IDS:
        try:
            await bot.set_my_commands(
                PLAYER_COMMANDS + ADMIN_EXTRA_COMMANDS,
                scope=BotCommandScopeChat(chat_id=admin_id)
            )
        except Exception as e:
            logger.warning(f"Gagal set commands untuk admin {admin_id}: {e}")


async def main():
    await init_db()
    logger.info("✅ Database initialized (v5 FIXED)")

    bot = Bot(token=BOT_TOKEN)
    # ✅ MemoryStorage diperlukan untuk FSM (registrasi username & setname)
    dp  = Dispatcher(storage=MemoryStorage())

    # Register semua router
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
    dp.include_router(bag.router)
    dp.include_router(favorite_museum.router)

    await set_bot_commands(bot)
    logger.info("✅ Bot commands set")

    logger.info("🤖 Mining Bot v5 FIXED starting...")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
