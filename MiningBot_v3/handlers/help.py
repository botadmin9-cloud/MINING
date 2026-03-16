from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from keyboards import main_menu_kb

router = Router()

HELP_TEXT = """
❓ *BANTUAN — MiningBot v4 ULTIMATE*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎮 *CARA BERMAIN:*
1️⃣ Mining ore → masuk ke Bag
2️⃣ Jual ore di Bag atau Market
3️⃣ Gunakan koin untuk beli alat & item
4️⃣ Level up untuk buka konten baru!

⚖️ *SISTEM KG:*
• Setiap ore punya berat (kg_min — kg_max)
• Ore lebih berat = harga jual lebih tinggi
• Harga jual = nilai_dasar × berat_kg × 1.5
• Alat lebih canggih = ore lebih berat!
• Gunakan ⚖️ Weight Enhancer untuk boost KG

⭐ *SISTEM XP:*
• Mining fokus memberikan XP (bukan koin)
• Koin didapat dari MENJUAL ore di Bag/Market
• Ore lebih berat = XP lebih banyak
• Critical hit = XP 2x + ore lebih berat
• Lucky = XP 1.5x + ore sedikit lebih berat

⚡ *PERINTAH UTAMA:*
/mine — Buka panel mining
/bag — Lihat & jual ore
/shop — Beli alat, item, zona baru
/inventory — Pakai item consumable
/profile — Lihat statistik kamu
/daily — Ambil bonus harian
/market — Jual beli ore antar pemain
/leaderboard — Papan peringkat

🎒 *UPGRADE BAG:*
/buyslot — +10 slot bag
/buykg — +50 kg kapasitas bag
/slotinfo — Info harga upgrade bag

⚡ *UPGRADE ENERGY:*
/buyenergy — +100 max energy
/energyinfo — Info harga upgrade energy

💡 *TIPS:*
• Gunakan zona lebih dalam = ore lebih langka
• Daily streak memberikan bonus berlipat
• Premium Mystery Box bisa dapat ore legendaris
• Rebirth Token reset level tapi +50% XP permanent
• Alat Tier 8 Divine menghasilkan XP 50x!

🌍 *ZONA:* 12 zona dari Permukaan hingga Alam Genesis
⛏️ *ALAT:* 25 alat dari Tier 1 Starter hingga Tier 8 Divine
🪨 *ORE:* 38 jenis ore dari Kerikil hingga Inti Semesta
🎒 *ITEM:* 18 item termasuk KG Boost baru!
"""

@router.message(F.text == "❓ Bantuan")
@router.message(Command("help"))
async def show_help(message: Message):
    await message.answer(HELP_TEXT, parse_mode="Markdown", reply_markup=main_menu_kb())
