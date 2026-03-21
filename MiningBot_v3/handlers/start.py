from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import TOOLS, ZONES, ADMIN_IDS
from database import get_user, create_user, update_user, is_dynamic_admin
from game import regen_energy, energy_full_in, get_active_buffs
from keyboards import main_menu_kb

router = Router()


class RegisterState(StatesGroup):
    waiting_username = State()


async def _is_admin(uid: int) -> bool:
    if uid in ADMIN_IDS:
        return True
    return await is_dynamic_admin(uid)


def _official_links_kb() -> InlineKeyboardMarkup:
    """Tombol channel & grup official."""
    from config import OFFICIAL_CHANNEL, OFFICIAL_GROUP
    rows = []
    if OFFICIAL_CHANNEL:
        rows.append([InlineKeyboardButton(text="📢 Channel Official", url=OFFICIAL_CHANNEL)])
    if OFFICIAL_GROUP:
        rows.append([InlineKeyboardButton(text="👥 Grup Official", url=OFFICIAL_GROUP)])
    rows.append([InlineKeyboardButton(text="🚀 Mulai Main!", callback_data="close_welcome")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    uid   = message.from_user.id
    uname = message.from_user.username or ""
    fname = message.from_user.first_name or "Miner"

    # FIX: Bersihkan FSM state apapun yang mungkin tertinggal (misal user tinggalkan
    # flow market/transfer tanpa tekan tombol Batal)
    current_state = await state.get_state()
    if current_state and "RegisterState" not in (current_state or ""):
        await state.clear()

    existing = await get_user(uid)
    if not existing:
        await state.set_state(RegisterState.waiting_username)
        await state.update_data(uid=uid, uname=uname, fname=fname)
        await message.answer(
            f"⛏️ *Selamat Datang di Mining Bot!*\n\n"
            f"Halo, {fname}! 👋\n\n"
            f"Sebelum mulai, masukkan *nama/username* yang ingin kamu gunakan di game ini:\n"
            f"_(Nama ini akan tampil di Profil dan Leaderboard)_\n\n"
            f"Contoh: `SiPenambang`, `ProMiner99`, dll.\n"
            f"Atau ketik /skip untuk pakai nama default (`{fname}`).",
            parse_mode="Markdown"
        )
    else:
        # Update username & first_name jika berubah
        needs_update = {}
        if existing.get("username") != uname:
            needs_update["username"] = uname
        if existing.get("first_name") != fname:
            needs_update["first_name"] = fname
        if needs_update:
            await update_user(uid, **needs_update)
        user = await regen_energy(existing)
        tool = TOOLS.get(user["current_tool"], TOOLS["stone_pick"])
        zone = ZONES.get(user.get("current_zone", "surface"), ZONES["surface"])
        buffs = get_active_buffs(user)
        buff_txt = ""
        if buffs:
            buff_txt = "\n⚡ *Buff aktif:* " + ", ".join(buffs.keys())

        admin_badge = " 👑 *[ADMIN]*" if await _is_admin(uid) else ""
        bag_slots = user.get("bag_slots", 50)
        ore_used  = sum(user.get("ore_inventory", {}).values())
        display   = user.get("display_name") or user.get("first_name", fname)

        text = (
            f"👋 *Selamat kembali, {display}!*{admin_badge}\n\n"
            f"🆔 ID       : `{uid}`\n"
            f"💰 Saldo   : `{user['balance']:,}` koin\n"
            f"⚡ Energy  : `{user['energy']}/{user['max_energy']}`\n"
            f"⭐ Level   : `{user['level']}`\n"
            f"🎒 Bag     : `{ore_used}/{bag_slots}` slot\n"
            f"🔧 Alat    : {tool['emoji']} {tool['name']}\n"
            f"📍 Zona    : {zone['name']}"
            f"{buff_txt}"
        )
        await message.answer(text, reply_markup=main_menu_kb(), parse_mode="Markdown")

        # Tampilkan tombol link official
        from config import OFFICIAL_CHANNEL, OFFICIAL_GROUP
        if OFFICIAL_CHANNEL or OFFICIAL_GROUP:
            await message.answer(
                "📢 *Bergabung ke komunitas official kami!*",
                reply_markup=_official_links_kb(),
                parse_mode="Markdown"
            )


@router.message(Command("skip"))
async def cmd_skip_username(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state != RegisterState.waiting_username:
        await message.answer("❌ Tidak ada proses registrasi aktif.", parse_mode="Markdown")
        return
    data = await state.get_data()
    await state.clear()
    uid   = data.get("uid", message.from_user.id)
    uname = data.get("uname", "")
    fname = data.get("fname", "Miner")
    await _finish_register(message, uid, uname, fname, fname)


@router.message(RegisterState.waiting_username)
async def process_username(message: Message, state: FSMContext):
    display_name = message.text.strip()
    if len(display_name) < 2 or len(display_name) > 30:
        await message.answer(
            "❌ Nama harus 2–30 karakter. Coba lagi:",
            parse_mode="Markdown"
        )
        return
    data = await state.get_data()
    await state.clear()
    uid   = data.get("uid", message.from_user.id)
    uname = data.get("uname", "")
    fname = data.get("fname", "Miner")
    await _finish_register(message, uid, uname, fname, display_name)


async def _finish_register(message: Message, uid: int, uname: str,
                             fname: str, display_name: str):
    from config import STARTING_BALANCE
    await create_user(uid, uname, fname, display_name)
    admin_note = "\n👑 Kamu adalah *Admin Bot* ini!" if await _is_admin(uid) else ""
    text = (
        f"⛏️ *Selamat Datang di Mining Bot, {display_name}!*\n\n"
        f"🎮 Kamu telah bergabung sebagai penambang!\n"
        f"💰 Saldo awal       : *{STARTING_BALANCE:,} koin*\n"
        f"⛏️ Alat starter     : *Beliung Batu* (Gratis)\n"
        f"📍 Zona awal        : *Permukaan*\n"
        f"⚡ Max Energy       : *500*\n"
        f"🎒 Slot Bag         : *50 slot*\n\n"
        f"🆔 Telegram ID: `{uid}`\n"
        f"👤 Nama Game  : *{display_name}*\n\n"
        f"📋 *Perintah Berguna:*\n"
        f"• `/bag` — Lihat & kelola ore\n"
        f"• `/shop` — Upgrade Bag & Energy di menu Shop\n"
        f"• `/profile` — Lihat profil\n"
        f"• `/rare_ore` — Lihat semua ore rare\n\n"
        f"🚀 Gunakan menu di bawah untuk memulai!"
        f"{admin_note}"
    )
    await message.answer(text, reply_markup=main_menu_kb(), parse_mode="Markdown")

    # Tampilkan tombol link official setelah register
    from config import OFFICIAL_CHANNEL, OFFICIAL_GROUP
    if OFFICIAL_CHANNEL or OFFICIAL_GROUP:
        await message.answer(
            "📢 *Bergabung ke komunitas official kami!*\n"
            "_(Dapatkan info update, event, dan tips mining terbaru!)_",
            reply_markup=_official_links_kb(),
            parse_mode="Markdown"
        )


@router.callback_query(F.data == "close_welcome")
async def cb_close_welcome(callback: CallbackQuery):
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.answer("🚀 Selamat bermain!")


@router.callback_query(F.data == "main_menu")
async def cb_main_menu(callback: CallbackQuery):
    uid  = callback.from_user.id
    user = await get_user(uid)
    if not user:
        await callback.answer("Ketik /start dulu!")
        return
    tool = TOOLS.get(user["current_tool"], TOOLS["stone_pick"])
    zone = ZONES.get(user.get("current_zone", "surface"), ZONES["surface"])
    admin_badge = " 👑" if await _is_admin(uid) else ""
    ore_used    = sum(user.get("ore_inventory", {}).values())
    bag_slots   = user.get("bag_slots", 50)
    display     = user.get("display_name") or user.get("first_name", "Miner")
    text = (
        f"🏠 *Menu Utama*{admin_badge}\n\n"
        f"👤 {display}\n"
        f"💰 Saldo  : `{user['balance']:,}` koin\n"
        f"⚡ Energy : `{user['energy']}/{user['max_energy']}`\n"
        f"⭐ Level  : `{user['level']}`\n"
        f"🎒 Bag    : `{ore_used}/{bag_slots}` slot\n"
        f"🔧 Alat   : {tool['emoji']} {tool['name']}\n"
        f"📍 Zona   : {zone['name']}"
    )
    try:
        await callback.message.edit_text(text, reply_markup=main_menu_kb(), parse_mode="Markdown")
    except Exception:
        pass
    await callback.answer()


@router.callback_query(F.data == "noop")
async def cb_noop(callback: CallbackQuery):
    await callback.answer()


@router.message(Command("links"))
async def cmd_links(message: Message):
    from config import OFFICIAL_CHANNEL, OFFICIAL_GROUP
    if not OFFICIAL_CHANNEL and not OFFICIAL_GROUP:
        await message.answer("ℹ️ Belum ada link official yang dikonfigurasi.")
        return
    await message.answer(
        "📢 *Link Official Mining Bot*",
        reply_markup=_official_links_kb(),
        parse_mode="Markdown"
    )
