import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat

from config import BOT_TOKEN, ADMIN_IDS
from database import init_db
from config import get_all_admin_ids
from middlewares import AutoRegisterMiddleware
from handlers import (start, mining, shop, profile, inventory,
                       equipment, daily, leaderboard, help,
                       admin, market, bag, favorite_museum)
from handlers import vip
from handlers import transfer

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
    BotCommand(command="buyenergy",   description="⚡ Upgrade Max Energy (via Shop)"),
    BotCommand(command="buyslot",     description="🎒 Upgrade Slot Bag (via Shop)"),
    BotCommand(command="help",        description="❓ Panduan bermain"),
    BotCommand(command="vip",         description="👑 Cek status VIP"),
    BotCommand(command="transfer",    description="📦 Transfer ore ke pemain lain"),
    BotCommand(command="transferinfo", description="📊 Info sisa transfer minggu ini"),
    BotCommand(command="ores",        description="📖 Lihat semua ore per rarity"),
    BotCommand(command="rare_ore",    description="💎 Lihat ore rare & langka"),
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
    BotCommand(command="admin_resetall",        description="⚠️ Reset SEMUA data pemain"),
    BotCommand(command="admin_listadmin",       description="🛡️ Lihat daftar admin"),
    BotCommand(command="admin_addadmin",        description="➕ Tambah admin baru"),
    BotCommand(command="admin_removeadmin",     description="➖ Hapus admin dinamis"),
    BotCommand(command="admin_setorephoto",     description="📸 Pasang foto ore"),
    BotCommand(command="admin_listorephoto",    description="📸 Daftar foto ore"),
    BotCommand(command="admin_delorephoto",     description="📸 Hapus foto ore"),
    BotCommand(command="admin_givevip",         description="👑 Beri VIP ke user"),
    BotCommand(command="admin_revokevip",       description="👑 Cabut VIP dari user"),
    BotCommand(command="admin_tools",           description="🔧 Daftar tool_id"),
    BotCommand(command="admin_items",           description="🎒 Daftar item_id"),
    BotCommand(command="admin_zones",           description="🌍 Daftar zone_id"),
    BotCommand(command="admin_ores",            description="🪨 Daftar ore_id"),
]


async def set_bot_commands(bot: Bot):
    await bot.set_my_commands(PLAYER_COMMANDS, scope=BotCommandScopeDefault())
    # Gabungkan admin statis dan dinamis agar semua admin dapat extra commands
    all_admin_ids = await get_all_admin_ids()
    for admin_id in all_admin_ids:
        try:
            await bot.set_my_commands(
                PLAYER_COMMANDS + ADMIN_EXTRA_COMMANDS,
                scope=BotCommandScopeChat(chat_id=admin_id)
            )
        except Exception as e:
            logger.warning(f"Gagal set commands untuk admin {admin_id}: {e}")


async def main():
    # Inisialisasi database
    await init_db()
    await get_all_admin_ids()
    logger.info("✅ Database initialized")

    bot = Bot(token=BOT_TOKEN)
    # MemoryStorage: FSM state hilang saat bot restart (normal untuk bot Telegram)
    # Untuk production skala besar, pertimbangkan RedisStorage
    dp = Dispatcher(storage=MemoryStorage())

    # Middleware auto-register user
    dp.message.middleware(AutoRegisterMiddleware())
    dp.callback_query.middleware(AutoRegisterMiddleware())

    # Register semua router (urutan penting - router lebih spesifik duluan)
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
    dp.include_router(vip.router)
    dp.include_router(transfer.router)

    try:
        await set_bot_commands(bot)
        logger.info("✅ Bot commands set")
    except Exception as e:
        logger.warning(f"Gagal set bot commands: {e}")

    logger.info("🤖 Mining Bot starting...")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()
        logger.info("👋 Bot stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot dihentikan oleh pengguna")
    except ValueError as e:
        # Konfigurasi tidak lengkap (BOT_TOKEN / ADMIN_IDS kosong)
        logger.critical(f"❌ Konfigurasi error: {e}")
        logger.critical("Pastikan file .env sudah diisi dengan benar!")
        exit(1)
