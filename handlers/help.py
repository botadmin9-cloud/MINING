"""
❓ Help Handler v2 — Tanpa referral, dengan info market & ore inventory
"""
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from keyboards import back_main_kb
from config import ENERGY_COOLDOWN_MINUTES, MAX_LEVEL

router = Router()


@router.message(F.text == "❓ Bantuan")
@router.message(Command("help"))
async def show_help(message: Message):
    text = (
        "❓ *Panduan Mining Bot v2*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"

        "⛏️ *CARA MINING:*\n"
        "1. Tekan menu *⛏️ Mining*\n"
        "2. Pilih *Mine!*, *Mine x5*, atau *Mine x10*\n"
        "3. Tiap mining menghabiskan ⚡ Energy\n"
        f"4. Energy regen 1 per {ENERGY_COOLDOWN_MINUTES} menit\n"
        "5. Ada *cooldown antar mine* tergantung alat yang dipakai\n"
        "   • Alat murah = cooldown lama\n"
        "   • Alat mahal = cooldown cepat (min 5 detik)\n\n"

        "🪨 *ORE & KETERANGAN:*\n"
        "• Setiap ore yang ditemukan dilengkapi keterangan\n"
        "• Ore tersimpan di *Ore Inventory* (cek di Profil)\n"
        "• Ore bisa dijual di *🛒 Market*!\n\n"

        "🎒 *PERALATAN (Equipment):*\n"
        "• Lihat & ganti alat di *🎒 Equipment*\n"
        "• Beli alat baru di *🏪 Shop → Alat Mining*\n"
        "• Ada 7 Tier: Starter → Mythical\n"
        "• Alat Legendary+ butuh ore khusus untuk dibeli!\n\n"

        "🌍 *ZONA MINING (10 Zona):*\n"
        "• Buka zona baru di *Shop → Buka Zona*\n"
        "• Zona makin dalam = ore makin berharga!\n"
        "• Dari Permukaan → Retakan Waktu (Level 150)\n\n"

        "🛒 *MARKET ORE:*\n"
        "• Jual ore ke pemain lain di *🛒 Market*\n"
        "• Tentukan harga sendiri!\n"
        "• Fee listing 5% dari total harga\n"
        "• Pembeli dan penjual ternotifikasi beserta ID\n\n"

        "🎁 *INVENTARIS & ITEM:*\n"
        "• Beli item di *Shop → Item*\n"
        "• Gunakan di *🎁 Inventaris*\n"
        "• ⚡ Energy Potion, 🍀 Luck Elixir, 💰 Double Coin, dll\n\n"

        "⭐ *LEVEL & XP:*\n"
        "• Mining menghasilkan XP dan naik level\n"
        f"• Level maksimal: *{MAX_LEVEL}*\n"
        "• Level naik = unlock alat & zona baru\n\n"

        "🔄 *REBIRTH SYSTEM:*\n"
        f"• Rebirth hanya tersedia di Level *{MAX_LEVEL}*\n"
        "• Reset level ke 1 tapi dapat +50% permanent coin!\n"
        "• Beli *Rebirth Token* di Shop\n\n"

        "🎁 *DAILY BONUS:*\n"
        "• Klaim tiap 24 jam via *🎁 Daily*\n"
        "• Streak berturut = multiplier bonus!\n"
        "• Energy langsung penuh saat klaim\n\n"

        "🏅 *PRESTASI:*\n"
        "Ada 20+ prestasi dengan hadiah koin!\n"
        "Cek di *👤 Profil → Prestasi*"
    )
    await message.answer(text, reply_markup=back_main_kb(), parse_mode="Markdown")
