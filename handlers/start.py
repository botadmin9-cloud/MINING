"""
🏠 Start Handler v2 — Tanpa referral link
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command

from config import TOOLS, ZONES, ADMIN_IDS
from database import get_user, create_user
from game import regen_energy, energy_full_in, get_active_buffs
from keyboards import main_menu_kb, mine_action_kb

router = Router()


def _is_admin(uid: int) -> bool:
    return uid in ADMIN_IDS


@router.message(CommandStart())
async def cmd_start(message: Message):
    uid = message.from_user.id
    uname = message.from_user.username or ""
    fname = message.from_user.first_name or "Miner"

    existing = await get_user(uid)
    if not existing:
        await create_user(uid, uname, fname)
        admin_note = "\n👑 Kamu adalah *Admin Bot* ini!" if _is_admin(uid) else ""
        text = (
            f"⛏️ *Selamat Datang di Mining Bot v2, {fname}!*\n\n"
            f"🎮 Kamu telah bergabung sebagai penambang!\n"
            f"💰 Saldo awal: *500 koin*\n"
            f"⛏️ Alat starter: *Beliung Batu* (Gratis)\n"
            f"📍 Zona awal: *Permukaan*\n\n"
            f"🆔 Telegram ID: `{uid}`\n\n"
            f"🚀 Mulai mining dan kumpulkan koin sebanyak mungkin!\n"
            f"💡 Cek *❓ Bantuan* untuk panduan lengkap."
            f"{admin_note}"
        )
    else:
        user = await regen_energy(existing)
        tool = TOOLS.get(user["current_tool"], TOOLS["stone_pick"])
        zone = ZONES.get(user.get("current_zone", "surface"), ZONES["surface"])
        buffs = get_active_buffs(user)
        buff_txt = ""
        if buffs:
            buff_txt = "\n⚡ *Buff aktif:* " + ", ".join(buffs.keys())

        admin_badge = " 👑 *[ADMIN]*" if _is_admin(uid) else ""
        text = (
            f"👋 *Selamat kembali, {fname}!*{admin_badge}\n\n"
            f"🆔 ID       : `{uid}`\n"
            f"💰 Saldo   : `{user['balance']:,}` koin\n"
            f"⚡ Energy  : `{user['energy']}/{user['max_energy']}`\n"
            f"⭐ Level   : `{user['level']}`\n"
            f"🔧 Alat    : {tool['emoji']} {tool['name']}\n"
            f"📍 Zona    : {zone['name']}"
            f"{buff_txt}"
        )

    await message.answer(text, reply_markup=main_menu_kb(), parse_mode="Markdown")


@router.callback_query(F.data == "main_menu")
async def cb_main_menu(callback: CallbackQuery):
    uid = callback.from_user.id
    user = await get_user(uid)
    if not user:
        await callback.answer("Ketik /start dulu!")
        return
    tool = TOOLS.get(user["current_tool"], TOOLS["stone_pick"])
    zone = ZONES.get(user.get("current_zone", "surface"), ZONES["surface"])
    admin_badge = " 👑" if _is_admin(uid) else ""
    text = (
        f"🏠 *Menu Utama*{admin_badge}\n\n"
        f"🆔 ID     : `{uid}`\n"
        f"💰 Saldo  : `{user['balance']:,}` koin\n"
        f"⚡ Energy : `{user['energy']}/{user['max_energy']}`\n"
        f"⭐ Level  : `{user['level']}`\n"
        f"🔧 Alat   : {tool['emoji']} {tool['name']}\n"
        f"📍 Zona   : {zone['name']}"
    )
    await callback.message.edit_text(text, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "noop")
async def cb_noop(callback: CallbackQuery):
    await callback.answer()
