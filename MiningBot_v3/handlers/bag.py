from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from config import (ORES, ADMIN_IDS,
                    BAG_SLOT_DEFAULT, BAG_SLOT_MAX, BAG_SLOT_STEP, BAG_SLOT_BASE_COST,
                    ENERGY_UPGRADE_MAX, ENERGY_UPGRADE_STEP, ENERGY_UPGRADE_BASE_COST,
                    BAG_KG_DEFAULT, BAG_KG_MAX, BAG_KG_UPGRADE_STEP, BAG_KG_UPGRADE_COST,
                    calculate_sell_price, get_random_kg, format_kg)
from database import get_user, update_user, remove_ore_from_inventory, add_balance
from game import buy_bag_slot, buy_energy_upgrade, buy_bag_kg
from keyboards import back_main_kb

router = Router()
BAG_PAGE_SIZE = 10


def _is_admin(uid: int) -> bool:
    return uid in ADMIN_IDS


def _ore_value(ore_id: str) -> int:
    return ORES.get(ore_id, {}).get("value", 0)


def _get_ore_avg_kg(user: dict, ore_id: str) -> float:
    """Ambil rata-rata KG ore dari ore_kg_data."""
    ore_inv = user.get("ore_inventory", {})
    ore_kg_data = user.get("ore_kg_data", {})
    qty = ore_inv.get(ore_id, 0)
    total_kg = ore_kg_data.get(ore_id, 0.0)
    if qty > 0 and total_kg > 0:
        return round(total_kg / qty, 2)
    # Fallback ke midpoint
    ore = ORES.get(ore_id, {})
    return round((ore.get("kg_min", 0.5) + ore.get("kg_max", 2.0)) / 2, 2)


def _estimated_sell_price(user: dict, ore_id: str, qty: int = 1) -> int:
    avg_kg = _get_ore_avg_kg(user, ore_id)
    return calculate_sell_price(ore_id, avg_kg) * qty


def _bag_kb(ore_items: list, page: int, total_pages: int, user: dict) -> InlineKeyboardMarkup:
    rows = []
    for ore_id, qty in ore_items:
        ore = ORES.get(ore_id, {})
        avg_kg = _get_ore_avg_kg(user, ore_id)
        label = f"{ore.get('emoji','')} {ore.get('name', ore_id)} x{qty} (~{format_kg(avg_kg*qty)})"
        rows.append([
            InlineKeyboardButton(text=label,             callback_data=f"bag_detail_{ore_id}"),
            InlineKeyboardButton(text="💰 Jual 1",       callback_data=f"bag_sell1_{ore_id}"),
            InlineKeyboardButton(text="💰 Jual Semua",   callback_data=f"bag_sellall_{ore_id}"),
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
    ore_inv = {k: v for k, v in user.get("ore_inventory", {}).items() if v > 0}
    sorted_items = sorted(ore_inv.items(), key=lambda x: _ore_value(x[0]), reverse=True)

    total_qty   = sum(v for _, v in sorted_items)
    bag_slots   = user.get("bag_slots", BAG_SLOT_DEFAULT)
    bag_kg_used = user.get("bag_kg_used", 0.0)
    bag_kg_max  = user.get("bag_kg_max", BAG_KG_DEFAULT)
    total_pages = max(1, (len(sorted_items) + BAG_PAGE_SIZE - 1) // BAG_PAGE_SIZE)
    page        = max(0, min(page, total_pages - 1))

    chunk = sorted_items[page * BAG_PAGE_SIZE : (page + 1) * BAG_PAGE_SIZE]

    # Estimasi nilai jual berdasarkan KG
    est_value = sum(_estimated_sell_price(user, oid, qty) for oid, qty in sorted_items)

    text = (
        f"🎒 *Bag Ore Kamu*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📦 Slot    : `{total_qty}/{bag_slots}`\n"
        f"⚖️ Berat   : `{format_kg(bag_kg_used)}/{format_kg(bag_kg_max)}`\n"
        f"🪨 Jenis   : `{len(sorted_items)}`\n"
        f"💰 Est.Jual: `{est_value:,}` koin\n\n"
        f"💡 Harga jual = nilai ore × berat (kg) × 1.5\n\n"
        f"Klik ore untuk detail, atau langsung jual:"
    )
    kb = _bag_kb(chunk, page, total_pages, user)
    return text, kb, sorted_items, total_pages


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


@router.callback_query(F.data.startswith("bag_detail_"))
async def cb_bag_detail(callback: CallbackQuery):
    ore_id = callback.data.replace("bag_detail_", "")
    ore    = ORES.get(ore_id)
    user   = await get_user(callback.from_user.id)
    if not ore or not user:
        await callback.answer("❌ Ore tidak ditemukan!")
        return

    qty     = user.get("ore_inventory", {}).get(ore_id, 0)
    avg_kg  = _get_ore_avg_kg(user, ore_id)
    total_kg = round(avg_kg * qty, 2)
    sell_1  = calculate_sell_price(ore_id, avg_kg)
    sell_all = sell_1 * qty
    fav     = user.get("favorite_ores", [])
    museum  = user.get("museum_ores", [])
    in_fav  = ore_id in fav
    in_mus  = ore_id in museum

    from config import ORE_TIER_COLORS
    tier_color = ORE_TIER_COLORS.get(ore.get("tier", "common"), "⬜")

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
        f"{tier_color} {ore['emoji']} *{ore['name']}*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📝 _{ore.get('desc','')}_ \n\n"
        f"📦 Kamu punya     : `{qty}` buah\n"
        f"⚖️ Berat rata-rata : `{format_kg(avg_kg)}` /buah\n"
        f"⚖️ Total berat    : `{format_kg(total_kg)}`\n"
        f"💰 Harga jual/bh  : `{sell_1:,}` koin\n"
        f"💰 Harga jual semua: `{sell_all:,}` koin\n\n"
        f"📊 Rentang berat: `{format_kg(ore.get('kg_min',0))}` — `{format_kg(ore.get('kg_max',5))}`\n"
        f"✨ Raritas       : `{ore['rarity']}%`\n\n"
        f"{'⭐ Ada di Favorit' if in_fav else ''}"
        f"{'  🏛️ Ada di Museum' if in_mus else ''}"
    )

    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    except Exception:
        await callback.message.answer(text, reply_markup=kb, parse_mode="Markdown")
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

    # Hitung harga berdasarkan rata-rata KG
    avg_kg = _get_ore_avg_kg(user, ore_id)
    coins  = calculate_sell_price(ore_id, avg_kg)

    # Kurangi qty dan kg
    ore_inv = dict(user.get("ore_inventory", {}))
    ore_kg_data = dict(user.get("ore_kg_data", {}))
    ore_inv[ore_id] = ore_inv.get(ore_id, 0) - 1
    if ore_inv[ore_id] <= 0:
        del ore_inv[ore_id]
    # Kurangi KG proporsional
    if ore_id in ore_kg_data:
        ore_kg_data[ore_id] = max(0.0, round(ore_kg_data[ore_id] - avg_kg, 2))
        if ore_kg_data[ore_id] <= 0:
            del ore_kg_data[ore_id]
    # Update bag_kg_used
    new_kg_used = max(0.0, round(user.get("bag_kg_used", 0.0) - avg_kg, 2))
    await update_user(callback.from_user.id,
                      ore_inventory=ore_inv,
                      ore_kg_data=ore_kg_data,
                      bag_kg_used=new_kg_used)
    await add_balance(callback.from_user.id, coins, f"Jual {ore['name']} x1 ({format_kg(avg_kg)})")

    await callback.answer(f"✅ +{coins:,} koin dari {ore['name']} ({format_kg(avg_kg)})", show_alert=False)

    user = await get_user(callback.from_user.id)
    if user and any(v > 0 for v in user.get("ore_inventory", {}).values()):
        text, kb, _, _ = await _bag_text(user, 0)
        try:
            await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
        except Exception:
            pass
    else:
        await callback.message.edit_text(
            "🎒 *Bag Kamu Kosong*\n\nMulai mining untuk mengisi bag!",
            reply_markup=back_main_kb(), parse_mode="Markdown"
        )


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

    # Harga berdasarkan TOTAL KG semua ore jenis ini
    ore_kg_data = user.get("ore_kg_data", {})
    total_kg_this_ore = ore_kg_data.get(ore_id, 0.0)
    if total_kg_this_ore <= 0:
        avg_kg = _get_ore_avg_kg(user, ore_id)
        total_kg_this_ore = avg_kg * qty
    coins = calculate_sell_price(ore_id, total_kg_this_ore)

    # Hapus ore dari inventory
    ore_inv = dict(user.get("ore_inventory", {}))
    if ore_id in ore_inv:
        del ore_inv[ore_id]
    if ore_id in ore_kg_data:
        del ore_kg_data[ore_id]
    new_kg_used = max(0.0, round(user.get("bag_kg_used", 0.0) - total_kg_this_ore, 2))

    await update_user(callback.from_user.id,
                      ore_inventory=ore_inv,
                      ore_kg_data=ore_kg_data,
                      bag_kg_used=new_kg_used)
    await add_balance(callback.from_user.id, coins, f"Jual {ore['name']} x{qty} ({format_kg(total_kg_this_ore)})")

    await callback.answer(f"✅ +{coins:,} koin dari {qty}x {ore['name']} ({format_kg(total_kg_this_ore)})", show_alert=True)

    user = await get_user(callback.from_user.id)
    if user and any(v > 0 for v in user.get("ore_inventory", {}).values()):
        text, kb, _, _ = await _bag_text(user, 0)
        try:
            await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
        except Exception:
            pass
    else:
        await callback.message.edit_text(
            "🎒 *Bag Kamu Kosong*\n\nMulai mining untuk mengisi bag!",
            reply_markup=back_main_kb(), parse_mode="Markdown"
        )


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

    ore_kg_data = user.get("ore_kg_data", {})
    total_coins = 0
    total_items = 0
    total_weight = 0.0

    for ore_id, qty in ore_inv.items():
        total_items += qty
        total_kg_this = ore_kg_data.get(ore_id, 0.0)
        if total_kg_this <= 0:
            avg = _get_ore_avg_kg(user, ore_id)
            total_kg_this = avg * qty
        total_weight += total_kg_this
        total_coins += calculate_sell_price(ore_id, total_kg_this)

    await update_user(callback.from_user.id, ore_inventory={}, ore_kg_data={}, bag_kg_used=0.0)
    await add_balance(callback.from_user.id, total_coins, f"Jual semua bag ({total_items} ore, {format_kg(total_weight)})")

    user = await get_user(callback.from_user.id)
    await callback.message.edit_text(
        f"💰 *Semua Ore Terjual!*\n\n"
        f"📦 Total ore   : `{total_items}` buah\n"
        f"⚖️ Total berat : `{format_kg(total_weight)}`\n"
        f"🪨 Total jenis : `{len(ore_inv)}`\n"
        f"💰 Koin dapat  : `+{total_coins:,}`\n"
        f"💰 Saldo baru  : `{user['balance']:,}` koin",
        reply_markup=back_main_kb(),
        parse_mode="Markdown"
    )
    await callback.answer(f"✅ +{total_coins:,} koin!", show_alert=True)


@router.message(Command("buyslot"))
async def cmd_buyslot(message: Message):
    is_admin = _is_admin(message.from_user.id)
    ok, msg = await buy_bag_slot(message.from_user.id, admin=is_admin)
    await message.answer(msg, parse_mode="Markdown")


@router.message(Command("buykg"))
async def cmd_buykg(message: Message):
    """Upgrade kapasitas KG bag."""
    is_admin = _is_admin(message.from_user.id)
    ok, msg = await buy_bag_kg(message.from_user.id, admin=is_admin)
    await message.answer(msg, parse_mode="Markdown")


@router.message(Command("slotinfo"))
async def cmd_slotinfo(message: Message):
    user = await get_user(message.from_user.id)
    if not user:
        await message.answer("❌ Ketik /start!")
        return

    cur_slots   = user.get("bag_slots", BAG_SLOT_DEFAULT)
    cur_kg      = user.get("bag_kg_max", 100.0)
    kg_used     = user.get("bag_kg_used", 0.0)
    steps_done  = (cur_slots - BAG_SLOT_DEFAULT) // BAG_SLOT_STEP
    next_price  = BAG_SLOT_BASE_COST + (steps_done * 500)
    ore_used    = sum(user.get("ore_inventory", {}).values())

    lines = [
        f"🎒 *Info Bag*",
        f"━━━━━━━━━━━━━━━━━━━━",
        f"📦 Slot     : `{ore_used}/{cur_slots}`",
        f"⚖️ Berat    : `{format_kg(kg_used)}/{format_kg(cur_kg)}`",
        f"",
        f"💰 Upgrade slot: `{next_price:,}` koin (+{BAG_SLOT_STEP} slot)",
        f"   Ketik `/buyslot` untuk upgrade",
        f"",
        f"💰 Upgrade KG: `{BAG_KG_UPGRADE_COST:,}` koin (+{format_kg(BAG_KG_UPGRADE_STEP)})",
        f"   Ketik `/buykg` untuk upgrade",
    ]
    await message.answer("\n".join(lines), parse_mode="Markdown")


@router.message(Command("buyenergy"))
async def cmd_buyenergy(message: Message):
    is_admin = _is_admin(message.from_user.id)
    ok, msg = await buy_energy_upgrade(message.from_user.id, admin=is_admin)
    await message.answer(msg, parse_mode="Markdown")


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
