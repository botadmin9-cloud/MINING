from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)
from config import TOOLS, ITEMS, ZONES, TIER_COLORS


# ══════════════════════════════════════════════════════════════
# MAIN MENU
# ══════════════════════════════════════════════════════════════
def main_menu_kb() -> ReplyKeyboardMarkup:
    from config import OFFICIAL_CHANNEL, OFFICIAL_GROUP
    keyboard = [
        [KeyboardButton(text="⛏️ Mining"),         KeyboardButton(text="👤 Profil")],
        [KeyboardButton(text="🔧 Equipment"),       KeyboardButton(text="🎁 Inventaris")],
        [KeyboardButton(text="🏪 Shop"),             KeyboardButton(text="🏆 Leaderboard")],
        [KeyboardButton(text="📅 Daily"),            KeyboardButton(text="🛒 Market")],
        [KeyboardButton(text="🎒 Bag"),              KeyboardButton(text="⭐ Favorit")],
        [KeyboardButton(text="🏛️ Museum"),           KeyboardButton(text="❓ Bantuan")],
    ]
    community_row = []
    if OFFICIAL_GROUP:
        community_row.append(KeyboardButton(text="👥 Gabung Grup"))
    if OFFICIAL_CHANNEL:
        community_row.append(KeyboardButton(text="📢 Gabung Channel"))
    if community_row:
        keyboard.append(community_row)
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Pilih menu..."
    )


def back_main_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Menu Utama", callback_data="main_menu")]
    ])


# ══════════════════════════════════════════════════════════════
# MINING
# ══════════════════════════════════════════════════════════════
def mine_action_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⛏️ Mine!",  callback_data="do_mine"),
            InlineKeyboardButton(text="⛏️x5",       callback_data="do_mine_5"),
            InlineKeyboardButton(text="⛏️x10",      callback_data="do_mine_10"),
        ],
        [
            InlineKeyboardButton(text="⛏️x25",      callback_data="do_mine_25"),
            InlineKeyboardButton(text="⛏️x50",      callback_data="do_mine_50"),
        ],
        [
            InlineKeyboardButton(text="📍 Ganti Zona", callback_data="zone_menu"),
            InlineKeyboardButton(text="🔧 Ganti Alat",  callback_data="equip_menu"),
        ],
        [InlineKeyboardButton(text="🏠 Menu Utama", callback_data="main_menu")],
    ])


# ══════════════════════════════════════════════════════════════
# SHOP
# ══════════════════════════════════════════════════════════════
def shop_main_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⛏️ Alat Mining",          callback_data="shop_tools_0")],
        [InlineKeyboardButton(text="🎒 Item & Consumable",      callback_data="shop_items")],
        [InlineKeyboardButton(text="🌍 Buka Zona Baru",        callback_data="shop_zones")],
        [InlineKeyboardButton(text="⬆️ Upgrade (Bag & Energy)", callback_data="shop_upgrades")],
        [InlineKeyboardButton(text="👑 VIP Member",             callback_data="shop_vip")],
        [InlineKeyboardButton(text="💰 Top Up Saldo",           callback_data="shop_topup")],
        [InlineKeyboardButton(text="🏠 Menu Utama",            callback_data="main_menu")],
    ])


def shop_upgrades_kb(cur_slots: int, cur_energy: int, balance: int) -> InlineKeyboardMarkup:
    from config import BAG_SLOT_MAX, BAG_SLOT_STEP, BAG_SLOT_BASE_COST, BAG_SLOT_DEFAULT
    from config import ENERGY_UPGRADE_MAX, ENERGY_UPGRADE_STEP, ENERGY_UPGRADE_BASE_COST

    rows = []

    # Slot bag button
    if cur_slots >= BAG_SLOT_MAX:
        rows.append([InlineKeyboardButton(
            text="🎒 Slot Bag — ✅ MAKS",
            callback_data="noop"
        )])
    else:
        steps = (cur_slots - BAG_SLOT_DEFAULT) // BAG_SLOT_STEP
        price = BAG_SLOT_BASE_COST + (steps * 2000)
        label = f"🎒 Beli +{BAG_SLOT_STEP} Slot Bag — {price:,}🪙"
        if balance < price:
            label = f"💸 {label} (Koin kurang)"
        rows.append([InlineKeyboardButton(text=label, callback_data="shop_buy_bag_slot")])

    # Energy button
    if cur_energy >= ENERGY_UPGRADE_MAX:
        rows.append([InlineKeyboardButton(
            text="⚡ Max Energy — ✅ MAKS",
            callback_data="noop"
        )])
    else:
        steps = (cur_energy - 500) // ENERGY_UPGRADE_STEP
        price = ENERGY_UPGRADE_BASE_COST + (steps * 5000)
        label = f"⚡ Beli +{ENERGY_UPGRADE_STEP} Max Energy — {price:,}🪙"
        if balance < price:
            label = f"💸 {label} (Koin kurang)"
        rows.append([InlineKeyboardButton(text=label, callback_data="shop_buy_energy")])

    rows.append([InlineKeyboardButton(text="🔙 Shop Menu", callback_data="shop_menu")])
    rows.append([InlineKeyboardButton(text="🏠 Menu Utama", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def shop_tools_kb(owned: list, level: int, balance: int, page: int = 0,
                  ore_inv: dict = None) -> InlineKeyboardMarkup:
    all_tools = list(TOOLS.items())
    per_page  = 5
    start     = page * per_page
    chunk     = all_tools[start: start + per_page]
    rows      = []
    ore_inv   = ore_inv or {}

    for tid, t in chunk:
        tier_icon = TIER_COLORS.get(t["tier"], "⬜")
        ore_req   = t.get("ore_req", {})

        if tid in owned:
            label = f"✅ {t['emoji']} {t['name']}"
        elif balance < t["price"] and t["price"] > 0:
            label = f"💸 {tier_icon} {t['name']} ({t['price']:,}🪙)"
        elif ore_req and not all(ore_inv.get(k, 0) >= v for k, v in ore_req.items()):
            label = f"🪨 {tier_icon} {t['name']} (Butuh Ore)"
        else:
            label = f"🛒 {tier_icon} {t['name']} ({t['price']:,}🪙)" if t["price"] > 0 else f"🆓 {t['name']}"
        rows.append([InlineKeyboardButton(text=label, callback_data=f"tool_detail_{tid}")])

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="◀️ Prev", callback_data=f"shop_tools_{page-1}"))
    if start + per_page < len(all_tools):
        nav.append(InlineKeyboardButton(text="Next ▶️", callback_data=f"shop_tools_{page+1}"))
    if nav:
        rows.append(nav)

    rows.append([InlineKeyboardButton(text="🔙 Shop Menu", callback_data="shop_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def tool_detail_kb(tool_id: str, owned: bool, is_current: bool) -> InlineKeyboardMarkup:
    rows = []
    if owned:
        if not is_current:
            rows.append([InlineKeyboardButton(text="⚒️ Pasang Alat Ini", callback_data=f"equip_{tool_id}")])
        else:
            rows.append([InlineKeyboardButton(text="✅ Sedang Dipakai", callback_data="noop")])
    else:
        rows.append([InlineKeyboardButton(text="🛒 Beli Sekarang", callback_data=f"buy_tool_{tool_id}")])
    rows.append([InlineKeyboardButton(text="🔙 Daftar Alat", callback_data="shop_tools_0")])
    rows.append([InlineKeyboardButton(text="🏠 Menu Utama",  callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def shop_items_kb() -> InlineKeyboardMarkup:
    rows = []
    for iid, item in ITEMS.items():
        rows.append([InlineKeyboardButton(
            text=f"{item['emoji']} {item['name']} — {item['price']:,}🪙",
            callback_data=f"item_detail_{iid}"
        )])
    rows.append([InlineKeyboardButton(text="🔙 Shop Menu", callback_data="shop_menu")])
    rows.append([InlineKeyboardButton(text="🏠 Menu Utama", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def item_detail_kb(item_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Beli Item Ini", callback_data=f"buy_item_{item_id}")],
        [InlineKeyboardButton(text="🔙 Daftar Item",   callback_data="shop_items")],
        [InlineKeyboardButton(text="🏠 Menu Utama",    callback_data="main_menu")],
    ])


def shop_zones_kb(unlocked: list, level: int, balance: int) -> InlineKeyboardMarkup:
    rows = []
    for zid, z in ZONES.items():
        if zid in unlocked:
            label = f"✅ {z['name']}"
        elif level < z["level_req"]:
            label = f"🔒 {z['name']} (Lv.{z['level_req']})"
        elif balance < z["unlock_cost"]:
            label = f"💸 {z['name']} ({z['unlock_cost']:,}🪙)"
        else:
            label = f"🔓 {z['name']} — {z['unlock_cost']:,}🪙"
        rows.append([InlineKeyboardButton(text=label, callback_data=f"zone_detail_{zid}")])
    rows.append([InlineKeyboardButton(text="🔙 Shop Menu", callback_data="shop_menu")])
    rows.append([InlineKeyboardButton(text="🏠 Menu Utama", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def zone_detail_kb(zone_id: str, unlocked: bool, is_active: bool) -> InlineKeyboardMarkup:
    rows = []
    if unlocked:
        if not is_active:
            rows.append([InlineKeyboardButton(text="📍 Pindah ke Zona Ini", callback_data=f"set_zone_{zone_id}")])
        else:
            rows.append([InlineKeyboardButton(text="✅ Zona Aktif", callback_data="noop")])
    else:
        rows.append([InlineKeyboardButton(text="🔓 Buka Zona Ini", callback_data=f"unlock_zone_{zone_id}")])
    rows.append([InlineKeyboardButton(text="🔙 Daftar Zona",  callback_data="shop_zones")])
    rows.append([InlineKeyboardButton(text="🏠 Menu Utama",   callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ══════════════════════════════════════════════════════════════
# EQUIPMENT
# ══════════════════════════════════════════════════════════════
def equipment_kb(owned: list, current: str) -> InlineKeyboardMarkup:
    rows = []
    for tid in owned:
        t = TOOLS.get(tid)
        if not t:
            continue
        prefix = "✅ " if tid == current else "   "
        label = f"{prefix}{t['emoji']} {t['name']} (Tier {t['tier']})"
        rows.append([InlineKeyboardButton(text=label, callback_data=f"tool_detail_{tid}")])
    rows.append([InlineKeyboardButton(text="🏪 Beli Alat Baru", callback_data="shop_tools_0")])
    rows.append([InlineKeyboardButton(text="🏠 Menu Utama",     callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def equip_menu_kb(owned: list, current: str) -> InlineKeyboardMarkup:
    rows = []
    for tid in owned:
        t = TOOLS.get(tid)
        if not t:
            continue
        label = f"{'✅' if tid == current else '⚒️'} {t['emoji']} {t['name']}"
        rows.append([InlineKeyboardButton(text=label, callback_data=f"equip_{tid}")])
    rows.append([InlineKeyboardButton(text="🔙 Kembali", callback_data="mine_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def zone_menu_kb(unlocked: list, current: str) -> InlineKeyboardMarkup:
    rows = []
    for zid in unlocked:
        z = ZONES.get(zid)
        if not z:
            continue
        label = f"{'📍' if zid == current else '  '} {z['name']}"
        rows.append([InlineKeyboardButton(text=label, callback_data=f"set_zone_{zid}")])
    rows.append([InlineKeyboardButton(text="🔓 Buka Zona Baru", callback_data="shop_zones")])
    rows.append([InlineKeyboardButton(text="🔙 Kembali",        callback_data="mine_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ══════════════════════════════════════════════════════════════
# INVENTORY
# ══════════════════════════════════════════════════════════════
def inventory_kb(inventory: dict) -> InlineKeyboardMarkup:
    rows = []
    for item_id, qty in inventory.items():
        item = ITEMS.get(item_id)
        if not item or qty <= 0:
            continue
        rows.append([InlineKeyboardButton(
            text=f"{item['emoji']} {item['name']} x{qty} — Gunakan",
            callback_data=f"use_item_{item_id}"
        )])
    if not rows:
        rows.append([InlineKeyboardButton(text="🏪 Beli Item di Shop", callback_data="shop_items")])
    rows.append([InlineKeyboardButton(text="🏠 Menu Utama", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ══════════════════════════════════════════════════════════════
# ORE INVENTORY (untuk market)
# ══════════════════════════════════════════════════════════════
def ore_inventory_kb(ore_inventory: dict, page: int = 0) -> InlineKeyboardMarkup:
    from config import ORES
    rows = []
    ore_list = [(k, v) for k, v in ore_inventory.items() if v > 0]
    per_page = 8
    start = page * per_page
    chunk = ore_list[start: start + per_page]

    for ore_id, qty in chunk:
        ore = ORES.get(ore_id, {})
        label = f"{ore.get('emoji','')} {ore.get('name', ore_id)} x{qty}"
        rows.append([InlineKeyboardButton(text=label, callback_data=f"sell_ore_{ore_id}")])

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="◀️", callback_data=f"ore_page_{page-1}"))
    if start + per_page < len(ore_list):
        nav.append(InlineKeyboardButton(text="▶️", callback_data=f"ore_page_{page+1}"))
    if nav:
        rows.append(nav)

    rows.append([InlineKeyboardButton(text="🔙 Market", callback_data="market_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ══════════════════════════════════════════════════════════════
# MARKET
# ══════════════════════════════════════════════════════════════
def market_main_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Lihat Semua Listing", callback_data="market_list_0")],
        [InlineKeyboardButton(text="💰 Jual Ore Saya",       callback_data="market_sell")],
        [InlineKeyboardButton(text="📦 Listing Saya",        callback_data="market_my_listings")],
        [InlineKeyboardButton(text="🏠 Menu Utama",          callback_data="main_menu")],
    ])


def market_listing_kb(listings: list, page: int = 0) -> InlineKeyboardMarkup:
    rows = []
    per_page = 5
    start = page * per_page
    chunk = listings[start: start + per_page]

    for lst in chunk:
        label = (
            f"{lst['ore_emoji']} {lst['ore_name']} x{lst['quantity']} "
            f"— {lst['price_total']:,}🪙 (@{lst['seller_username'] or lst['seller_name']})"
        )
        rows.append([InlineKeyboardButton(
            text=label[:64],
            callback_data=f"market_buy_{lst['id']}"
        )])

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="◀️", callback_data=f"market_list_{page-1}"))
    if start + per_page < len(listings):
        nav.append(InlineKeyboardButton(text="▶️", callback_data=f"market_list_{page+1}"))
    if nav:
        rows.append(nav)

    rows.append([InlineKeyboardButton(text="🔙 Market", callback_data="market_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def market_my_listings_kb(listings: list) -> InlineKeyboardMarkup:
    rows = []
    for lst in listings:
        label = f"❌ Batal: {lst['ore_emoji']} {lst['ore_name']} x{lst['quantity']} ({lst['price_total']:,}🪙)"
        rows.append([InlineKeyboardButton(
            text=label[:64],
            callback_data=f"market_cancel_{lst['id']}"
        )])
    if not rows:
        rows.append([InlineKeyboardButton(text="Tidak ada listing aktif", callback_data="noop")])
    rows.append([InlineKeyboardButton(text="🔙 Market", callback_data="market_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ══════════════════════════════════════════════════════════════
# PROFILE & LEADERBOARD
# ══════════════════════════════════════════════════════════════
def profile_kb(can_change: bool = True) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(text="📊 Statistik Mining", callback_data="mine_stats"),
            InlineKeyboardButton(text="🏅 Prestasi",         callback_data="achievements"),
        ],
        [InlineKeyboardButton(text="📦 Ore Inventory", callback_data="ore_inv_view")],
    ]
    if can_change:
        rows.append([InlineKeyboardButton(text="✏️ Ganti Nama", callback_data="profile_setname")])
    else:
        rows.append([InlineKeyboardButton(text="✏️ Ganti Nama (cooldown)", callback_data="profile_setname")])
    rows.append([InlineKeyboardButton(text="🏠 Menu Utama", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def leaderboard_kb(period: str = "weekly", field: str = "balance") -> InlineKeyboardMarkup:
    def btn(label, p, f):
        mark = "✅ " if (p == period and f == field) else ""
        return InlineKeyboardButton(text=f"{mark}{label}", callback_data=f"lb_{p}_{f}")

    return InlineKeyboardMarkup(inline_keyboard=[
        # Period selector — BUG FIX: preserve current field when switching period
        # (previously hardcoded to 'balance', so switching period always reset field)
        [
            InlineKeyboardButton(
                text=("📅 ✅Weekly" if period == "weekly" else "📅 Weekly"),
                callback_data=f"lb_weekly_{field}"
            ),
            InlineKeyboardButton(
                text=("🗓️ ✅Monthly" if period == "monthly" else "🗓️ Monthly"),
                callback_data=f"lb_monthly_{field}"
            ),
        ],
        # Field selector
        [btn("💰 Koin Didapat", period, "balance"),  btn("⛏️ Mining", period, "mine_count")],
        [btn("⚖️ Total KG", period, "total_kg"), btn("🪨 Total Ore", period, "ore_count")],
        # Actions
        [InlineKeyboardButton(text="🔄 Refresh", callback_data="lb_refresh")],
        [InlineKeyboardButton(text="🏠 Menu Utama", callback_data="main_menu")],
    ])


# ══════════════════════════════════════════════════════════════
# ADMIN
# ══════════════════════════════════════════════════════════════
def admin_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Statistik Bot", callback_data="admin_stats")],
        [InlineKeyboardButton(text="👥 Daftar User",   callback_data="admin_users")],
        [InlineKeyboardButton(text="🏠 Menu Utama",    callback_data="main_menu")],
    ])


# ══════════════════════════════════════════════════════════════
# VIP SHOP
# ══════════════════════════════════════════════════════════════
def vip_shop_kb(has_vip: bool = False) -> InlineKeyboardMarkup:
    from config import VIP_PRICES
    rows = []
    for pid, pdata in VIP_PRICES.items():
        rows.append([InlineKeyboardButton(
            text=f"👑 {pdata['label']} — Rp {pdata['price']:,}",
            callback_data=f"vip_buy_{pid}"
        )])
    rows.append([InlineKeyboardButton(text="📸 Kirim Bukti Transfer", callback_data="vip_proof")])
    rows.append([InlineKeyboardButton(text="🔙 Kembali ke Shop", callback_data="shop_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def vip_proof_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Saya Sudah Transfer", callback_data="vip_confirm_transfer")],
        [InlineKeyboardButton(text="🔙 Kembali", callback_data="shop_vip")],
    ])


def topup_shop_kb() -> InlineKeyboardMarkup:
    packages = [
        ("💰 Rp 10.000 → 10 Juta Koin",  "topup_10k"),
        ("💰 Rp 25.000 → 50 Juta Koin",  "topup_25k"),
        ("💰 Rp 50.000 → 100 Juta Koin",  "topup_50k"),
        ("💰 Rp 125.000 → 250 Juta Koin","topup_125k"),
        ("💰 Rp 250.000 → 500 Juta Koin","topup_250k"),
        ("💎 Rp 500.000 → 2,5 Milyar Koin","topup_500k"),
    ]
    rows = [[InlineKeyboardButton(text=t, callback_data=d)] for t, d in packages]
    rows.append([InlineKeyboardButton(text="📸 Kirim Bukti Transfer", callback_data="topup_proof")])
    rows.append([InlineKeyboardButton(text="🔙 Kembali ke Shop", callback_data="shop_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def topup_proof_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Saya Sudah Transfer", callback_data="topup_confirm_transfer")],
        [InlineKeyboardButton(text="🔙 Kembali", callback_data="shop_topup")],
    ])
