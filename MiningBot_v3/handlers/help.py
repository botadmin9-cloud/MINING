from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from keyboards import back_main_kb
from config import ENERGY_COOLDOWN_MINUTES, MAX_LEVEL, BAG_SLOT_DEFAULT, BAG_SLOT_MAX, ENERGY_UPGRADE_MAX

router = Router()

@router.message(F.text == "❓ Bantuan")
@router.message(Command("help"))
async def show_help(message: Message):
    text = (
        "❓ *Panduan Mining Bot v3*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"

        "⛏️ *CARA MINING:*\n"
        "• Tekan *⛏️ Mining* → Mine!, x5, atau x10\n"
        "• Tiap mine pakai ⚡ Energy\n"
        f"• Energy regen 1 per {ENERGY_COOLDOWN_MINUTES} menit\n"
        "• Cooldown antar mine tergantung alat (murah=lama, mahal=cepat)\n\n"

        "🎒 *BAG (Kantong Ore):*\n"
        f"• Default: `{BAG_SLOT_DEFAULT}` slot, maks `{BAG_SLOT_MAX}` slot\n"
        "• Ketik `/bag` untuk lihat semua ore kamu\n"
        "• Tombol *Jual 1* / *Jual Semua* / *Jual SEMUA Ore* tersedia\n"
        "• Klik nama ore untuk detail + foto (jika ada)\n\n"

        "⚡ *UPGRADE ENERGY & SLOT:*\n"
        f"• `/buyenergy` — Tambah max energy (+100, maks {ENERGY_UPGRADE_MAX})\n"
        "• `/energyinfo` — Cek harga upgrade energy\n"
        f"• `/buyslot` — Tambah slot bag (+10, maks {BAG_SLOT_MAX})\n"
        "• `/slotinfo` — Cek harga upgrade slot\n"
        "• Harga naik setiap kali upgrade!\n\n"

        "⭐ *FAVORIT (maks 150):*\n"
        "• Tandai ore favorit via `/bag` → detail ore\n"
        "• Lihat semua favorit: *⭐ Favorit* atau `/fav`\n\n"

        "🏛️ *MUSEUM (maks 30):*\n"
        "• Simpan ore langka sebagai koleksi di museum\n"
        "• Lihat foto ore langka yang dipasang admin\n"
        "• Buka via *🏛️ Museum* atau `/museum`\n\n"

        "🛒 *MARKET ORE:*\n"
        "• Jual ore ke pemain lain, harga bebas\n"
        "• Fee 5% dari total harga jual\n"
        "• Notifikasi beserta ID Telegram ke kedua pihak\n\n"

        "🔄 *REBIRTH:*\n"
        f"• Hanya di Level {MAX_LEVEL} (level maks)\n"
        "• Reset level → 1, dapat +50% permanent coin\n"
        "• Beli *Rebirth Token* di Shop\n\n"

        "🏅 *PRESTASI:*\n"
        "20+ prestasi! Cek di *👤 Profil → Prestasi*\n\n"

        "📋 *PERINTAH CEPAT:*\n"
        "`/bag` `/buyenergy` `/buyslot`\n"
        "`/favorite` `/museum` `/shop` `/daily`"
    )
    await message.answer(text, reply_markup=back_main_kb(), parse_mode="Markdown")
