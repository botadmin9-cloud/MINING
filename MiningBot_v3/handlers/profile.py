from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime, timedelta

from config import TOOLS, ZONES, ACHIEVEMENTS, ORES, xp_for_level, ADMIN_IDS, BAG_SLOT_DEFAULT
from database import get_user, get_user_rank, get_ore_stats, update_user, is_dynamic_admin
from game import regen_energy, energy_full_in, make_bar
from keyboards import profile_kb, back_main_kb

router = Router()

NAME_CHANGE_COOLDOWN_DAYS = 7


class SetNameState(StatesGroup):
    waiting_name = State()


async def _is_admin(uid: int) -> bool:
    if uid in ADMIN_IDS:
        return True
    return await is_dynamic_admin(uid)


@router.message(F.text == "👤 Profil")
@router.message(Command("profile"))
async def show_profile(message: Message):
    uid  = message.from_user.id
    user = await get_user(uid)
    if not user:
        await message.answer("❌ Ketik /start!")
        return
    user = await regen_energy(user)
    await _send_profile(message, user, message.from_user)


async def _send_profile(target, user: dict, tg_user):
    uid = user["user_id"]
    viewer_id = tg_user.id if hasattr(tg_user, "id") else uid
    if await _is_admin(uid) and viewer_id != uid:
        msg = "❌ Profil ini tidak dapat dilihat."
        if isinstance(target, Message):
            await target.answer(msg, reply_markup=back_main_kb())
        else:
            await target.message.edit_text(msg, reply_markup=back_main_kb())
        return

    rank    = await get_user_rank(uid)
    tool    = TOOLS.get(user["current_tool"], TOOLS["stone_pick"])
    zone    = ZONES.get(user.get("current_zone", "surface"), ZONES["surface"])
    lv, xp  = user["level"], user["xp"]
    next_xp = xp_for_level(lv)
    xp_bar  = make_bar(xp, next_xp, 10)
    e_bar   = make_bar(user["energy"], user["max_energy"], 8)

    rebirth_txt = ""
    vip_txt = ""
    vip_exp = user.get("vip_expires_at")
    if vip_exp:
        try:
            exp_dt = datetime.fromisoformat(vip_exp)
            if exp_dt > datetime.now():
                days_left = (exp_dt - datetime.now()).days
                vip_txt = f"\n👑 VIP         : `Aktif ({days_left} hari)`"
        except Exception:
            pass
    if user.get("rebirth_count", 0) > 0:
        rebirth_txt = (f"\n🔄 Rebirth    : `{user['rebirth_count']}x` "
                       f"(Perm XP: `{user.get('perm_xp_mult', 1.0):.1f}x`)")

    # Hitung kapan bisa ganti nama lagi
    last_change = user.get("last_name_change")
    name_cd_txt = ""
    can_change_now = True
    if last_change and not await _is_admin(uid):
        try:
            lc_dt = datetime.fromisoformat(last_change)
            next_change = lc_dt + timedelta(days=NAME_CHANGE_COOLDOWN_DAYS)
            if datetime.now() < next_change:
                remaining = next_change - datetime.now()
                days_left = remaining.days
                hours_left = remaining.seconds // 3600
                name_cd_txt = f"\n   _(Bisa ganti lagi: {days_left}h {hours_left}j)_"
                can_change_now = False
            else:
                name_cd_txt = "\n   _(Bisa ganti sekarang!)_"
        except Exception:
            name_cd_txt = ""
    else:
        if not await _is_admin(uid):
            name_cd_txt = "\n   _(Bisa ganti sekarang!)_"

    _uid_is_admin = await _is_admin(uid)
    admin_badge = " 👑 *[ADMIN]*" if _uid_is_admin else ""
    ore_inv   = user.get("ore_inventory", {})
    ore_qty   = sum(v for v in ore_inv.values() if v > 0)
    ore_types = len([k for k, v in ore_inv.items() if v > 0])
    bag_slots = user.get("bag_slots", BAG_SLOT_DEFAULT)

    display = (user.get("display_name") or "").strip() or user.get("first_name", "Miner")

    text = (
        f"👤 *Profil Penambang*{admin_badge}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🏷️ Nama        : *{display}*{name_cd_txt}\n"
        f"🆔 ID          : `{uid}`\n"
        f"⭐ Level       : `{lv}` / XP: `{xp:,}` / `{next_xp:,}`\n"
        f"   {xp_bar}\n"
        f"⚡ Energy      : `{user['energy']}/{user['max_energy']}`\n"
        f"   {e_bar} (penuh: {energy_full_in(user)})\n"
        f"💰 Saldo       : `{user['balance']:,}` koin\n"
        f"💸 Total Earn  : `{user.get('total_earned',0):,}` koin\n"
        f"📊 Rank        : `#{rank}`\n\n"
        f"⛏️ Mining      : `{user.get('mine_count',0):,}x`\n"
        f"⚖️ Total KG    : `{user.get('total_kg_mined',0):.2f}` kg\n"
        f"🪨 Ore di Bag  : `{ore_qty}` buah ({ore_types} jenis)\n"
        f"🎒 Slot Bag    : `{ore_qty}/{bag_slots}`\n"
        f"🔧 Alat Aktif  : {tool['emoji']} {tool['name']}\n"
        f"📍 Zona Aktif  : {zone['name']}\n"
        f"🏅 Prestasi    : `{len(user['achievements'])}` / `{len(ACHIEVEMENTS)}`"
        f"{rebirth_txt}{vip_txt}"
    )
    # FIX 11: Gunakan profile_kb yang sudah ada tombol ganti nama
    kb = profile_kb(can_change=can_change_now or _uid_is_admin)
    if isinstance(target, Message):
        await target.answer(text, reply_markup=kb, parse_mode="Markdown")
    else:
        await target.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")


# FIX 11: Callback untuk tombol "✏️ Ganti Nama" di profile
@router.callback_query(F.data == "profile_setname")
async def cb_profile_setname(callback: CallbackQuery, state: FSMContext):
    uid = callback.from_user.id
    user = await get_user(uid)
    if not user:
        await callback.answer("❌ Ketik /start!")
        return

    if not await _is_admin(uid):
        last_change = user.get("last_name_change")
        if last_change:
            try:
                lc_dt = datetime.fromisoformat(last_change)
                next_change = lc_dt + timedelta(days=NAME_CHANGE_COOLDOWN_DAYS)
                if datetime.now() < next_change:
                    remaining = next_change - datetime.now()
                    days_left = remaining.days
                    hours_left = remaining.seconds // 3600
                    await callback.answer(
                        f"⏳ Belum bisa ganti nama!\nCoba lagi dalam {days_left}h {hours_left}j.",
                        show_alert=True
                    )
                    return
            except Exception:
                pass

    await state.set_state(SetNameState.waiting_name)
    current = user.get("display_name", "") if user else ""
    await callback.answer()
    try:
        await callback.message.edit_text(
            f"✏️ *Ganti Nama Game*\n\n"
            f"Nama saat ini: *{current or '(belum diset)'}*\n\n"
            f"⚠️ Nama hanya bisa diganti *1x per minggu*!\n\n"
            f"Masukkan nama baru (2–30 karakter):\n"
            f"Atau ketik /cancel untuk batal.",
            parse_mode="Markdown"
        )
    except Exception:
        await callback.message.answer(
            f"✏️ *Ganti Nama Game*\n\n"
            f"Nama saat ini: *{current or '(belum diset)'}*\n\n"
            f"Masukkan nama baru (2–30 karakter):\nAtau ketik /cancel untuk batal.",
            parse_mode="Markdown"
        )


# FIX 11: Pertahankan /setname sebagai alias (tidak dihapus sepenuhnya agar tidak error)
@router.message(Command("setname"))
async def cmd_setname(message: Message, state: FSMContext):
    uid = message.from_user.id
    user = await get_user(uid)
    if not user:
        await message.answer("❌ Ketik /start!")
        return

    if not await _is_admin(uid):
        last_change = user.get("last_name_change")
        if last_change:
            try:
                lc_dt = datetime.fromisoformat(last_change)
                next_change = lc_dt + timedelta(days=NAME_CHANGE_COOLDOWN_DAYS)
                if datetime.now() < next_change:
                    remaining = next_change - datetime.now()
                    days_left = remaining.days
                    hours_left = remaining.seconds // 3600
                    await message.answer(
                        f"⏳ *Belum bisa ganti nama!*\n\n"
                        f"Ganti nama hanya bisa dilakukan *1x per minggu*.\n"
                        f"Coba lagi dalam: `{days_left}` hari `{hours_left}` jam.",
                        parse_mode="Markdown"
                    )
                    return
            except Exception:
                pass

    await state.set_state(SetNameState.waiting_name)
    current = user.get("display_name", "") if user else ""
    await message.answer(
        f"✏️ *Ganti Nama Game*\n\n"
        f"Nama saat ini: *{current or '(belum diset)'}*\n\n"
        f"⚠️ Nama hanya bisa diganti *1x per minggu*!\n\n"
        f"Masukkan nama baru (2–30 karakter):\n"
        f"Atau /cancel untuk batal.",
        parse_mode="Markdown"
    )


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    current = await state.get_state()
    if current:
        await state.clear()
        await message.answer("❌ Proses dibatalkan.")
    else:
        await message.answer("ℹ️ Tidak ada proses yang aktif saat ini.")


@router.message(SetNameState.waiting_name)
async def process_setname(message: Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 2 or len(name) > 30:
        await message.answer("❌ Nama harus 2–30 karakter. Coba lagi:")
        return
    await state.clear()
    now = datetime.now().isoformat()
    await update_user(message.from_user.id, display_name=name, last_name_change=now)
    await message.answer(
        f"✅ *Nama game berhasil diubah!*\n\n"
        f"Nama baru: *{name}*\n\n"
        f"ℹ️ Nama bisa diganti lagi dalam *7 hari*.\n"
        f"Nama ini akan tampil di Profil dan Leaderboard.",
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "mine_stats")
async def cb_mine_stats(callback: CallbackQuery):
    stats = await get_ore_stats(callback.from_user.id)
    if not stats:
        text = "📊 *Statistik Mining*\n\nBelum ada data. Mulai mining!"
    else:
        lines = ["📊 *Statistik Ore Mining:*\n"]
        for s in stats[:12]:
            lines.append(f"  {s['ore_name']}: `{s['cnt']}x`")
        text = "\n".join(lines)
    try:
        await callback.message.edit_text(text, reply_markup=back_main_kb(), parse_mode="Markdown")
    except Exception:
        pass
    await callback.answer()


@router.callback_query(F.data == "achievements")
async def cb_achievements(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.answer("Ketik /start!")
        return
    achieved = user["achievements"]
    done_count = len(achieved)
    total_count = len(ACHIEVEMENTS)

    unlocked_lines = []
    locked_lines   = []
    for ach_id, ach in ACHIEVEMENTS.items():
        if ach_id in achieved:
            unlocked_lines.append(f"✅ *{ach['name']}* (+{ach['reward']:,}🪙)")
        else:
            locked_lines.append(f"⬜ *{ach['name']}*\n   _{ach['desc']}_")

    header = [f"🏅 *Prestasi: {done_count}/{total_count}*\n━━━━━━━━━━━━━━━━━━━━\n"]
    if unlocked_lines:
        header.append("*✅ Sudah Didapat:*")
        header.extend(unlocked_lines)
        header.append("")
    if locked_lines:
        header.append("*⬜ Belum Didapat:*")
        header.extend(locked_lines[:20])
        if len(locked_lines) > 20:
            header.append(f"_...dan {len(locked_lines)-20} prestasi lagi_")

    text = "\n".join(header)
    if len(text) > 4000:
        text = text[:3990] + "\n_...(terpotong)_"
    try:
        await callback.message.edit_text(text, reply_markup=back_main_kb(), parse_mode="Markdown")
    except Exception:
        pass
    await callback.answer()


@router.callback_query(F.data == "ore_inv_view")
async def cb_ore_inv_view(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.answer("Ketik /start!")
        return
    ore_inv = {k: v for k, v in user.get("ore_inventory", {}).items() if v > 0}
    if not ore_inv:
        try:
            await callback.message.edit_text(
                "📦 *Inventory Ore Kosong!*\n\nMulai mining untuk mengumpulkan ore.",
                reply_markup=back_main_kb(), parse_mode="Markdown")
        except Exception:
            pass
        await callback.answer()
        return
    sorted_ores = sorted(ore_inv.items(), key=lambda x: ORES.get(x[0], {}).get("value", 0), reverse=True)
    lines = ["📦 *Inventory Ore Kamu*\n"]
    for ore_id, qty in sorted_ores[:15]:
        ore = ORES.get(ore_id, {})
        lines.append(f"{ore.get('emoji','')} *{ore.get('name', ore_id)}*: `{qty}` buah")
    if len(sorted_ores) > 15:
        lines.append(f"\n_...dan {len(sorted_ores)-15} jenis lainnya_")
    lines.append("\n💡 Kelola ore di *🎒 Bag*!")
    try:
        await callback.message.edit_text("\n".join(lines), reply_markup=back_main_kb(), parse_mode="Markdown")
    except Exception:
        pass
    await callback.answer()
