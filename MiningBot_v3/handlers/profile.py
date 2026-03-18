from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import TOOLS, ZONES, ACHIEVEMENTS, ORES, xp_for_level, ADMIN_IDS, BAG_SLOT_DEFAULT
from database import get_user, get_user_rank, get_ore_stats, update_user
from game import regen_energy, energy_full_in, make_bar
from keyboards import profile_kb, back_main_kb

router = Router()


class SetNameState(StatesGroup):
    waiting_name = State()


def _is_admin(uid: int) -> bool:
    return uid in ADMIN_IDS


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
    # BLOKIR: non-admin tidak bisa melihat profil admin
    if _is_admin(uid) and viewer_id != uid:
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
    if user.get("rebirth_count", 0) > 0:
        rebirth_txt = (f"\n🔄 Rebirth    : `{user['rebirth_count']}x` "
                       f"(Perm XP: `{user.get('perm_xp_mult', 1.0):.1f}x`)")

    admin_badge = " 👑 *[ADMIN]*" if _is_admin(uid) else ""
    ore_inv   = user.get("ore_inventory", {})
    ore_qty   = sum(v for v in ore_inv.values() if v > 0)
    ore_types = len([k for k, v in ore_inv.items() if v > 0])
    bag_slots = user.get("bag_slots", BAG_SLOT_DEFAULT)

    # ✅ Tampilkan display_name (nama kustom) jika ada
    display = (user.get("display_name") or "").strip()
    if not display:
        display = tg_user.first_name if hasattr(tg_user, "first_name") else user.get("first_name", "Miner")

    uname_txt = f"@{tg_user.username}" if (hasattr(tg_user, "username") and tg_user.username) else ""

    text = (
        f"👤 *Profil: {display}*{admin_badge}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🆔 Telegram ID : `{uid}`\n"
        + (f"📱 Username    : {uname_txt}\n" if uname_txt else "")
        + f"🎮 Nama Game   : *{display}*\n"
        f"🏆 Rank        : *#{rank}*\n"
        f"⭐ Level       : *{lv}*\n"
        f"📈 XP          : `{xp:,}` / `{next_xp:,}`\n"
        f"   {xp_bar}\n\n"
        f"💰 Saldo       : `{user['balance']:,}` koin\n"
        f"💎 Total Earn  : `{user.get('total_earned', 0):,}` koin\n"
        f"🔢 Mine Count  : `{user['mine_count']:,}` kali\n"
        f"🔥 Streak      : `{user.get('daily_streak', 0)}` hari\n"
        f"⚡ Energy      : {e_bar} `{user['energy']}/{user['max_energy']}`\n"
        f"⏰ Penuh dalam : *{energy_full_in(user)}*\n\n"
        f"🎒 Bag         : `{ore_qty}/{bag_slots}` slot ({ore_types} jenis)\n"
        f"⭐ Favorit     : `{len(user.get('favorite_ores',[]))}` ore\n"
        f"🏛️ Museum      : `{len(user.get('museum_ores',[]))}` ore\n\n"
        f"🔧 Alat Aktif  : {tool['emoji']} *{tool['name']}*\n"
        f"   └ Power: `+{tool['power']}` | Speed: `{tool['speed_mult']}x`\n"
        f"📍 Zona Aktif  : {zone['name']}\n"
        f"🏅 Prestasi    : `{len(user['achievements'])}` / `{len(ACHIEVEMENTS)}`"
        f"{rebirth_txt}\n\n"
        f"💡 Ketik `/setname` untuk ganti nama game."
    )
    if isinstance(target, Message):
        await target.answer(text, reply_markup=profile_kb(), parse_mode="Markdown")
    else:
        await target.message.edit_text(text, reply_markup=profile_kb(), parse_mode="Markdown")


@router.message(Command("setname"))
async def cmd_setname(message: Message, state: FSMContext):
    await state.set_state(SetNameState.waiting_name)
    user = await get_user(message.from_user.id)
    current = user.get("display_name", "") if user else ""
    await message.answer(
        f"✏️ *Ganti Nama Game*\n\n"
        f"Nama saat ini: *{current or '(belum diset)'}*\n\n"
        f"Masukkan nama baru (2–30 karakter):\n"
        f"Atau /cancel untuk batal.",
        parse_mode="Markdown"
    )


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    current = await state.get_state()
    if current:
        await state.clear()
        await message.answer("❌ Dibatalkan.")


@router.message(SetNameState.waiting_name)
async def process_setname(message: Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 2 or len(name) > 30:
        await message.answer("❌ Nama harus 2–30 karakter. Coba lagi:")
        return
    await state.clear()
    await update_user(message.from_user.id, display_name=name)
    await message.answer(
        f"✅ *Nama game berhasil diubah!*\n\n"
        f"Nama baru: *{name}*\n\n"
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
    await callback.message.edit_text(text, reply_markup=back_main_kb(), parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "achievements")
async def cb_achievements(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.answer("Ketik /start!")
        return
    achieved = user["achievements"]
    lines = ["🏅 *Daftar Prestasi:*\n"]
    for ach_id, ach in ACHIEVEMENTS.items():
        done = ach_id in achieved
        lines.append(f"{'✅' if done else '⬜'} *{ach['name']}*\n   _{ach['desc']}_ (+{ach['reward']:,}🪙)")
    await callback.message.edit_text("\n".join(lines), reply_markup=back_main_kb(), parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "ore_inv_view")
async def cb_ore_inv_view(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.answer("Ketik /start!")
        return
    ore_inv = {k: v for k, v in user.get("ore_inventory", {}).items() if v > 0}
    if not ore_inv:
        await callback.message.edit_text(
            "📦 *Inventory Ore Kosong!*\n\nMulai mining untuk mengumpulkan ore.",
            reply_markup=back_main_kb(), parse_mode="Markdown")
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
    await callback.message.edit_text("\n".join(lines), reply_markup=back_main_kb(), parse_mode="Markdown")
    await callback.answer()
