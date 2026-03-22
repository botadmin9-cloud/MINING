from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from keyboards import main_menu_kb
from middlewares import register_message_owner

router = Router()

HELP_TEXT = (
    "<b>❓ BANTUAN — MiningBot v6 ULTIMATE</b>\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "<b>🎮 CARA BERMAIN:</b>\n"
    "1️⃣ Mining ore → masuk ke Bag\n"
    "2️⃣ Jual ore di Bag atau Market\n"
    "3️⃣ Gunakan koin untuk beli alat &amp; item\n"
    "4️⃣ Level up untuk XP &amp; koin lebih banyak!\n\n"
    "<b>💰 SISTEM KOIN:</b>\n"
    "• Koin didapat dengan MENJUAL ore di Bag atau Market\n"
    "• Critical hit = ore lebih berat (harga jual lebih tinggi)\n"
    "• Lucky = ore sedikit lebih berat\n\n"
    "<b>⚖️ SISTEM KG &amp; JUAL:</b>\n"
    "• Setiap ore punya berat (kg) yang berbeda\n"
    "• Harga jual = nilai × berat_kg × 0.02\n"
    "• Alat lebih canggih = ore lebih berat!\n\n"
    "<b>⭐ SISTEM XP:</b>\n"
    "• Mining memberikan XP setiap kali\n"
    "• Critical hit = XP 2x | Lucky = XP 1.5x\n\n"
    "<b>⛏️ MINING:</b>\n"
    "• Cooldown dasar: 6 detik (tier 1)\n"
    "• Alat makin canggih = cooldown makin cepat\n"
    "• Mode mining: x1 / x5 / x10 / x25 / x50\n\n"
    "<b>📦 TRANSFER ORE:</b>\n"
    "• Kirim ore ke pemain lain dengan /transfer\n"
    "• Maks 3x kirim &amp; 3x terima per minggu\n\n"
    "<b>👑 SISTEM VIP:</b>\n"
    "• Cooldown mining lebih cepat 15%\n"
    "• Energy recovery lebih cepat\n"
    "• Luck +3% | Critical +2%\n"
    "• Beli VIP di: 🏪 Shop → 👑 VIP Member\n\n"
    "<b>⚡ PERINTAH UTAMA:</b>\n"
    "/mine — Buka panel mining\n"
    "/bag — Lihat &amp; jual ore\n"
    "/shop — Beli alat, item, zona baru\n"
    "/inventory — Pakai item consumable\n"
    "/profile — Lihat statistik kamu\n"
    "/daily — Ambil bonus harian\n"
    "/market — Jual beli ore antar pemain\n"
    "/transfer — Transfer ore ke pemain lain\n"
    "/ores — 📖 Daftar semua ore per rarity (COMMON, UNCOMMON, dll)\n"
    "/ores [tier] — Filter satu tier, contoh: /ores epic\n"
    "/leaderboard — Papan peringkat\n"
    "/vip — Cek status VIP kamu\n\n"
    "<b>⬆️ UPGRADE (BAG &amp; ENERGY):</b>\n"
    "/shop → Upgrade → Beli slot bag atau tambah max energy\n"
    "• Slot Bag: +10 slot per upgrade (harga naik tiap kali)\n"
    "• Max Energy: +100 per upgrade (harga naik tiap kali)\n\n"
    "<b>💡 TIPS:</b>\n"
    "• Zona lebih dalam = ore lebih langka &amp; mahal\n"
    "• Daily streak memberikan bonus berlipat\n"
    "• Alat tier 6+ perlu ore untuk dibeli (maks 5 ore)\n"
    "• VIP = cara terbaik farming lebih efisien\n\n"
    "<b>🌍 ZONA:</b> 20 zona dari Permukaan hingga Alam Genesis\n"
    "<b>⛏️ ALAT:</b> 48 alat dari Tier 1 Starter hingga Tier 8 Divine\n"
    "<b>🪨 ORE:</b> 113 jenis ore dari Kerikil hingga Permata Tak Terbatas\n"
    "<b>🎒 ITEM:</b> 10 item: potion energy, buff XP/speed/luck, mystery box &amp; rebirth token!"
)


@router.message(F.text == "❓ Bantuan")
@router.message(Command("help"))
async def show_help(message: Message):
    _sent = await message.answer(HELP_TEXT, parse_mode="HTML", reply_markup=main_menu_kb())
    if _sent: register_message_owner(_sent.chat.id, _sent.message_id, message.from_user.id)
