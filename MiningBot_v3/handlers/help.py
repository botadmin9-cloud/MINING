from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from keyboards import main_menu_kb

router = Router()

HELP_TEXT = """
❓ *BANTUAN — MiningBot v6 ULTIMATE*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎮 *CARA BERMAIN:*
1️⃣ Mining ore → masuk ke Bag
2️⃣ Jual ore di Bag atau Market
3️⃣ Gunakan koin untuk beli alat & item
4️⃣ Level up untuk XP & koin lebih banyak!

⚖️ *SISTEM KG:*
• Setiap ore punya berat hingga *100.000 KG*
• Ore lebih berat = harga jual lebih tinggi
• Harga jual = nilai × berat_kg × 1.5
• Alat lebih canggih = ore lebih berat!

⭐ *SISTEM XP:*
• Mining memberikan XP (koin dari jual ore)
• Ore lebih berat = XP lebih banyak
• Critical hit = XP 2x + ore lebih berat
• Lucky = XP 1.5x + ore sedikit lebih berat

⛏️ *MINING:*
• Cooldown dasar: *6 detik* (tier 1)
• Alat makin canggih = cooldown makin cepat
• Mining: x1 / x5 / x10 / *x25* / *x50*
• Semua pemain bisa mining x5 hingga x50!

👑 *SISTEM VIP:*
• Cooldown mining lebih cepat 15%
• Energy recovery lebih cepat
• Luck +3% | Critical +2%
• Badge VIP di profil
• Beli VIP di: 🏪 Shop → 👑 VIP Member

💰 *TOP UP SALDO:*
• Beli koin dengan transfer bank
• Tersedia 6 paket dari Rp 10.000 – Rp 500.000
• Beli di: 🏪 Shop → 💰 Top Up Saldo

⚡ *PERINTAH UTAMA:*
/mine — Buka panel mining
/bag — Lihat & jual ore
/shop — Beli alat, item, zona baru
/inventory — Pakai item consumable
/profile — Lihat statistik kamu
/daily — Ambil bonus harian
/market — Jual beli ore antar pemain
/leaderboard — Papan peringkat
/vip — Cek status VIP kamu

🎒 *UPGRADE BAG:*
/buyslot — +10 slot bag
/slotinfo — Info harga upgrade bag

⚡ *UPGRADE ENERGY:*
/buyenergy — +100 max energy
/energyinfo — Info harga upgrade energy

💡 *TIPS:*
• Zona lebih dalam = ore lebih langka & mahal
• Daily streak memberikan bonus berlipat
• Alat tidak membutuhkan syarat level apapun!
• Alat tier 6+ perlu sedikit ore untuk dibeli
• VIP = cara terbaik farming lebih efisien

🌍 *ZONA:* 20 zona dari Permukaan hingga Alam Genesis
⛏️ *ALAT:* 48 alat dari Tier 1 Starter hingga Tier 8 Divine
🪨 *ORE:* 113 jenis ore dari Kerikil hingga Permata Tak Terbatas
🎒 *ITEM:* Puluhan item termasuk buff XP, luck, speed, & KG!
"""

@router.message(F.text == "❓ Bantuan")
@router.message(Command("help"))
async def show_help(message: Message):
    await message.answer(HELP_TEXT, parse_mode="Markdown", reply_markup=main_menu_kb())
