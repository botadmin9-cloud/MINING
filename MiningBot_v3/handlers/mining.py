import asyncio
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from config import ADMIN_IDS, TOOLS, ZONES, ORES, ORE_TIER_COLORS
from database import get_user, get_zone_photo, get_tool_photo, set_mining_multi_status
from game import (perform_mine, build_mine_result_text, regen_energy,
                   energy_full_in, equip_tool, set_zone,
                   get_mine_cooldown_seconds, check_mine_cooldown, is_vip_active)
from config import format_kg, xp_for_level
from keyboards import mine_action_kb, equip_menu_kb, zone_menu_kb, main_menu_kb

router = Router()


def _is_admin(uid: int) -> bool:
    return uid in ADMIN_IDS


def _zone_ore_list(zone_id: str) -> str:
    """Buat daftar ore yang bisa didapat di zona ini."""
    zone = ZONES.get(zone_id, {})
    ore_bonus = zone.get("ore_bonus", {})
    if not ore_bonus:
        # Zona surface - ore dasar
        return "🪨 Kerikil, ⬛ Batu Bara, 🗿 Batu Biasa, ⚙️ Bijih Besi, dll."
    ore_names = []
    for ore_id in list(ore_bonus.keys())[:6]:
        ore = ORES.get(ore_id, {})
        name = ore.get("name", ore_id)
        ore_names.append(name)
    return ", ".join(ore_names) if ore_names else "Berbagai ore"


async def _mine_panel(user_id: int) -> tuple:
    """Return (text, photo_id_or_None)"""
    user = await get_user(user_id)
    if not user:
        return "❌ Ketik /start", None

    # Cek apakah sedang mining multi
    if user.get("is_mining_multi") and not _is_admin(user_id):
        multi_type = user.get("mining_multi_type", "?")
        return (
            f"⛏️ *Sedang Mining {multi_type}...*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"⏳ Proses mining sedang berjalan!\n"
            f"🔄 Tidak bisa memulai mining baru hingga selesai.\n\n"
            f"💡 Harap tunggu hingga mining {multi_type} selesai."
        ), None

    user = await regen_energy(user)
    tool = TOOLS.get(user["current_tool"], TOOLS["stone_pick"])
    zone_id = user.get("current_zone", "surface")
    zone = ZONES.get(zone_id, ZONES["surface"])
    is_admin = _is_admin(user_id)
    cooldown = 1 if is_admin else get_mine_cooldown_seconds(user, is_admin)  # FIX: teruskan is_admin
    vip_active = is_vip_active(user)
    admin_tag = " 👑 *[ADMIN — Gratis & Cepat]*" if is_admin else (" ✨ *[VIP]*" if vip_active else "")

    ore_list = _zone_ore_list(zone_id)

    # ── Hitung sisa waktu cooldown ─────────────────────────────
    cooldown_status = ""
    if not is_admin:
        last_mine = user.get("last_mine_time")
        if last_mine:
            try:
                elapsed = (datetime.now() - datetime.fromisoformat(last_mine)).total_seconds()
                remaining = cooldown - elapsed
                if remaining > 0:
                    cooldown_status = f"\n⏳ *Siap mining dalam: `{remaining:.1f}` detik*"
                else:
                    cooldown_status = "\n✅ *Siap mining sekarang!*"
            except Exception:
                cooldown_status = "\n✅ *Siap mining sekarang!*"
        else:
            cooldown_status = "\n✅ *Siap mining sekarang!*"

    text = (
        f"⛏️ *Panel Mining*{admin_tag}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🔧 *Alat Aktif:*\n"
        f"   {tool['emoji']} *{tool['name']}* (Tier {tool['tier']} — {tool['tier_name']})\n"
        f"   ├ ⚡ Power    : `+{tool['power']}` (base)\n"
        f"   ├ 🚀 Speed    : `{tool['speed_mult']}x`\n"
        f"   ├ ⏱️ Cooldown : `{cooldown}` detik\n"
        f"   ├ 💥 Crit     : `{int(tool['crit_bonus']*100)}%` bonus\n"
        f"   ├ 🍀 Luck     : `{int(tool['luck_bonus']*100)}%` bonus\n"
        f"   └ ⚡ Biaya    : `-{tool['energy_cost']}` energy\n\n"
        f"📍 *Zona:* {zone['name']}\n"
        f"   └ {zone['desc']}\n"
        f"   🪨 *Ore di zona ini:* _{ore_list}_\n\n"
        f"⚡ Energy: `{user['energy']}/{user['max_energy']}` "
        f"(penuh dalam *{energy_full_in(user)}*)\n"
        f"💰 Saldo : `{user['balance']:,}` koin"
        f"{cooldown_status}\n\n"
        f"Pilih aksi mining:"
    )

    # Cek foto zona
    zone_photo = await get_zone_photo(zone_id)
    photo_id = zone_photo["photo_id"] if zone_photo else None

    return text, photo_id


@router.message(F.text == "⛏️ Mining")
@router.message(Command("mine"))
async def show_mine(message: Message):
    result = await _mine_panel(message.from_user.id)
    text, photo_id = result if isinstance(result, tuple) else (result, None)
    kb = mine_action_kb()
    if photo_id:
        await message.answer_photo(photo=photo_id, caption=text,
                                   reply_markup=kb, parse_mode="Markdown")
    else:
        await message.answer(text, reply_markup=kb, parse_mode="Markdown")


@router.callback_query(F.data == "mine_menu")
async def cb_mine_menu(callback: CallbackQuery):
    result = await _mine_panel(callback.from_user.id)
    text, photo_id = result if isinstance(result, tuple) else (result, None)
    kb = mine_action_kb()
    try:
        if photo_id:
            await callback.message.answer_photo(photo=photo_id, caption=text,
                                                  reply_markup=kb, parse_mode="Markdown")
            await callback.message.delete()
        else:
            try:
                await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
            except Exception:
                pass
    except Exception:
        await callback.message.answer(text, reply_markup=kb, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "do_mine")
async def cb_do_mine(callback: CallbackQuery):
    uid = callback.from_user.id
    is_admin = _is_admin(uid)
    user = await get_user(uid)

    if not user:
        await callback.answer("❌ Ketik /start", show_alert=True)
        return

    # Blokir jika sedang mining multi
    if user.get("is_mining_multi") and not is_admin:
        mt = user.get("mining_multi_type", "multi")
        await callback.answer(
            f"⏳ Sedang mining {mt}! Tunggu hingga selesai.",
            show_alert=True
        )
        return

    if not is_admin:
        can_mine, cd_msg = await check_mine_cooldown(user, is_admin)
        if not can_mine:
            await callback.answer(cd_msg, show_alert=True)
            return

    result = await perform_mine(uid, is_admin=is_admin)
    if result["ok"]:
        text = build_mine_result_text(result)
    else:
        text = result["msg"]

    try:
        await callback.message.edit_text(text, reply_markup=mine_action_kb(), parse_mode="Markdown")
    except Exception:
        pass
    await callback.answer()


async def _do_mine_multi(callback: CallbackQuery, count: int):
    uid = callback.from_user.id
    is_admin = _is_admin(uid)

    user = await get_user(uid)
    if not user:
        await callback.answer("❌ Ketik /start", show_alert=True)
        return

    # Blokir jika sudah sedang mining multi
    if user.get("is_mining_multi") and not is_admin:
        mt = user.get("mining_multi_type", "multi")
        await callback.answer(
            f"⏳ Sedang mining {mt}! Tunggu hingga selesai.",
            show_alert=True
        )
        return

    multi_label = f"x{count}"
    await callback.answer(f"⛏️ Mining {multi_label}... Harap tunggu!")

    # Set status mining multi
    if not is_admin:
        await set_mining_multi_status(uid, True, multi_label)

    # Update pesan awal
    try:
        await callback.message.edit_text(
            f"⛏️ *Sedang Mining {multi_label}...*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"⏳ Proses mining sedang berjalan...\n"
            f"🔄 Tidak bisa memulai mining baru hingga selesai.\n\n"
            f"💡 Harap tunggu dengan sabar!",
            reply_markup=None,
            parse_mode="Markdown"
        )
    except Exception:
        pass

    total_xp   = 0
    total_kg   = 0.0
    ores_found = {}
    specials   = []
    crits = luckies = level_ups = 0
    new_ach    = []
    last_error = None

    try:
        for i in range(count):
            user = await get_user(uid)
            if not user:
                break
            if not is_admin:
                can_mine, _ = await check_mine_cooldown(user, is_admin)
                if not can_mine:
                    cd = get_mine_cooldown_seconds(user, is_admin)
                    await asyncio.sleep(cd)

            r = await perform_mine(uid, is_admin=is_admin)
            if not r["ok"]:
                last_error = r["msg"]
                break
            total_xp   += r["xp_gain"]
            total_kg   += r.get("ore_kg", 0.0)
            ore_key = f"{r['ore']['emoji']} {r['ore']['name']}"
            ores_found[ore_key] = ores_found.get(ore_key, 0) + 1
            if r["is_crit"]:    crits += 1
            if r["is_lucky"]:   luckies += 1
            if r["special_hit"]: specials.append(r["special_hit"])
            if r["leveled_up"]: level_ups += 1
            new_ach.extend(r.get("new_achievements", []))

            if not is_admin and i < count - 1:
                # FIX: Gunakan cooldown_secs dari result (sudah hitung buff terkini)
                cd = r.get("cooldown_secs") or get_mine_cooldown_seconds(user, is_admin)
                await asyncio.sleep(cd)
    except Exception as _e:
        last_error = f"⚠️ Mining dihentikan karena error: {_e}"
    finally:
        # Selalu hapus status mining, bahkan jika terjadi exception
        if not is_admin:
            await set_mining_multi_status(uid, False)

    ore_lines = "\n".join(f"   {k}: x{v}" for k, v in ores_found.items()) or "   Tidak ada"
    user = await get_user(uid)

    lines = [
        f"✅ *Mining {multi_label} Selesai!*",
        "━━━━━━━━━━━━━━━━━━━━",
        "",
        f"🪨 *Bijih Ditemukan:*\n{ore_lines}",
        "",
        f"⭐ Total XP   : `+{total_xp:,}`",
        f"⚖️ Total KG   : `{format_kg(total_kg)}`",
        f"💥 Critical   : {crits}x",
        f"🍀 Lucky      : {luckies}x",
    ]
    if specials:
        lines.append(f"🌟 Special: {', '.join(set(specials))}")
    if level_ups:
        lines.append(f"🎉 *Level UP x{level_ups}!*")
    for a in new_ach:
        lines.append(f"🏅 Prestasi: *{a['name']}*")
    if last_error:
        lines.append(f"\n⚠️ {last_error}")
    if user:
        lines.append(f"\n💰 Saldo: `{user['balance']:,}` koin")
        lines.append(f"⚡ Energy: `{user['energy']}/{user['max_energy']}`")

    text = "\n".join(lines)
    try:
        await callback.message.edit_text(text, reply_markup=mine_action_kb(), parse_mode="Markdown")
    except Exception:
        try:
            await callback.message.answer(text, reply_markup=mine_action_kb(), parse_mode="Markdown")
        except Exception:
            pass


@router.callback_query(F.data == "do_mine_5")
async def cb_do_mine_5(callback: CallbackQuery):
    await _do_mine_multi(callback, 5)


@router.callback_query(F.data == "do_mine_10")
async def cb_do_mine_10(callback: CallbackQuery):
    await _do_mine_multi(callback, 10)


@router.callback_query(F.data == "do_mine_25")
async def cb_do_mine_25(callback: CallbackQuery):
    await _do_mine_multi(callback, 25)


@router.callback_query(F.data == "do_mine_50")
async def cb_do_mine_50(callback: CallbackQuery):
    await _do_mine_multi(callback, 50)


@router.callback_query(F.data == "equip_menu")
async def cb_equip_menu(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.answer("❌ Ketik /start")
        return
    try:
        await callback.message.edit_text(
            "⚒️ *Pilih Alat untuk Dipakai:*",
            reply_markup=equip_menu_kb(user["owned_tools"], user["current_tool"]),
            parse_mode="Markdown"
        )
    except Exception:
        pass
    await callback.answer()


@router.callback_query(F.data.startswith("equip_"))
async def cb_equip(callback: CallbackQuery):
    tool_id = callback.data.replace("equip_", "")
    ok, msg = await equip_tool(callback.from_user.id, tool_id)
    await callback.answer(msg[:200], show_alert=not ok)
    if ok:
        user = await get_user(callback.from_user.id)
        # Cek dan tampilkan foto alat jika ada
        tool_photo = await get_tool_photo(tool_id)
        tool = TOOLS.get(tool_id, {})
        text = f"⚒️ *Ganti Alat*\n\n{msg}"
        kb = equip_menu_kb(user["owned_tools"], user["current_tool"])
        if tool_photo:
            try:
                await callback.message.answer_photo(
                    photo=tool_photo["photo_id"],
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
                pass


@router.callback_query(F.data == "zone_menu")
async def cb_zone_menu(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.answer("❌ Ketik /start")
        return
    try:
        await callback.message.edit_text(
            "📍 *Pilih Zona Mining:*\n_(Zona berbeda = ore berbeda)_",
            reply_markup=zone_menu_kb(user["unlocked_zones"], user.get("current_zone", "surface")),
            parse_mode="Markdown"
        )
    except Exception:
        pass
    await callback.answer()


@router.callback_query(F.data.startswith("set_zone_"))
async def cb_set_zone(callback: CallbackQuery):
    zone_id = callback.data.replace("set_zone_", "")
    ok, msg = await set_zone(callback.from_user.id, zone_id)
    await callback.answer(msg[:200], show_alert=not ok)
    if ok:
        user = await get_user(callback.from_user.id)
        zone = ZONES.get(zone_id, {})
        ore_list = _zone_ore_list(zone_id)
        # Cek foto zona
        zone_photo = await get_zone_photo(zone_id)
        text = (
            f"📍 *Zona Mining*\n\n{msg}\n\n"
            f"🪨 *Ore di zona ini:*\n_{ore_list}_"
        )
        kb = zone_menu_kb(user["unlocked_zones"], user.get("current_zone", "surface"))
        if zone_photo:
            try:
                await callback.message.answer_photo(
                    photo=zone_photo["photo_id"],
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
                pass


@router.message(Command("rare_ore"))
async def cmd_rare_ore(message: Message):
    """Lihat semua ore rare (bisa dilihat semua pemain)."""
    tier_order = ["legendary", "mythical", "cosmic", "divine", "epic"]
    lines = ["💎 *Daftar Ore Rare di Mining Bot*\n"]
    for tier in tier_order:
        tier_ores = [(k, v) for k, v in ORES.items() if v.get("tier") == tier]
        if not tier_ores:
            continue
        tier_icon = ORE_TIER_COLORS.get(tier, "⬜")
        tier_label = tier.upper()
        lines.append(f"\n{tier_icon} *{tier_label}*")
        for ore_id, ore in tier_ores:
            rarity = ore.get("rarity", 0)
            value = ore.get("value", 0)
            lines.append(
                f"   {ore['emoji']} *{ore['name']}*\n"
                f"   └ Rarity: `{rarity}%` | Nilai: `{value:,}` koin/unit"
            )
    text = "\n".join(lines)
    if len(text) > 4096:
        text = text[:4090] + "\n..."
    await message.answer(text, parse_mode="Markdown")
