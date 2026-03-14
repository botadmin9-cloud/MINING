"""
🎒 Bag Handler v3
— /bag          : lihat ore inventory (50 slot default, maks 350)
— /buyslot      : beli tambahan slot bag (+10 per upgrade)
— /buyenergy    : beli tambahan max energy (+100 per upgrade, maks 5000)
— Inline: jual 1 ore, jual semua jenis, jual semua bag
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import (ORES, ADMIN_IDS,
                    BAG_SLOT_DEFAULT, BAG_SLOT_MAX, BAG_SLOT_STEP, BAG_SLOT_BASE_COST,
                    ENERGY_UPGRADE_MAX, ENERGY_UPGRADE_STEP, ENERGY_UPGRADE_BASE_COST)
from database import get_user, update_user, remove_ore_from_inventory, add_balance
from game import buy_bag_slot, buy_energy_upgrade
from keyboards import back_main_kb

router = Router()

BAG_PAGE_SIZE = 10   # ore per halaman


def _is_admin(uid: int) -> bool:
    return uid in ADMIN_IDS


# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════
def _ore_value(ore_id: str) -> int:
    return ORES.get(ore_id, {}).get("value", 0)


def _bag_kb(ore_items: list, page: int, total_pages: int) -> InlineKeyboardMarkup:
    """ore_items = [(ore_id, qty), ...]  sudah di-slice ke halaman ini."""
    rows = []
    for ore_id, qty in ore_items:
        ore = ORES.get(ore_id, {})
        label = f"{ore.get('emoji','')} {ore.get('name', ore_id)} x{qty}"
        rows.append([
            InlineKeyboardButton(text=label,            callback_data=f"bag_detail_{ore_id}"),
            InlineKeyboardButton(text="💰 Jual 1",      callback_data=f"bag_sell1_{ore_id}"),
            InlineKeyboardButton(text="💰 Jual Semua",  callback_data=f"bag_sellall_{ore_id}"),
        ])

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="◀️", callback_data=f"bag_page_{page-1}"))
    nav.append(InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="noop"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton(text="▶️", callback_data=f"bag_page_{page+1}"))
    if nav:
        rows.append(nav)

    rows.append([
        InlineKeyboardButton(text="🗑️ Jual SEMUA Ore", callback_data="bag_sell_everything"),
        InlineKeyboardButton(text="🔙 Menu",            callback_data="main_menu"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def _bag_text(user: dict, page: int) -> tuple:
    """Returns (text, kb, sorted_items, total_pages)"""
    ore_inv = {k: v for k, v in user.get("ore_inventory", {}).items() if v > 0}
    # sort by ore value descending
    sorted_items = sorted(ore_inv.items(), key=lambda x: _ore_value(x[0]), reverse=True)

    total_qty   = sum(v for _, v in sorted_items)
    bag_slots   = user.get("bag_slots", BAG_SLOT_DEFAULT)
    total_pages = max(1, (len(sorted_items) + BAG_PAGE_SIZE - 1) // BAG_PAGE_SIZE)
    page        = max(0, min(page, total_pages - 1))

    chunk = sorted_items[page * BAG_PAGE_SIZE : (page + 1) * BAG_PAGE_SIZE]

    est_value = sum(_ore_value(oid) * qty for oid, qty in sorted_items)

    text = (
        f"🎒 *Bag Ore Kamu*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📦 Slot    : `{total_qty}/{bag_slots}`\n"
        f"🪨 Jenis   : `{len(sorted_items)}`\n"
        f"💰 Est.Nilai: `{est_value:,}` koin\n\n"
        f"Klik ore untuk detail, atau langsung jual:"
    )
    kb = _bag_kb(chunk, page, total_pages)
    return text, kb, sorted_items, total_pages


# ══════════════════════════════════════════════════════════════
# /bag  &  🎒 Bag  button
# ══════════════════════════════════════════════════════════════
@router.message(F.text == "🎒 Bag")
@router.message(Command("bag"))
async def cmd_bag(message: Message):
    user = await get_user(message.from_user.id)
    if not user:
        await message.answer("❌ Ketik /start!")
        return
    if not user.get("ore_inventory") or not any(v > 0 for v in user["ore_inventory"].values()):
        await message.answer(
            "🎒 *Bag Kamu Kosong*\n\nMulai mining untuk mengisi bag!",
            reply_markup=back_main_kb(), parse_mode="Markdown"
        )
        return
    text, kb, _, _ = await _bag_text(user, 0)
    await message.answer(text, reply_markup=kb, parse_mode="Markdown")


@router.callback_query(F.data.startswith("bag_page_"))
async def cb_bag_page(callback: CallbackQuery):
    page = int(callback.data.split("_")[-1])
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.answer("Ketik /start!")
        return
    text, kb, _, _ = await _bag_text(user, page)
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    await callback.answer()


# ── Detail ore di bag ─────────────────────────────────────────
@router.callback_query(F.data.startswith("bag_detail_"))
async def cb_bag_detail(callback: CallbackQuery):
    ore_id = callback.data.replace("bag_detail_", "")
    ore    = ORES.get(ore_id)
    user   = await get_user(callback.from_user.id)
    if not ore or not user:
        await callback.answer("❌ Ore tidak ditemukan!")
        return

    qty     = user.get("ore_inventory", {}).get(ore_id, 0)
    fav     = user.get("favorite_ores", [])
    museum  = user.get("museum_ores", [])
    in_fav  = ore_id in fav
    in_mus  = ore_id in museum

    # Cek apakah ada foto ore
    from database import get_ore_photo
    photo = await get_ore_photo(ore_id)

    rows = [
        [
            InlineKeyboardButton(text="💰 Jual 1",     callback_data=f"bag_sell1_{ore_id}"),
            InlineKeyboardButton(text="💰 Jual Semua", callback_data=f"bag_sellall_{ore_id}"),
        ],
        [
            InlineKeyboardButton(
                text="⭐ Hapus Favorit" if in_fav else "⭐ Tambah Favorit",
                callback_data=f"fav_toggle_{ore_id}"
            ),
            InlineKeyboardButton(
                text="🏛️ Hapus Museum" if in_mus else "🏛️ Simpan Museum",
                callback_data=f"museum_toggle_{ore_id}"
            ),
        ],
        [InlineKeyboardButton(text="🔙 Bag", callback_data="bag_back_0")],
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)

    text = (
        f"{ore['emoji']} *{ore['name']}*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📝 _{ore.get('desc','')}_\n\n"
        f"📦 Kamu punya : `{qty}` buah\n"
        f"💰 Nilai/buah : `{ore['value']:,}` koin\n"
        f"💰 Total est. : `{ore['value'] * qty:,}` koin\n"
        f"✨ Raritas    : `{ore['rarity']}%`\n\n"
        f"{'⭐ Ada di Favorit' if in_fav else ''}"
        f"{'  🏛️ Ada di Museum' if in_mus else ''}"
    )

    if photo:
        await callback.message.answer_photo(
            photo=photo["photo_id"],
            caption=text,
            reply_markup=kb,
            parse_mode="Markdown"
        )
    else:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "bag_back_0")
async def cb_bag_back(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.answer("Ketik /start!")
        return
    text, kb, _, _ = await _bag_text(user, 0)
    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    except Exception:
        await callback.message.answer(text, reply_markup=kb, parse_mode="Markdown")
    await callback.answer()


# ── Jual 1 ore ────────────────────────────────────────────────
@router.callback_query(F.data.startswith("bag_sell1_"))
async def cb_bag_sell1(callback: CallbackQuery):
    ore_id = callback.data.replace("bag_sell1_", "")
    ore    = ORES.get(ore_id)
    user   = await get_user(callback.from_user.id)
    if not ore or not user:
        await callback.answer("❌ Ore tidak ditemukan!")
        return

    qty = user.get("ore_inventory", {}).get(ore_id, 0)
    if qty <= 0:
        await callback.answer("❌ Ore sudah habis!", show_alert=True)
        return

    ok = await remove_ore_from_inventory(callback.from_user.id, ore_id, 1)
    if not ok:
        await callback.answer("❌ Gagal menjual!", show_alert=True)
        return

    coins = ore["value"]
    await add_balance(callback.from_user.id, coins, f"Jual {ore['name']} x1 dari bag")
    await callback.answer(f"✅ +{coins:,} koin dari {ore['name']}", show_alert=False)

    # refresh bag
    user = await get_user(callback.from_user.id)
    text, kb, _, _ = await _bag_text(user, 0)
    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    except Exception:
        pass


# ── Jual Semua (satu jenis ore) ───────────────────────────────
@router.callback_query(F.data.startswith("bag_sellall_"))
async def cb_bag_sellall(callback: CallbackQuery):
    ore_id = callback.data.replace("bag_sellall_", "")
    ore    = ORES.get(ore_id)
    user   = await get_user(callback.from_user.id)
    if not ore or not user:
        await callback.answer("❌ Ore tidak ditemukan!")
        return

    qty = user.get("ore_inventory", {}).get(ore_id, 0)
    if qty <= 0:
        await callback.answer("❌ Ore sudah habis!", show_alert=True)
        return

    ok = await remove_ore_from_inventory(callback.from_user.id, ore_id, qty)
    if not ok:
        await callback.answer("❌ Gagal menjual!", show_alert=True)
        return

    coins = ore["value"] * qty
    await add_balance(callback.from_user.id, coins, f"Jual {ore['name']} x{qty} dari bag")
    await callback.answer(f"✅ +{coins:,} koin dari {qty}x {ore['name']}", show_alert=True)

    user = await get_user(callback.from_user.id)
    text, kb, _, _ = await _bag_text(user, 0)
    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    except Exception:
        pass


# ── Jual SEMUA isi bag ────────────────────────────────────────
@router.callback_query(F.data == "bag_sell_everything")
async def cb_bag_sell_everything(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.answer("Ketik /start!")
        return

    ore_inv = {k: v for k, v in user.get("ore_inventory", {}).items() if v > 0}
    if not ore_inv:
        await callback.answer("❌ Bag sudah kosong!", show_alert=True)
        return

    total_coins = 0
    total_items = 0
    for ore_id, qty in ore_inv.items():
        ore = ORES.get(ore_id, {})
        total_coins += ore.get("value", 0) * qty
        total_items += qty

    # Kosongkan ore_inventory
    await update_user(callback.from_user.id, ore_inventory={})
    await add_balance(callback.from_user.id, total_coins, f"Jual semua bag ({total_items} ore)")

    user = await get_user(callback.from_user.id)
    await callback.message.edit_text(
        f"💰 *Semua Ore Terjual!*\n\n"
        f"📦 Total ore   : `{total_items}` buah\n"
        f"🪨 Total jenis : `{len(ore_inv)}`\n"
        f"💰 Koin dapat  : `+{total_coins:,}`\n"
        f"💰 Saldo baru  : `{user['balance']:,}` koin",
        reply_markup=back_main_kb(),
        parse_mode="Markdown"
    )
    await callback.answer(f"✅ +{total_coins:,} koin!", show_alert=True)


# ══════════════════════════════════════════════════════════════
# /buyslot — Tambah slot bag
# ══════════════════════════════════════════════════════════════
@router.message(Command("buyslot"))
async def cmd_buyslot(message: Message):
    is_admin = _is_admin(message.from_user.id)
    ok, msg = await buy_bag_slot(message.from_user.id, admin=is_admin)
    await message.answer(msg, parse_mode="Markdown")


# Info harga slot
@router.message(Command("slotinfo"))
async def cmd_slotinfo(message: Message):
    user = await get_user(message.from_user.id)
    if not user:
        await message.answer("❌ Ketik /start!")
        return

    cur_slots   = user.get("bag_slots", BAG_SLOT_DEFAULT)
    steps_done  = (cur_slots - BAG_SLOT_DEFAULT) // BAG_SLOT_STEP
    next_price  = BAG_SLOT_BASE_COST + (steps_done * 500)
    ore_used    = sum(user.get("ore_inventory", {}).values())

    lines = [
        f"🎒 *Info Slot Bag*",
        f"━━━━━━━━━━━━━━━━━━━━",
        f"📦 Slot saat ini : `{cur_slots}`",
        f"📦 Slot terpakai : `{ore_used}/{cur_slots}`",
        f"📦 Slot maksimal : `{BAG_SLOT_MAX}`",
        f"",
        f"💰 Harga upgrade berikutnya: `{next_price:,}` koin",
        f"   _(+{BAG_SLOT_STEP} slot per upgrade)_",
        f"",
        f"Ketik `/buyslot` untuk upgrade!",
    ]
    if cur_slots >= BAG_SLOT_MAX:
        lines.append(f"\n✅ *Slot sudah maksimal ({BAG_SLOT_MAX})!*")

    await message.answer("\n".join(lines), parse_mode="Markdown")


# ══════════════════════════════════════════════════════════════
# /buyenergy — Tambah max energy
# ══════════════════════════════════════════════════════════════
@router.message(Command("buyenergy"))
async def cmd_buyenergy(message: Message):
    is_admin = _is_admin(message.from_user.id)
    ok, msg = await buy_energy_upgrade(message.from_user.id, admin=is_admin)
    await message.answer(msg, parse_mode="Markdown")


# Info harga energy
@router.message(Command("energyinfo"))
async def cmd_energyinfo(message: Message):
    user = await get_user(message.from_user.id)
    if not user:
        await message.answer("❌ Ketik /start!")
        return

    cur_max    = user.get("max_energy", 500)
    steps_done = (cur_max - 500) // ENERGY_UPGRADE_STEP
    next_price = ENERGY_UPGRADE_BASE_COST + (steps_done * 2000)

    lines = [
        f"⚡ *Info Upgrade Energy*",
        f"━━━━━━━━━━━━━━━━━━━━",
        f"⚡ Max Energy saat ini : `{cur_max}`",
        f"⚡ Max Energy maksimal : `{ENERGY_UPGRADE_MAX}`",
        f"",
        f"💰 Harga upgrade berikutnya: `{next_price:,}` koin",
        f"   _(+{ENERGY_UPGRADE_STEP} max energy per upgrade)_",
        f"",
        f"Ketik `/buyenergy` untuk upgrade!",
    ]
    if cur_max >= ENERGY_UPGRADE_MAX:
        lines.append(f"\n✅ *Max Energy sudah maksimal ({ENERGY_UPGRADE_MAX})!*")

    await message.answer("\n".join(lines), parse_mode="Markdown")
