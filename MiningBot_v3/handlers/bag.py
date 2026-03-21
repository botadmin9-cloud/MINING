from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from config import (ORES, ADMIN_IDS,
                    BAG_SLOT_DEFAULT,
                    calculate_sell_price, format_kg,
                    ORE_TIER_COLORS)
from database import get_user, update_user, add_balance
from game import get_active_buffs, get_buff_val
# buy_bag_slot and buy_energy_upgrade moved to shop.py
from keyboards import back_main_kb

router = Router()
BAG_PAGE_SIZE = 10

# Urutan tier untuk sorting
TIER_ORDER = {"divine": 0, "cosmic": 1, "mythical": 2, "legendary": 3,
               "epic": 4, "rare": 5, "uncommon": 6, "common": 7}
TIER_LABELS = {
    "divine":    "🌈 DIVINE",
    "cosmic":    "🌟 COSMIC",
    "mythical":  "💜 MYTHICAL",
    "legendary": "🔴 LEGENDARY",
    "epic":      "🟠 EPIC",
    "rare":      "🔵 RARE",
    "uncommon":  "🟢 UNCOMMON",
    "common":    "⚪ COMMON",
}
RARE_TIERS = {"rare", "epic", "legendary", "mythical", "cosmic", "divine"}


def _is_admin(uid: int) -> bool:
    return uid in ADMIN_IDS


def _ore_value(ore_id: str) -> int:
    return ORES.get(ore_id, {}).get("value", 0)


def _ore_tier_rank(ore_id: str) -> int:
    tier = ORES.get(ore_id, {}).get("tier", "common")
    return TIER_ORDER.get(tier, 99)


def _get_ore_avg_kg(user: dict, ore_id: str) -> float:
    ore_inv = user.get("ore_inventory", {})
    ore_kg_data = user.get("ore_kg_data", {})
    qty = ore_inv.get(ore_id, 0)
    total_kg = ore_kg_data.get(ore_id, 0.0)
    if qty > 0 and total_kg > 0:
        return round(total_kg / qty, 2)
    ore = ORES.get(ore_id, {})
    return round((ore.get("kg_min", 0.5) + ore.get("kg_max", 2.0)) / 2, 2)


def _estimated_sell_price(user: dict, ore_id: str, qty: int = 1) -> int:
    avg_kg = _get_ore_avg_kg(user, ore_id)
    base   = calculate_sell_price(ore_id, avg_kg) * qty
    # Terapkan buff coin_mult jika aktif
    buffs      = get_active_buffs(user)
    coin_mult  = get_buff_val(buffs, "coin_mult", 1.0)
    if coin_mult and coin_mult != 1.0:
        base = int(base * coin_mult)
    return base


def _apply_coin_mult(user: dict, base_coins: int) -> int:
    """Terapkan coin_mult buff ke harga jual aktual."""
    buffs     = get_active_buffs(user)
    coin_mult = get_buff_val(buffs, "coin_mult", 1.0)
    if coin_mult and coin_mult != 1.0:
        return int(base_coins * coin_mult)
    return base_coins


def _bag_kb(ore_items: list, page: int, total_pages: int, user: dict,
             show_rare_only: bool = False) -> InlineKeyboardMarkup:
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
    prefix = "bag_rare_page_" if show_rare_only else "bag_page_"
    if page > 0:
        nav.append(InlineKeyboardButton(text="◀️", callback_data=f"{prefix}{page-1}"))
    nav.append(InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="noop"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton(text="▶️", callback_data=f"{prefix}{page+1}"))
    if nav:
        rows.append(nav)

    if show_rare_only:
        rows.append([
            InlineKeyboardButton(text="📦 Tampilkan Semua Ore", callback_data="bag_view_all"),
            InlineKeyboardButton(text="💎 Jual Semua Rare",     callback_data="bag_sell_rare_confirm"),
        ])
    else:
        rows.append([
            InlineKeyboardButton(text="💎 Lihat Rare Saja",     callback_data="bag_view_rare"),
            InlineKeyboardButton(text="🗑️ Jual Semua Ore",      callback_data="bag_sell_everything_confirm"),
        ])
    rows.append([InlineKeyboardButton(text="🔙 Menu", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _get_sorted_items(user: dict, rare_only: bool = False) -> list:
    """Ambil ore inventory, diurutkan berdasarkan tier lalu value."""
    ore_inv = {k: v for k, v in user.get("ore_inventory", {}).items() if v > 0}
    if rare_only:
        ore_inv = {k: v for k, v in ore_inv.items()
                   if ORES.get(k, {}).get("tier", "common") in RARE_TIERS}
    return sorted(ore_inv.items(),
                  key=lambda x: (_ore_tier_rank(x[0]), -_ore_value(x[0])))


def _build_rare_text(user: dict) -> str:
    """Bangun teks tampilan ore rare yang tersusun rapi per tier."""
    sorted_items = _get_sorted_items(user, rare_only=True)
    if not sorted_items:
        return "💎 *Tidak ada ore rare di bag kamu!*"

    # Kelompokkan per tier
    by_tier: dict = {}
    for ore_id, qty in sorted_items:
        tier = ORES.get(ore_id, {}).get("tier", "common")
        by_tier.setdefault(tier, []).append((ore_id, qty))

    total_items = sum(qty for _, qty in sorted_items)
    total_types = len(sorted_items)
    ore_kg_data = user.get("ore_kg_data", {})

    # Estimasi total nilai
    total_est = sum(_estimated_sell_price(user, oid, qty) for oid, qty in sorted_items)

    lines = [
        "💎 *Ore Rare & Langka Kamu*",
        "━━━━━━━━━━━━━━━━━━━━",
        f"🪨 Total  : `{total_items}` buah ({total_types} jenis)",
        f"💰 Est.   : `{total_est:,}` koin",
        "",
    ]

    # Urutkan tier dari terbaik ke terburuk
    tier_order_list = ["divine", "cosmic", "mythical", "legendary", "epic", "rare"]
    for tier in tier_order_list:
        if tier not in by_tier:
            continue
        tier_label = TIER_LABELS.get(tier, tier.upper())
        lines.append(f"┌─ {tier_label} ─────────────────")
        for ore_id, qty in by_tier[tier]:
            ore = ORES.get(ore_id, {})
            avg_kg = _get_ore_avg_kg(user, ore_id)
            total_kg = round(avg_kg * qty, 2)
            sell_val = calculate_sell_price(ore_id, avg_kg) * qty
            lines.append(
                f"│ {ore.get('emoji','')} *{ore.get('name', ore_id)}*"
                f" × `{qty}` (~{format_kg(total_kg)})"
            )
            lines.append(f"│   💰 Est. `{sell_val:,}` koin")
        lines.append("└────────────────────────────")
        lines.append("")

    lines.append("💡 Klik tombol bawah untuk aksi:")
    return "\n".join(lines)


async def _bag_text(user: dict, page: int, rare_only: bool = False) -> tuple:
    sorted_items = _get_sorted_items(user, rare_only)
    ore_inv_all  = {k: v for k, v in user.get("ore_inventory", {}).items() if v > 0}

    total_qty   = sum(v for _, v in sorted_items)
    total_all   = sum(v for _, v in ore_inv_all.items())
    bag_slots   = user.get("bag_slots", BAG_SLOT_DEFAULT)
    total_pages = max(1, (len(sorted_items) + BAG_PAGE_SIZE - 1) // BAG_PAGE_SIZE)
    page        = max(0, min(page, total_pages - 1))

    chunk = sorted_items[page * BAG_PAGE_SIZE: (page + 1) * BAG_PAGE_SIZE]
    est_value = sum(_estimated_sell_price(user, oid, qty) for oid, qty in sorted_items)

    filter_note = " *(Rare+)*" if rare_only else ""
    text = (
        f"🎒 *Bag Ore Kamu*{filter_note}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📦 Slot    : `{total_all}/{bag_slots}`\n"
        f"🪨 Ditampil: `{total_qty}` buah ({len(sorted_items)} jenis)\n"
        f"💰 Est.Jual: `{est_value:,}` koin\n\n"
        f"💡 Harga jual = nilai ore × berat × 0.02\n\n"
        f"Klik ore untuk detail, atau langsung jual:"
    )
    kb = _bag_kb(chunk, page, total_pages, user, show_rare_only=rare_only)
    return text, kb, sorted_items, total_pages


@router.message(F.text == "🎒 Bag")
@router.message(Command("bag"))
async def cmd_bag(message: Message):
    user = await get_user(message.from_user.id)
    if not user:
        await message.answer("❌ Ketik /start!")
        return
    ore_inv = user.get("ore_inventory") or {}
    if not ore_inv or not any(v > 0 for v in ore_inv.values()):
        await message.answer(
            "🎒 *Bag Kamu Kosong*\n\nMulai mining untuk mengisi bag!",
            reply_markup=back_main_kb(), parse_mode="Markdown"
        )
        return
    text, kb, _, _ = await _bag_text(user, 0)
    await message.answer(text, reply_markup=kb, parse_mode="Markdown")


@router.callback_query(F.data == "bag_view_rare")
async def cb_bag_view_rare(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.answer("Ketik /start!")
        return
    sorted_rare = _get_sorted_items(user, rare_only=True)
    if not sorted_rare:
        await callback.answer("❌ Tidak ada ore rare di bag kamu!", show_alert=True)
        return

    rare_text = _build_rare_text(user)
    # Keyboard khusus rare view yang rapi
    rows = [
        [
            InlineKeyboardButton(text="📦 Tampilkan Semua Ore", callback_data="bag_view_all"),
            InlineKeyboardButton(text="💎 Jual Semua Rare",     callback_data="bag_sell_rare_confirm"),
        ],
        [InlineKeyboardButton(text="🔙 Menu", callback_data="main_menu")],
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    try:
        await callback.message.edit_text(rare_text, reply_markup=kb, parse_mode="Markdown")
    except Exception:
        pass
    await callback.answer()


@router.callback_query(F.data == "bag_view_all")
async def cb_bag_view_all(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.answer("Ketik /start!")
        return
    text, kb, _, _ = await _bag_text(user, 0, rare_only=False)
    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    except Exception:
        pass
    await callback.answer()


@router.callback_query(F.data.startswith("bag_page_"))
async def cb_bag_page(callback: CallbackQuery):
    page = int(callback.data.split("_")[-1])
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.answer("Ketik /start!")
        return
    text, kb, _, _ = await _bag_text(user, page, rare_only=False)
    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    except Exception:
        pass
    await callback.answer()


@router.callback_query(F.data.startswith("bag_rare_page_"))
async def cb_bag_rare_page(callback: CallbackQuery):
    page = int(callback.data.split("_")[-1])
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.answer("Ketik /start!")
        return
    text, kb, _, _ = await _bag_text(user, page, rare_only=True)
    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    except Exception:
        pass
    await callback.answer()


@router.callback_query(F.data.startswith("bag_detail_"))
async def cb_bag_detail(callback: CallbackQuery):
    ore_id = callback.data.replace("bag_detail_", "")
    ore    = ORES.get(ore_id)
    user   = await get_user(callback.from_user.id)
    if not ore or not user:
        await callback.answer("❌ Ore tidak ditemukan!")
        return

    qty      = user.get("ore_inventory", {}).get(ore_id, 0)
    avg_kg   = _get_ore_avg_kg(user, ore_id)
    total_kg = round(avg_kg * qty, 2)
    sell_1   = calculate_sell_price(ore_id, avg_kg)
    sell_all = sell_1 * qty
    fav      = user.get("favorite_ores", [])
    museum   = user.get("museum_ores", [])
    in_fav   = ore_id in fav
    in_mus   = ore_id in museum

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
        f"📦 Kamu punya      : `{qty}` buah\n"
        f"⚖️ Berat rata-rata  : `{format_kg(avg_kg)}` /buah\n"
        f"⚖️ Total berat     : `{format_kg(total_kg)}`\n"
        f"💰 Harga jual/bh   : `{sell_1:,}` koin\n"
        f"💰 Harga jual semua: `{sell_all:,}` koin\n\n"
        f"📊 Rentang berat: `{format_kg(ore.get('kg_min',0))}` — `{format_kg(ore.get('kg_max',5))}`\n"
        f"✨ Raritas       : `{ore.get('tier','common').upper()}`\n\n"
        f"{'⭐ Ada di Favorit' if in_fav else ''}"
        f"{'  🏛️ Ada di Museum' if in_mus else ''}"
    )

    from database import get_ore_photo
    ore_photo = await get_ore_photo(ore_id)
    if ore_photo:
        try:
            await callback.message.answer_photo(
                photo=ore_photo["photo_id"],
                caption=text,
                reply_markup=kb,
                parse_mode="Markdown"
            )
            await callback.message.delete()
        except Exception:
            try:
                await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
            except Exception:
                pass
    else:
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

    # FIX: Simpan avg_kg SEBELUM remove, karena setelah remove qty=0 dan avg_kg akan jadi default
    avg_kg_before = _get_ore_avg_kg(user, ore_id)

    # Gunakan remove_ore_from_inventory agar atomic dan mencegah double-sell
    from database import remove_ore_from_inventory
    removed = await remove_ore_from_inventory(callback.from_user.id, ore_id, 1)
    if not removed:
        await callback.answer("❌ Ore sudah habis!", show_alert=True)
        return

    # Re-fetch user terbaru untuk coin_mult buff, tapi pakai avg_kg yang sudah disimpan
    user = await get_user(callback.from_user.id)
    avg_kg  = avg_kg_before
    coins   = _apply_coin_mult(user, calculate_sell_price(ore_id, avg_kg)) if user else calculate_sell_price(ore_id, avg_kg)
    await add_balance(callback.from_user.id, coins, f"Jual {ore['name']} x1")
    await callback.answer(f"✅ +{coins:,} koin dari {ore['name']}", show_alert=False)

    user = await get_user(callback.from_user.id)
    if user and any(v > 0 for v in user.get("ore_inventory", {}).values()):
        text, kb, _, _ = await _bag_text(user, 0)
        try:
            await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
        except Exception:
            pass
    else:
        try:
            await callback.message.edit_text(
                "🎒 *Bag Kamu Kosong*\n\nMulai mining untuk mengisi bag!",
                reply_markup=back_main_kb(), parse_mode="Markdown"
            )
        except Exception:
            pass


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

    ore_kg_data  = user.get("ore_kg_data", {})
    total_kg_this = ore_kg_data.get(ore_id, 0.0)
    if total_kg_this <= 0:
        avg_kg = _get_ore_avg_kg(user, ore_id)
        total_kg_this = avg_kg * qty
    coins = _apply_coin_mult(user, calculate_sell_price(ore_id, total_kg_this))

    ore_inv     = dict(user.get("ore_inventory", {}))
    ore_kg_data = dict(ore_kg_data)
    ore_inv.pop(ore_id, None)
    ore_kg_data.pop(ore_id, None)
    new_kg_used = max(0.0, round(user.get("bag_kg_used", 0.0) - total_kg_this, 2))

    await update_user(callback.from_user.id,
                      ore_inventory=ore_inv,
                      ore_kg_data=ore_kg_data,
                      bag_kg_used=new_kg_used)
    await add_balance(callback.from_user.id, coins, f"Jual {ore['name']} x{qty}")
    await callback.answer(f"✅ +{coins:,} koin dari {qty}x {ore['name']}", show_alert=True)

    user = await get_user(callback.from_user.id)
    if user and any(v > 0 for v in user.get("ore_inventory", {}).values()):
        text, kb, _, _ = await _bag_text(user, 0)
        try:
            await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
        except Exception:
            pass
    else:
        try:
            await callback.message.edit_text(
                "🎒 *Bag Kamu Kosong*\n\nMulai mining untuk mengisi bag!",
                reply_markup=back_main_kb(), parse_mode="Markdown"
            )
        except Exception:
            pass


# ── Konfirmasi Jual Semua ─────────────────────────────────────
@router.callback_query(F.data == "bag_sell_everything_confirm")
async def cb_bag_sell_everything_confirm(callback: CallbackQuery):
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
    total_items = sum(ore_inv.values())
    for ore_id, qty in ore_inv.items():
        total_kg_this = ore_kg_data.get(ore_id, 0.0)
        if total_kg_this <= 0:
            avg = _get_ore_avg_kg(user, ore_id)
            total_kg_this = avg * qty
        total_coins += _apply_coin_mult(user, calculate_sell_price(ore_id, total_kg_this))

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Ya, Jual Semua!", callback_data="bag_sell_everything_yes"),
            InlineKeyboardButton(text="❌ Batal",           callback_data="bag_back_0"),
        ]
    ])
    try:
        await callback.message.edit_text(
            f"⚠️ *Konfirmasi Jual Semua Ore*\n\n"
            f"📦 Total ore  : `{total_items}` buah ({len(ore_inv)} jenis)\n"
            f"💰 Estimasi   : `{total_coins:,}` koin\n\n"
            f"❓ Yakin ingin menjual *SEMUA* ore di bag?",
            reply_markup=kb,
            parse_mode="Markdown"
        )
    except Exception:
        pass
    await callback.answer()


@router.callback_query(F.data == "bag_sell_everything_yes")
async def cb_bag_sell_everything_yes(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.answer("Ketik /start!")
        return

    ore_inv = {k: v for k, v in user.get("ore_inventory", {}).items() if v > 0}
    if not ore_inv:
        await callback.answer("❌ Bag sudah kosong!", show_alert=True)
        return

    ore_kg_data = user.get("ore_kg_data", {})
    total_coins  = 0
    total_items  = 0
    total_weight = 0.0

    for ore_id, qty in ore_inv.items():
        total_items += qty
        total_kg_this = ore_kg_data.get(ore_id, 0.0)
        if total_kg_this <= 0:
            avg = _get_ore_avg_kg(user, ore_id)
            total_kg_this = avg * qty
        total_weight += total_kg_this
        total_coins  += _apply_coin_mult(user, calculate_sell_price(ore_id, total_kg_this))

    await update_user(callback.from_user.id, ore_inventory={}, ore_kg_data={}, bag_kg_used=0.0)
    await add_balance(callback.from_user.id, total_coins, f"Jual semua bag ({total_items} ore)")

    user = await get_user(callback.from_user.id)
    try:
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
    except Exception:
        pass
    await callback.answer(f"✅ +{total_coins:,} koin!", show_alert=True)


# ── Konfirmasi Jual Semua RARE ────────────────────────────────
@router.callback_query(F.data == "bag_sell_rare_confirm")
async def cb_bag_sell_rare_confirm(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.answer("Ketik /start!")
        return

    rare_items = _get_sorted_items(user, rare_only=True)
    if not rare_items:
        await callback.answer("❌ Tidak ada ore rare di bag!", show_alert=True)
        return

    ore_kg_data = user.get("ore_kg_data", {})
    total_coins = 0
    total_items = 0
    for ore_id, qty in rare_items:
        total_items += qty
        total_kg_this = ore_kg_data.get(ore_id, 0.0)
        if total_kg_this <= 0:
            avg = _get_ore_avg_kg(user, ore_id)
            total_kg_this = avg * qty
        total_coins += _apply_coin_mult(user, calculate_sell_price(ore_id, total_kg_this))

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Ya, Jual Semua Rare!", callback_data="bag_sell_rare_yes"),
            InlineKeyboardButton(text="❌ Batal",                callback_data="bag_view_rare"),
        ]
    ])
    try:
        await callback.message.edit_text(
            f"⚠️ *Konfirmasi Jual Semua Ore Rare+*\n\n"
            f"📦 Total ore rare : `{total_items}` buah ({len(rare_items)} jenis)\n"
            f"💰 Estimasi       : `{total_coins:,}` koin\n\n"
            f"❓ Yakin ingin menjual *SEMUA ore rare/epic/legendary/mythical*?",
            reply_markup=kb,
            parse_mode="Markdown"
        )
    except Exception:
        pass
    await callback.answer()


@router.callback_query(F.data == "bag_sell_rare_yes")
async def cb_bag_sell_rare_yes(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.answer("Ketik /start!")
        return

    rare_items = _get_sorted_items(user, rare_only=True)
    if not rare_items:
        await callback.answer("❌ Tidak ada ore rare!", show_alert=True)
        return

    ore_inv     = dict(user.get("ore_inventory", {}))
    ore_kg_data = dict(user.get("ore_kg_data", {}))
    total_coins  = 0
    total_items  = 0
    total_weight = 0.0

    for ore_id, qty in rare_items:
        total_items += qty
        total_kg_this = ore_kg_data.get(ore_id, 0.0)
        if total_kg_this <= 0:
            avg = _get_ore_avg_kg(user, ore_id)
            total_kg_this = avg * qty
        total_weight += total_kg_this
        total_coins  += _apply_coin_mult(user, calculate_sell_price(ore_id, total_kg_this))
        ore_inv.pop(ore_id, None)
        ore_kg_data.pop(ore_id, None)

    new_kg_used = max(0.0, round(user.get("bag_kg_used", 0.0) - total_weight, 2))
    await update_user(callback.from_user.id,
                      ore_inventory=ore_inv,
                      ore_kg_data=ore_kg_data,
                      bag_kg_used=new_kg_used)
    await add_balance(callback.from_user.id, total_coins, f"Jual semua rare ({total_items} ore)")

    user = await get_user(callback.from_user.id)
    try:
        await callback.message.edit_text(
            f"💎 *Semua Ore Rare Terjual!*\n\n"
            f"📦 Total ore   : `{total_items}` buah\n"
            f"⚖️ Total berat : `{format_kg(total_weight)}`\n"
            f"🪨 Total jenis : `{len(rare_items)}`\n"
            f"💰 Koin dapat  : `+{total_coins:,}`\n"
            f"💰 Saldo baru  : `{user['balance']:,}` koin",
            reply_markup=back_main_kb(),
            parse_mode="Markdown"
        )
    except Exception:
        pass
    await callback.answer(f"✅ +{total_coins:,} koin!", show_alert=True)


@router.message(Command("buyslot"))
async def cmd_buyslot(message: Message):
    await message.answer(
        "💡 Pembelian *Slot Bag* sekarang tersedia di *🏪 Shop → ⬆️ Upgrade*!\n\n"
        "Ketik `🏪 Shop` atau `/shop` untuk akses.",
        parse_mode="Markdown"
    )


@router.message(Command("buyenergy"))
async def cmd_buyenergy(message: Message):
    await message.answer(
        "💡 Pembelian *Tambah Energy* sekarang tersedia di *🏪 Shop → ⬆️ Upgrade*!\n\n"
        "Ketik `🏪 Shop` atau `/shop` untuk akses.",
        parse_mode="Markdown"
    )
