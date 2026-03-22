from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from config import (TOOLS, ITEMS, ZONES, ORES, TIER_COLORS, ADMIN_IDS,
                    BAG_SLOT_DEFAULT, BAG_SLOT_MAX, BAG_SLOT_STEP, BAG_SLOT_BASE_COST,
                    ENERGY_UPGRADE_MAX, ENERGY_UPGRADE_STEP, ENERGY_UPGRADE_BASE_COST,
                    format_kg)
from database import get_user, is_dynamic_admin, get_item_photo, get_vip_photo, get_topup_photo
from game import buy_tool, buy_item, unlock_zone, buy_bag_slot, buy_energy_upgrade
from keyboards import (shop_main_kb, shop_tools_kb, tool_detail_kb,
                        shop_items_kb, item_detail_kb, shop_zones_kb,
                        zone_detail_kb, vip_shop_kb, topup_shop_kb,
                        shop_upgrades_kb)

router = Router()


async def _is_admin(uid: int) -> bool:
    if uid in ADMIN_IDS:
        return True
    return await is_dynamic_admin(uid)


@router.message(F.text == "🏪 Shop")
@router.message(Command("shop"))
async def show_shop(message: Message):
    user = await get_user(message.from_user.id)
    balance_txt = f"\n💰 Saldo kamu: `{user['balance']:,}` koin" if user else ""
    await message.answer(
        f"🏪 *Toko Mining*{balance_txt}\n\nPilih kategori:",
        reply_markup=shop_main_kb(),
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "shop_menu")
async def cb_shop_menu(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    balance_txt = f"\n💰 Saldo kamu: `{user['balance']:,}` koin" if user else ""
    try:
        await callback.message.edit_text(
            f"🏪 *Toko Mining*{balance_txt}\n\nPilih kategori:",
            reply_markup=shop_main_kb(),
            parse_mode="Markdown"
        )
    except Exception:
        pass
    await callback.answer()


# ── TOOLS ─────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("shop_tools_"))
async def cb_shop_tools(callback: CallbackQuery):
    page = int(callback.data.split("_")[-1])
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.answer("Ketik /start dulu!")
        return
    text = (
        f"⛏️ *Daftar Alat Mining*\n"
        f"Dari Starter (Gratis) hingga Mythical!\n\n"
        f"✅ = Dimiliki | 🔒 = Level kurang | 💸 = Koin kurang\n"
        f"🪨 = Butuh Ore | 🛒 = Bisa dibeli\n\n"
        f"💰 Saldo: `{user['balance']:,}` koin\n\n"
        f"💡 Alat Legendary+ membutuhkan ore khusus!"
    )
    try:
        await callback.message.edit_text(
            text,
            reply_markup=shop_tools_kb(
                user["owned_tools"], user["level"], user["balance"],
                page, user.get("ore_inventory", {})
            ),
            parse_mode="Markdown"
        )
    except Exception:
        pass
    await callback.answer()


@router.callback_query(F.data.startswith("tool_detail_"))
async def cb_tool_detail(callback: CallbackQuery):
    tool_id = callback.data.replace("tool_detail_", "")
    tool = TOOLS.get(tool_id)
    user = await get_user(callback.from_user.id)
    if not tool or not user:
        await callback.answer("❌ Tidak ditemukan!")
        return

    owned      = tool_id in user["owned_tools"]
    is_current = user["current_tool"] == tool_id
    tier_icon  = TIER_COLORS.get(tool["tier"], "⬜")
    price_txt  = "✨ *GRATIS*" if tool["price"] == 0 else f"`{tool['price']:,}` koin"
    special_txt = f"\n🌟 *Special:* {tool['special']}" if tool.get("special") else ""

    # Ore requirements
    ore_req = tool.get("ore_req", {})
    ore_req_txt = ""
    if ore_req:
        ore_inv = user.get("ore_inventory", {})
        ore_lines = []
        for ore_id, qty_need in ore_req.items():
            ore = ORES.get(ore_id, {})
            have = ore_inv.get(ore_id, 0)
            status = "✅" if have >= qty_need else "❌"
            ore_lines.append(
                f"   {status} {ore.get('emoji','')} {ore.get('name', ore_id)}: "
                f"`{have}/{qty_need}`"
            )
        ore_req_txt = "\n🪨 *Butuh Ore:*\n" + "\n".join(ore_lines)

    # FIX 4: Hapus description dari detail alat, hanya tampilkan stats
    text = (
        f"{tool['emoji']} *{tool['name']}*\n"
        f"{tier_icon} Tier {tool['tier']} — {tool['tier_name']}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📊 *Statistik:*\n"
        f"   ⚡ Power      : `+{tool['power']}` koin/mine\n"
        f"   🚀 Speed      : `{tool['speed_mult']}x` multiplier\n"
        f"   ⏱️ Cooldown   : `{tool['speed_delay']}` detik\n"
        f"   💥 Crit Bonus : `+{int(tool['crit_bonus']*100)}%`\n"
        f"   🍀 Luck Bonus : `+{int(tool['luck_bonus']*100)}%`\n"
        f"   ⚡ Energy/mine: `-{tool['energy_cost']}`\n"
        f"   📏 Level Req  : `{tool['level_req']}`\n"
        f"   💰 Harga      : {price_txt}"
        f"{special_txt}"
        f"{ore_req_txt}\n\n"
        f"💰 Saldo kamu: `{user['balance']:,}` koin\n\n"
        f"{'✅ *Sudah dimiliki*' + (' _(Aktif)_' if is_current else '') if owned else '🛒 Belum dimiliki'}"
    )
    try:
        await callback.message.edit_text(
            text,
            reply_markup=tool_detail_kb(tool_id, owned, is_current),
            parse_mode="Markdown"
        )
    except Exception:
        pass
    await callback.answer()


@router.callback_query(F.data.startswith("buy_tool_"))
async def cb_buy_tool(callback: CallbackQuery):
    tool_id = callback.data.replace("buy_tool_", "")
    user_before = await get_user(callback.from_user.id)
    balance_before = user_before["balance"] if user_before else 0
    is_admin = await _is_admin(callback.from_user.id)
    ok, msg = await buy_tool(callback.from_user.id, tool_id, admin=is_admin)

    if ok:
        user_after = await get_user(callback.from_user.id)
        balance_after = user_after["balance"] if user_after else 0
        tool = TOOLS.get(tool_id, {})
        price = tool.get("price", 0)
        saldo_info = (
            f"\n\n💰 Saldo sebelum: `{balance_before:,}` koin"
            f"\n💸 Biaya: `-{price:,}` koin"
            f"\n💰 Saldo sekarang: `{balance_after:,}` koin"
        ) if not is_admin and price > 0 else ""
        await callback.answer(f"✅ {msg}{saldo_info}"[:200], show_alert=True)
        owned = tool_id in user_after["owned_tools"]
        is_current = user_after["current_tool"] == tool_id
        try:
            await callback.message.edit_reply_markup(
                reply_markup=tool_detail_kb(tool_id, owned, is_current)
            )
        except Exception:
            pass
    else:
        await callback.answer(msg[:200], show_alert=True)


# ── ITEMS ─────────────────────────────────────────────────────

@router.callback_query(F.data == "shop_items")
async def cb_shop_items(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    balance_txt = f"\n💰 Saldo kamu: `{user['balance']:,}` koin" if user else ""
    # FIX 6: Tampilkan foto item di list jika ada
    try:
        await callback.message.edit_text(
            f"🎒 *Item & Consumable*{balance_txt}\n\nBeli potion, scroll, dan item spesial!\n\n"
            f"Pilih item untuk melihat detail & foto:",
            reply_markup=shop_items_kb(),
            parse_mode="Markdown"
        )
    except Exception:
        pass
    await callback.answer()


@router.callback_query(F.data.startswith("item_detail_"))
async def cb_item_detail(callback: CallbackQuery):
    item_id = callback.data.replace("item_detail_", "")
    item = ITEMS.get(item_id)
    user = await get_user(callback.from_user.id)
    if not item or not user:
        await callback.answer("❌ Tidak ditemukan!")
        return

    qty = user["inventory"].get(item_id, 0)
    text = (
        f"{item['emoji']} *{item['name']}*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📝 {item['description']}\n\n"
        f"💰 Harga   : `{item['price']:,}` koin\n"
        f"📦 Dimiliki: `{qty}` buah\n"
        f"♻️ Stackable: {'Ya' if item['stackable'] else 'Tidak'}\n\n"
        f"💰 Saldo kamu: `{user['balance']:,}` koin"
    )

    # FIX 6: Cek foto item dan tampilkan
    item_photo = await get_item_photo(item_id)
    if item_photo:
        try:
            await callback.message.answer_photo(
                photo=item_photo["photo_id"],
                caption=text,
                reply_markup=item_detail_kb(item_id),
                parse_mode="Markdown"
            )
            await callback.message.delete()
        except Exception:
            try:
                await callback.message.edit_text(text, reply_markup=item_detail_kb(item_id), parse_mode="Markdown")
            except Exception:
                pass
    else:
        try:
            await callback.message.edit_text(text, reply_markup=item_detail_kb(item_id), parse_mode="Markdown")
        except Exception:
            pass
    await callback.answer()


@router.callback_query(F.data.startswith("buy_item_"))
async def cb_buy_item(callback: CallbackQuery):
    item_id = callback.data.replace("buy_item_", "")
    user_before = await get_user(callback.from_user.id)
    balance_before = user_before["balance"] if user_before else 0
    is_admin = await _is_admin(callback.from_user.id)
    ok, msg = await buy_item(callback.from_user.id, item_id, admin=is_admin)

    user_after = await get_user(callback.from_user.id)
    item = ITEMS.get(item_id)

    if ok:
        balance_after = user_after["balance"] if user_after else 0
        price = item.get("price", 0) if item else 0
        saldo_info = (
            f"\n\n💰 Sebelum: `{balance_before:,}` koin"
            f"\n💸 Biaya: `-{price:,}` koin"
            f"\n💰 Sesudah: `{balance_after:,}` koin"
        ) if not is_admin else ""
        await callback.answer(f"✅ {msg}{saldo_info}"[:200], show_alert=True)
    else:
        await callback.answer(msg[:200], show_alert=True)

    if item and user_after:
        qty = user_after["inventory"].get(item_id, 0)
        text = (
            f"{item['emoji']} *{item['name']}*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📝 {item['description']}\n\n"
            f"💰 Harga   : `{item['price']:,}` koin\n"
            f"📦 Dimiliki: `{qty}` buah\n"
            f"♻️ Stackable: {'Ya' if item['stackable'] else 'Tidak'}\n\n"
            f"💰 Saldo kamu: `{user_after['balance']:,}` koin"
        )
        item_photo = await get_item_photo(item_id)
        if item_photo:
            try:
                await callback.message.answer_photo(
                    photo=item_photo["photo_id"],
                    caption=text,
                    reply_markup=item_detail_kb(item_id),
                    parse_mode="Markdown"
                )
                await callback.message.delete()
            except Exception:
                try:
                    await callback.message.edit_text(text, reply_markup=item_detail_kb(item_id), parse_mode="Markdown")
                except Exception:
                    pass
        else:
            try:
                await callback.message.edit_text(text, reply_markup=item_detail_kb(item_id), parse_mode="Markdown")
            except Exception:
                pass


# ── ZONES ─────────────────────────────────────────────────────

@router.callback_query(F.data == "shop_zones")
async def cb_shop_zones(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.answer("Ketik /start!")
        return
    try:
        await callback.message.edit_text(
            f"🌍 *Buka Zona Mining Baru*\n\n"
            f"Zona berbeda memberikan ore berbeda dan lebih berharga!\n\n"
            f"💰 Saldo kamu: `{user['balance']:,}` koin",
            reply_markup=shop_zones_kb(user["unlocked_zones"], user["level"], user["balance"]),
            parse_mode="Markdown"
        )
    except Exception:
        pass
    await callback.answer()


@router.callback_query(F.data.startswith("zone_detail_"))
async def cb_zone_detail(callback: CallbackQuery):
    zone_id = callback.data.replace("zone_detail_", "")
    zone = ZONES.get(zone_id)
    user = await get_user(callback.from_user.id)
    if not zone or not user:
        await callback.answer("❌ Tidak ditemukan!")
        return

    unlocked  = zone_id in user["unlocked_zones"]
    is_active = user.get("current_zone") == zone_id
    bonus_txt = ""
    if zone["ore_bonus"]:
        for oid, mult in zone["ore_bonus"].items():
            ore = ORES.get(oid, {})
            bonus_txt += f"\n   {ore.get('emoji','')} {ore.get('name', oid)}: `{mult}x`"

    cost_txt = "✨ *Gratis*" if zone["unlock_cost"] == 0 else f"`{zone['unlock_cost']:,}` koin"
    # FIX 4: Hapus desc zona dari detail, hanya tampilkan stats
    text = (
        f"{zone['name']}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🔓 Level Req : `{zone['level_req']}`\n"
        f"💰 Biaya     : {cost_txt}\n"
        f"📊 Ore Bonus :{bonus_txt if bonus_txt else ' Tidak ada'}\n\n"
        f"💰 Saldo kamu: `{user['balance']:,}` koin\n\n"
        f"{'✅ *Sudah terbuka*' + (' _(Aktif)_' if is_active else '') if unlocked else '🔒 Belum dibuka'}"
    )
    try:
        await callback.message.edit_text(
            text,
            reply_markup=zone_detail_kb(zone_id, unlocked, is_active),
            parse_mode="Markdown"
        )
    except Exception:
        pass
    await callback.answer()


@router.callback_query(F.data.startswith("unlock_zone_"))
async def cb_unlock_zone(callback: CallbackQuery):
    zone_id = callback.data.replace("unlock_zone_", "")
    user_before = await get_user(callback.from_user.id)
    balance_before = user_before["balance"] if user_before else 0
    is_admin = await _is_admin(callback.from_user.id)
    ok, msg = await unlock_zone(callback.from_user.id, zone_id, admin=is_admin)

    if ok:
        user_after = await get_user(callback.from_user.id)
        balance_after = user_after["balance"] if user_after else 0
        zone = ZONES.get(zone_id, {})
        cost = zone.get("unlock_cost", 0)
        saldo_info = (
            f"\n\n💰 Sebelum: `{balance_before:,}` koin"
            f"\n💸 Biaya: `-{cost:,}` koin"
            f"\n💰 Sesudah: `{balance_after:,}` koin"
        ) if not is_admin and cost > 0 else ""
        await callback.answer(f"✅ {msg}{saldo_info}"[:200], show_alert=True)
        unlocked  = zone_id in user_after["unlocked_zones"]
        is_active = user_after.get("current_zone") == zone_id
        try:
            await callback.message.edit_reply_markup(
                reply_markup=zone_detail_kb(zone_id, unlocked, is_active)
            )
        except Exception:
            pass
    else:
        await callback.answer(msg[:200], show_alert=True)


# ── UPGRADES (Slot Bag & Energy) ──────────────────────────────

def _build_upgrades_text(cur_slots: int, cur_energy: int, balance: int) -> str:
    steps_slot   = (cur_slots - BAG_SLOT_DEFAULT) // BAG_SLOT_STEP
    price_slot   = BAG_SLOT_BASE_COST + (steps_slot * 2000)
    steps_energy = (cur_energy - 500) // ENERGY_UPGRADE_STEP
    price_energy = ENERGY_UPGRADE_BASE_COST + (steps_energy * 5000)
    slot_status   = "✅ *MAKS*" if cur_slots >= BAG_SLOT_MAX else f"`{price_slot:,}` koin"
    energy_status = "✅ *MAKS*" if cur_energy >= ENERGY_UPGRADE_MAX else f"`{price_energy:,}` koin"
    return (
        f"⬆️ *Upgrade Karakter*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🎒 *Slot Bag*\n"
        f"   Status : `{cur_slots}/{BAG_SLOT_MAX}` slot\n"
        f"   +{BAG_SLOT_STEP} slot per upgrade\n"
        f"   Harga   : {slot_status}\n\n"
        f"⚡ *Max Energy*\n"
        f"   Status : `{cur_energy}/{ENERGY_UPGRADE_MAX}`\n"
        f"   +{ENERGY_UPGRADE_STEP} energy per upgrade\n"
        f"   Harga   : {energy_status}\n\n"
        f"💰 Saldo kamu : `{balance:,}` koin"
    )


@router.callback_query(F.data == "shop_upgrades")
async def cb_shop_upgrades(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.answer("Ketik /start!")
        return
    cur_slots  = user.get("bag_slots", BAG_SLOT_DEFAULT)
    cur_energy = user.get("max_energy", 500)
    balance    = user.get("balance", 0)
    text = _build_upgrades_text(cur_slots, cur_energy, balance)
    try:
        await callback.message.edit_text(
            text,
            reply_markup=shop_upgrades_kb(cur_slots, cur_energy, balance),
            parse_mode="Markdown"
        )
    except Exception:
        pass
    await callback.answer()


@router.callback_query(F.data == "shop_buy_bag_slot")
async def cb_shop_buy_bag_slot(callback: CallbackQuery):
    user_before = await get_user(callback.from_user.id)
    balance_before = user_before["balance"] if user_before else 0
    is_admin = await _is_admin(callback.from_user.id)
    ok, msg = await buy_bag_slot(callback.from_user.id, admin=is_admin)
    user = await get_user(callback.from_user.id)
    if ok and user:
        saldo_info = (
            f"\n💰 Sebelum: `{balance_before:,}` → `{user['balance']:,}` koin"
        ) if not is_admin else ""
        await callback.answer(f"✅ {msg}{saldo_info}"[:200], show_alert=True)
        cur_slots  = user.get("bag_slots", BAG_SLOT_DEFAULT)
        cur_energy = user.get("max_energy", 500)
        balance    = user.get("balance", 0)
        try:
            await callback.message.edit_text(
                _build_upgrades_text(cur_slots, cur_energy, balance),
                reply_markup=shop_upgrades_kb(cur_slots, cur_energy, balance),
                parse_mode="Markdown"
            )
        except Exception:
            pass
    else:
        await callback.answer(msg[:200], show_alert=True)


@router.callback_query(F.data == "shop_buy_energy")
async def cb_shop_buy_energy(callback: CallbackQuery):
    user_before = await get_user(callback.from_user.id)
    balance_before = user_before["balance"] if user_before else 0
    is_admin = await _is_admin(callback.from_user.id)
    ok, msg = await buy_energy_upgrade(callback.from_user.id, admin=is_admin)
    user = await get_user(callback.from_user.id)
    if ok and user:
        saldo_info = (
            f"\n💰 Sebelum: `{balance_before:,}` → `{user['balance']:,}` koin"
        ) if not is_admin else ""
        await callback.answer(f"✅ {msg}{saldo_info}"[:200], show_alert=True)
        cur_slots  = user.get("bag_slots", BAG_SLOT_DEFAULT)
        cur_energy = user.get("max_energy", 500)
        balance    = user.get("balance", 0)
        try:
            await callback.message.edit_text(
                _build_upgrades_text(cur_slots, cur_energy, balance),
                reply_markup=shop_upgrades_kb(cur_slots, cur_energy, balance),
                parse_mode="Markdown"
            )
        except Exception:
            pass
    else:
        await callback.answer(msg[:200], show_alert=True)
