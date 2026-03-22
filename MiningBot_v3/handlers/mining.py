import asyncio
import time
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from config import ADMIN_IDS, TOOLS, ZONES, ORES, ORE_TIER_COLORS
from database import get_user, get_zone_photo, get_tool_photo, set_mining_multi_status, get_ore_photo
from game import (perform_mine, build_mine_result_text, regen_energy,
                   energy_full_in, equip_tool, set_zone,
                   get_mine_cooldown_seconds, check_mine_cooldown, is_vip_active)
from config import format_kg, xp_for_level
from keyboards import mine_action_kb, equip_menu_kb, zone_menu_kb, main_menu_kb
from middlewares import register_message_owner

router = Router()


def _is_admin(uid: int) -> bool:
    return uid in ADMIN_IDS


def _zone_ore_list(zone_id: str) -> str:
    zone = ZONES.get(zone_id, {})
    ore_bonus = zone.get("ore_bonus", {})
    if not ore_bonus:
        return "🪨 Kerikil, ⬛ Batu Bara, 🗿 Batu Biasa, ⚙️ Bijih Besi, dll."
    ore_names = []
    for ore_id in list(ore_bonus.keys())[:6]:
        ore = ORES.get(ore_id, {})
        name = ore.get("name", ore_id)
        ore_names.append(name)
    return ", ".join(ore_names) if ore_names else "Berbagai ore"


async def _mine_panel(user_id: int) -> tuple:
    user = await get_user(user_id)
    if not user:
        return "❌ Ketik /start", None

    if user.get("is_mining_multi") and not _is_admin(user_id):
        multi_type = user.get("mining_multi_type", "?")
        last_mine = user.get("last_mine_time")
        cd_secs = get_mine_cooldown_seconds(user, False)
        wait_txt = ""
        if last_mine:
            try:
                elapsed = (datetime.now() - datetime.fromisoformat(last_mine)).total_seconds()
                remaining = max(0, cd_secs - elapsed)
                if remaining > 0:
                    h = int(remaining) // 3600
                    m = (int(remaining) % 3600) // 60
                    s = int(remaining) % 60
                    if h > 0:
                        time_str = f"{h}j {m}m {s}d"
                    elif m > 0:
                        time_str = f"{m}m {s}d"
                    else:
                        time_str = f"{s} detik"
                    wait_txt = f"\n⏱️ Mining berikutnya dalam: `{time_str}`"
            except Exception:
                pass
        return (
            f"⛏️ *Sedang Mining {multi_type}...*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"⏳ Proses mining sedang berjalan!\n"
            f"🔄 Tidak bisa memulai mining baru hingga selesai."
            f"{wait_txt}\n\n"
            f"💡 Harap tunggu hingga mining {multi_type} selesai."
        ), None

    user = await regen_energy(user)
    tool = TOOLS.get(user["current_tool"], TOOLS["stone_pick"])
    zone_id = user.get("current_zone", "surface")
    zone = ZONES.get(zone_id, ZONES["surface"])
    is_admin = _is_admin(user_id)
    cooldown = 1 if is_admin else get_mine_cooldown_seconds(user, is_admin)
    vip_active = is_vip_active(user)
    admin_tag = " 👑 *[ADMIN — Gratis & Cepat]*" if is_admin else (" ✨ *[VIP]*" if vip_active else "")

    ore_list = _zone_ore_list(zone_id)

    cooldown_status = ""
    if not is_admin:
        last_mine = user.get("last_mine_time")
        if last_mine:
            try:
                elapsed = (datetime.now() - datetime.fromisoformat(last_mine)).total_seconds()
                remaining = cooldown - elapsed
                if remaining > 0:
                    r_int = int(remaining)
                    h = r_int // 3600
                    m = (r_int % 3600) // 60
                    s = r_int % 60
                    if h > 0:
                        time_str = f"{h}j {m}m {s}d"
                    elif m > 0:
                        time_str = f"{m}m {s}d"
                    else:
                        time_str = f"{s} detik"
                    cooldown_status = f"\n⏳ *Siap mining dalam: `{time_str}`*"
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
        f"   🪨 *Ore di zona ini:* _{ore_list}_\n\n"
        f"⚡ Energy: `{user['energy']}/{user['max_energy']}` "
        f"(penuh dalam *{energy_full_in(user)}*)\n"
        f"💰 Saldo : `{user['balance']:,}` koin"
        f"{cooldown_status}\n\n"
        f"Pilih aksi mining:"
    )

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
        _sent = await message.answer_photo(photo=photo_id, caption=text,
                                   reply_markup=kb, parse_mode="Markdown")
        if _sent: register_message_owner(_sent.chat.id, _sent.message_id, message.from_user.id)
    else:
        _sent = await message.answer(text, reply_markup=kb, parse_mode="Markdown")
        if _sent: register_message_owner(_sent.chat.id, _sent.message_id, message.from_user.id)


@router.callback_query(F.data == "mine_menu")
async def cb_mine_menu(callback: CallbackQuery):
    result = await _mine_panel(callback.from_user.id)
    text, photo_id = result if isinstance(result, tuple) else (result, None)
    kb = mine_action_kb()
    try:
        if photo_id:
            _sent = await callback.message.answer_photo(photo=photo_id, caption=text,
                                                  reply_markup=kb, parse_mode="Markdown")
            if _sent: register_message_owner(_sent.chat.id, _sent.message_id, callback.from_user.id)
            await callback.message.delete()
        else:
            try:
                await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
            except Exception:
                _sent = await callback.message.answer(text, reply_markup=kb, parse_mode="Markdown")
                if _sent: register_message_owner(_sent.chat.id, _sent.message_id, callback.from_user.id)
    except Exception:
        _sent = await callback.message.answer(text, reply_markup=kb, parse_mode="Markdown")
        if _sent: register_message_owner(_sent.chat.id, _sent.message_id, callback.from_user.id)
    await callback.answer()


@router.callback_query(F.data == "do_mine")
async def cb_do_mine(callback: CallbackQuery):
    uid = callback.from_user.id
    is_admin = _is_admin(uid)
    user = await get_user(uid)

    if not user:
        await callback.answer("❌ Ketik /start", show_alert=True)
        return

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
        # Tampilkan foto ore yang didapat (ore_id sudah tersimpan langsung di result)
        ore_id = result.get("ore_id")
        ore_photo = await get_ore_photo(ore_id) if ore_id else None
        if ore_photo:
            try:
                _sent = await callback.message.answer_photo(
                    photo=ore_photo["photo_id"],
                    caption=text,
                    reply_markup=mine_action_kb(),
                    parse_mode="Markdown"
                )
                if _sent: register_message_owner(_sent.chat.id, _sent.message_id, callback.from_user.id)
                await callback.message.delete()
                await callback.answer()
                return
            except Exception:
                pass
        # Fallback: tampilkan sebagai teks biasa (tanpa foto)
        try:
            await callback.message.edit_text(text, reply_markup=mine_action_kb(), parse_mode="Markdown")
        except Exception:
            _sent = await callback.message.answer(text, reply_markup=mine_action_kb(), parse_mode="Markdown")
            if _sent: register_message_owner(_sent.chat.id, _sent.message_id, callback.from_user.id)
        await callback.answer()
    else:
        text = result["msg"]
        try:
            await callback.message.edit_text(text, reply_markup=mine_action_kb(), parse_mode="Markdown")
        except Exception:
            _sent = await callback.message.answer(text, reply_markup=mine_action_kb(), parse_mode="Markdown")
            if _sent: register_message_owner(_sent.chat.id, _sent.message_id, callback.from_user.id)
        await callback.answer()


def _format_duration(seconds: float) -> str:
    seconds = max(0, int(seconds))
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0:
        return f"{h}j {m}m {s}d"
    elif m > 0:
        return f"{m}m {s}d"
    else:
        return f"{s} detik"


async def _do_mine_multi(callback: CallbackQuery, count: int):
    uid = callback.from_user.id
    is_admin = _is_admin(uid)

    user = await get_user(uid)
    if not user:
        await callback.answer("❌ Ketik /start", show_alert=True)
        return

    # GUARD #1: Cek apakah sedang mining multi
    if user.get("is_mining_multi") and not is_admin:
        mt = user.get("mining_multi_type", "multi")
        # GUARD #1b: Auto-reset jika stuck > 30 menit (bot restart, crash, dll)
        started_raw = user.get("mining_multi_started")
        is_stuck = False
        if started_raw:
            try:
                started_dt = datetime.fromisoformat(started_raw)
                stuck_secs = (datetime.now() - started_dt).total_seconds()
                if stuck_secs > 1800:  # 30 menit
                    is_stuck = True
            except Exception:
                is_stuck = True
        if is_stuck:
            await set_mining_multi_status(uid, False)
        else:
            await callback.answer(
                f"⏳ Sedang mining {mt}! Tunggu hingga selesai.",
                show_alert=True
            )
            return

    # GUARD #2: Cek cooldown sebelum mulai (bukan admin)
    if not is_admin:
        can_mine, cd_msg = await check_mine_cooldown(user, is_admin)
        if not can_mine:
            await callback.answer(cd_msg[:200], show_alert=True)
            return

    # GUARD #3: Cek energy cukup sebelum mulai
    from config import TOOLS as _TOOLS
    tool_id = user.get("current_tool", "stone_pick")
    tool = _TOOLS.get(tool_id, _TOOLS["stone_pick"])
    energy_cost = tool.get("energy_cost", 1)
    if not is_admin and user.get("energy", 0) < energy_cost:
        await callback.answer(
            f"⚡ Energy tidak cukup! ({user.get('energy',0)}/{user.get('max_energy',100)})\n"
            f"Butuh minimal {energy_cost} energy.",
            show_alert=True
        )
        return

    # GUARD #4: Cek bag tidak penuh sebelum mulai
    if not is_admin:
        ore_inv = user.get("ore_inventory", {})
        total_ore_in_bag = sum(ore_inv.values())
        bag_slots = user.get("bag_slots", 50)
        if total_ore_in_bag >= bag_slots:
            await callback.answer(
                f"🎒 Bag penuh! ({total_ore_in_bag}/{bag_slots} slot)\n"
                f"Jual ore dulu di Market sebelum mining.",
                show_alert=True
            )
            return

    multi_label = f"x{count}"
    cd_secs = get_mine_cooldown_seconds(user, is_admin)
    total_wait_secs = cd_secs * count if not is_admin else 0
    eta_str = _format_duration(total_wait_secs) if total_wait_secs > 0 else "Sebentar"

    # GUARD #5: Set flag SEBELUM callback.answer agar tidak ada double-tap
    if not is_admin:
        await set_mining_multi_status(uid, True, multi_label)

    await callback.answer(f"⛏️ Mining {multi_label}... Harap tunggu!")

    try:
        await callback.message.edit_text(
            f"⛏️ *Sedang Mining {multi_label}...*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"⏳ Proses mining sedang berjalan...\n"
            f"🔄 Tidak bisa memulai mining baru hingga selesai.\n\n"
            f"🕐 *Estimasi waktu:* `{eta_str}`\n"
            f"⏱️ Cooldown per mine: `{cd_secs}` detik\n\n"
            f"💡 Harap tunggu dengan sabar!",
            reply_markup=None,
            parse_mode="Markdown"
        )
    except Exception:
        pass

    total_xp   = 0
    total_kg   = 0.0
    ores_found = {}
    ore_ids_found = {}
    specials   = []
    crits = luckies = level_ups = 0
    new_ach    = []
    last_error = None
    mines_done = 0

    try:
        for i in range(count):
            user = await get_user(uid)
            if not user:
                last_error = "User tidak ditemukan"
                break

            # GUARD #6: Cek energy tiap iterasi (bukan hanya di awal)
            if not is_admin:
                fresh_tool = _TOOLS.get(user.get("current_tool", "stone_pick"), _TOOLS["stone_pick"])
                if user.get("energy", 0) < fresh_tool.get("energy_cost", 1):
                    last_error = (
                        f"Energy habis di mine ke-{i+1}! "
                        f"({user.get('energy',0)}/{user.get('max_energy',100)})"
                    )
                    break

            # GUARD #7: Cek bag tiap iterasi agar tidak overflow diam-diam
            if not is_admin:
                ore_inv = user.get("ore_inventory", {})
                if sum(ore_inv.values()) >= user.get("bag_slots", 50):
                    last_error = (
                        f"Bag penuh di mine ke-{i+1}! "
                        f"({sum(ore_inv.values())}/{user.get('bag_slots',50)} slot)"
                    )
                    break

            r = await perform_mine(uid, is_admin=is_admin)
            if not r["ok"]:
                # Strip markdown dari pesan error agar tidak konflik format
                err_raw = r["msg"]
                err_clean = err_raw.replace("*", "").replace("`", "").replace("_", "")
                last_error = err_clean
                break

            mines_done += 1
            total_xp   += r["xp_gain"]
            total_kg   += r.get("ore_kg", 0.0)
            ore_obj = r.get("ore", {})
            ore_key = f"{ore_obj.get('emoji','')} {ore_obj.get('name','?')}"
            ores_found[ore_key] = ores_found.get(ore_key, 0) + 1
            ore_id_key = r.get("ore_id", "") or ore_obj.get("id", "")
            if ore_id_key:
                ore_ids_found[ore_id_key] = ore_ids_found.get(ore_id_key, 0) + 1
            if r["is_crit"]:    crits += 1
            if r["is_lucky"]:   luckies += 1
            if r.get("special_hit"): specials.append(r["special_hit"])
            if r["leveled_up"]: level_ups += 1
            new_ach.extend(r.get("new_achievements", []))

            # GUARD #8: Cooldown diambil dari user fresh (bukan snapshot lama)
            if not is_admin and i < count - 1:
                fresh_user = await get_user(uid)
                cd = get_mine_cooldown_seconds(fresh_user, is_admin) if fresh_user else cd_secs
                await asyncio.sleep(cd + 0.5)  # +0.5s buffer agar tidak race condition

    except asyncio.CancelledError:
        last_error = "Mining dibatalkan"
    except Exception as _e:
        last_error = f"Mining dihentikan karena error: {_e}"
    finally:
        # GUARD #9: Selalu reset status mining multi (termasuk saat error/exception/crash)
        if not is_admin:
            await set_mining_multi_status(uid, False)

    ore_lines = "\n".join(f"   {k}: x{v}" for k, v in ores_found.items()) or "   Tidak ada"
    user = await get_user(uid)

    # BUG FIX #7: Tampilkan berapa mine yang berhasil dilakukan jika tidak full
    selesai_label = f"{mines_done}/{count}" if mines_done < count else multi_label

    lines = [
        f"✅ *Mining {selesai_label} Selesai!*",
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

    # Kirim foto ore yang ditemukan (maks 1 foto agar tidak error media group)
    ore_photos = []
    for oid in list(ore_ids_found.keys())[:1]:
        op = await get_ore_photo(oid)
        if op:
            ore_photos.append(op["photo_id"])

    try:
        if ore_photos:
            _sent = await callback.message.answer_photo(
                photo=ore_photos[0],
                caption=text,
                reply_markup=mine_action_kb(),
                parse_mode="Markdown"
            )
            if _sent: register_message_owner(_sent.chat.id, _sent.message_id, callback.from_user.id)
            try:
                await callback.message.delete()
            except Exception:
                pass
        else:
            try:
                await callback.message.edit_text(text, reply_markup=mine_action_kb(), parse_mode="Markdown")
            except Exception:
                _sent = await callback.message.answer(text, reply_markup=mine_action_kb(), parse_mode="Markdown")
                if _sent: register_message_owner(_sent.chat.id, _sent.message_id, callback.from_user.id)
    except Exception:
        try:
            await callback.message.edit_text(text, reply_markup=mine_action_kb(), parse_mode="Markdown")
        except Exception:
            try:
                _sent = await callback.message.answer(text, reply_markup=mine_action_kb(), parse_mode="Markdown")
                if _sent: register_message_owner(_sent.chat.id, _sent.message_id, callback.from_user.id)
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
        tool_photo = await get_tool_photo(tool_id)
        text = f"⚒️ *Ganti Alat*\n\n{msg}"
        kb = equip_menu_kb(user["owned_tools"], user["current_tool"])
        if tool_photo:
            try:
                _sent = await callback.message.answer_photo(
                    photo=tool_photo["photo_id"],
                    caption=text,
                    reply_markup=kb,
                    parse_mode="Markdown"
                )
                if _sent: register_message_owner(_sent.chat.id, _sent.message_id, callback.from_user.id)
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
        ore_list = _zone_ore_list(zone_id)
        zone_photo = await get_zone_photo(zone_id)
        text = (
            f"📍 *Zona Mining*\n\n{msg}\n\n"
            f"🪨 *Ore di zona ini:*\n_{ore_list}_"
        )
        kb = zone_menu_kb(user["unlocked_zones"], user.get("current_zone", "surface"))
        if zone_photo:
            try:
                _sent = await callback.message.answer_photo(
                    photo=zone_photo["photo_id"],
                    caption=text,
                    reply_markup=kb,
                    parse_mode="Markdown"
                )
                if _sent: register_message_owner(_sent.chat.id, _sent.message_id, callback.from_user.id)
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


@router.message(Command("resetmining"))
async def cmd_reset_mining(message: Message):
    """Command untuk pemain yang stuck saat mining multi (x5, x10, x25, x50).
    Mereset flag is_mining_multi agar pemain bisa mining kembali."""
    uid = message.from_user.id
    user = await get_user(uid)

    if not user:
        _sent = await message.answer("❌ Ketik /start terlebih dahulu.")
        if _sent: register_message_owner(_sent.chat.id, _sent.message_id, message.from_user.id)
        return

    if not user.get("is_mining_multi"):
        _sent = await message.answer(
            "✅ *Status Mining Normal*\n\n"
            "Kamu tidak sedang dalam kondisi stuck mining.\n"
            "Tidak perlu reset! Kamu bisa langsung mining seperti biasa.",
            parse_mode="Markdown"
        )
        if _sent: register_message_owner(_sent.chat.id, _sent.message_id, message.from_user.id)
        return

    # Cek apakah mining baru saja dimulai (< 2 menit) — hindari abuse reset
    started_raw = user.get("mining_multi_started")
    if started_raw and not _is_admin(uid):
        try:
            started_dt = datetime.fromisoformat(started_raw)
            elapsed_secs = (datetime.now() - started_dt).total_seconds()
            if elapsed_secs < 120:  # 2 menit cooldown sebelum boleh reset
                remaining = int(120 - elapsed_secs)
                _sent = await message.answer(
                    f"⏳ *Mining Baru Saja Dimulai*\n\n"
                    f"Mining baru berjalan `{int(elapsed_secs)}` detik.\n"
                    f"Tunggu `{remaining}` detik lagi sebelum bisa reset.\n\n"
                    f"💡 _Gunakan /resetmining jika mining benar-benar stuck._",
                    parse_mode="Markdown"
                )
                if _sent: register_message_owner(_sent.chat.id, _sent.message_id, message.from_user.id)
                return
        except Exception:
            pass  # Jika parse gagal, lanjut reset

    multi_type = user.get("mining_multi_type", "multi")
    await set_mining_multi_status(uid, False)

    _sent = await message.answer(
        f"🔄 *Reset Mining Berhasil!*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"✅ Status mining {multi_type} telah direset.\n"
        f"Kamu sekarang bisa mulai mining kembali.\n\n"
        f"⛏️ Ketik /mine atau tekan tombol *⛏️ Mining* untuk memulai.",
        parse_mode="Markdown"
    )
    if _sent: register_message_owner(_sent.chat.id, _sent.message_id, message.from_user.id)


@router.message(Command("rare_ore"))
async def cmd_rare_ore(message: Message):
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
    _sent = await message.answer(text, parse_mode="Markdown")
    if _sent: register_message_owner(_sent.chat.id, _sent.message_id, message.from_user.id)
