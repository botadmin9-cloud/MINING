from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from config import ORES, ADMIN_IDS
from database import get_user, update_user, get_ore_photo
from keyboards import back_main_kb

router = Router()

FAV_MAX    = 150
MUSEUM_MAX = 30


def _is_admin(uid: int) -> bool:
    return uid in ADMIN_IDS


# ══════════════════════════════════════════════════════════════
# FAVORIT
# ══════════════════════════════════════════════════════════════
@router.message(F.text == "⭐ Favorit")
@router.message(Command("favorite"))
@router.message(Command("fav"))
async def cmd_favorite(message: Message):
    user = await get_user(message.from_user.id)
    if not user:
        await message.answer("❌ Ketik /start!")
        return
    await _show_favorite(message, user, send_new=True)


async def _show_favorite(target, user: dict, send_new: bool = False):
    fav = user.get("favorite_ores", [])
    if not fav:
        text = (
            "⭐ *Ore Favorit*\n\n"
            "Belum ada ore favorit.\n\n"
            "💡 Cara menambah:\n"
            "• Buka `/bag` → klik nama ore → *Tambah Favorit*"
        )
        if send_new:
            await target.answer(text, reply_markup=back_main_kb(), parse_mode="Markdown")
        else:
            await target.message.edit_text(text, reply_markup=back_main_kb(), parse_mode="Markdown")
        return

    lines = [f"⭐ *Ore Favorit ({len(fav)}/{FAV_MAX})*\n━━━━━━━━━━━━━━━━━━━━\n"]
    for ore_id in fav:
        ore = ORES.get(ore_id, {})
        qty = user.get("ore_inventory", {}).get(ore_id, 0)
        lines.append(
            f"{ore.get('emoji','')} *{ore.get('name', ore_id)}*"
            f"  —  `{qty}` buah  |  `{ore.get('value',0):,}` koin/buah"
        )

    rows = []
    # Tombol hapus per ore (maks 5 tampil)
    for ore_id in fav[:5]:
        ore = ORES.get(ore_id, {})
        rows.append([InlineKeyboardButton(
            text=f"❌ {ore.get('emoji','')} {ore.get('name', ore_id)}",
            callback_data=f"fav_remove_{ore_id}"
        )])
    if len(fav) > 5:
        rows.append([InlineKeyboardButton(
            text=f"... +{len(fav)-5} lainnya (hapus via /bag)", callback_data="noop"
        )])
    rows.append([InlineKeyboardButton(text="🏠 Menu", callback_data="main_menu")])
    kb = InlineKeyboardMarkup(inline_keyboard=rows)

    text = "\n".join(lines)
    if send_new:
        await target.answer(text, reply_markup=kb, parse_mode="Markdown")
    else:
        try:
            await target.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
        except Exception:
            await target.message.answer(text, reply_markup=kb, parse_mode="Markdown")


@router.callback_query(F.data.startswith("fav_toggle_"))
async def cb_fav_toggle(callback: CallbackQuery):
    ore_id = callback.data.replace("fav_toggle_", "")
    ore    = ORES.get(ore_id)
    user   = await get_user(callback.from_user.id)
    if not ore or not user:
        await callback.answer("❌ Ore tidak ditemukan!")
        return

    fav = list(user.get("favorite_ores", []))
    if ore_id in fav:
        fav.remove(ore_id)
        await update_user(callback.from_user.id, favorite_ores=fav)
        await callback.answer(f"❌ {ore['name']} dihapus dari Favorit", show_alert=False)
    else:
        if len(fav) >= FAV_MAX:
            await callback.answer(f"❌ Favorit penuh! Maks {FAV_MAX} ore.", show_alert=True)
            return
        fav.append(ore_id)
        await update_user(callback.from_user.id, favorite_ores=fav)
        await callback.answer(f"⭐ {ore['name']} ditambah ke Favorit!", show_alert=False)


@router.callback_query(F.data.startswith("fav_remove_"))
async def cb_fav_remove(callback: CallbackQuery):
    ore_id = callback.data.replace("fav_remove_", "")
    user   = await get_user(callback.from_user.id)
    if not user:
        await callback.answer("Ketik /start!")
        return
    fav = list(user.get("favorite_ores", []))
    if ore_id in fav:
        fav.remove(ore_id)
        await update_user(callback.from_user.id, favorite_ores=fav)
        ore = ORES.get(ore_id, {})
        await callback.answer(f"❌ {ore.get('name', ore_id)} dihapus", show_alert=False)
    user = await get_user(callback.from_user.id)
    await _show_favorite(callback, user, send_new=False)


# ══════════════════════════════════════════════════════════════
# MUSEUM
# ══════════════════════════════════════════════════════════════
@router.message(F.text == "🏛️ Museum")
@router.message(Command("museum"))
async def cmd_museum(message: Message):
    user = await get_user(message.from_user.id)
    if not user:
        await message.answer("❌ Ketik /start!")
        return
    await _show_museum(message, user, send_new=True)


async def _show_museum(target, user: dict, send_new: bool = False):
    museum = user.get("museum_ores", [])
    if not museum:
        text = (
            "🏛️ *Museum Ore*\n\n"
            f"Museum kosong _(maks {MUSEUM_MAX} jenis)_.\n\n"
            "💡 Cara mengisi:\n"
            "• Buka `/bag` → klik nama ore → *Simpan Museum*\n\n"
            "Museum menyimpan catatan ore langka yang pernah kamu temukan!"
        )
        if send_new:
            await target.answer(text, reply_markup=back_main_kb(), parse_mode="Markdown")
        else:
            await target.message.edit_text(text, reply_markup=back_main_kb(), parse_mode="Markdown")
        return

    lines = [f"🏛️ *Museum Ore ({len(museum)}/{MUSEUM_MAX})*\n━━━━━━━━━━━━━━━━━━━━\n"]
    for i, ore_id in enumerate(museum, 1):
        ore = ORES.get(ore_id, {})
        lines.append(
            f"`{i}.` {ore.get('emoji','')} *{ore.get('name', ore_id)}*\n"
            f"     _{ore.get('desc','')}_\n"
            f"     Nilai: `{ore.get('value',0):,}` koin | Rarity: `{ore.get('rarity',0)}%`"
        )

    rows = [
        [InlineKeyboardButton(text="📸 Lihat Foto Ore", callback_data="museum_view_photos")],
        [InlineKeyboardButton(text="🏠 Menu", callback_data="main_menu")],
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    text = "\n".join(lines)

    if send_new:
        await target.answer(text, reply_markup=kb, parse_mode="Markdown")
    else:
        try:
            await target.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
        except Exception:
            await target.message.answer(text, reply_markup=kb, parse_mode="Markdown")


@router.callback_query(F.data.startswith("museum_toggle_"))
async def cb_museum_toggle(callback: CallbackQuery):
    ore_id = callback.data.replace("museum_toggle_", "")
    ore    = ORES.get(ore_id)
    user   = await get_user(callback.from_user.id)
    if not ore or not user:
        await callback.answer("❌ Ore tidak ditemukan!")
        return

    museum = list(user.get("museum_ores", []))
    if ore_id in museum:
        museum.remove(ore_id)
        await update_user(callback.from_user.id, museum_ores=museum)
        await callback.answer(f"🗑️ {ore['name']} dihapus dari Museum", show_alert=False)
    else:
        if len(museum) >= MUSEUM_MAX:
            await callback.answer(f"❌ Museum penuh! Maks {MUSEUM_MAX} jenis.", show_alert=True)
            return
        museum.append(ore_id)
        await update_user(callback.from_user.id, museum_ores=museum)
        await callback.answer(f"🏛️ {ore['name']} disimpan ke Museum!", show_alert=False)


@router.callback_query(F.data == "museum_view_photos")
async def cb_museum_view_photos(callback: CallbackQuery):
    """Tampilkan foto-foto ore yang sudah di-set admin untuk ore di museum."""
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.answer("Ketik /start!")
        return

    museum = user.get("museum_ores", [])
    if not museum:
        await callback.answer("Museum kosong!", show_alert=True)
        return

    await callback.answer("📸 Memuat foto ore...")
    sent_any = False
    for ore_id in museum:
        ore   = ORES.get(ore_id, {})
        photo = await get_ore_photo(ore_id)
        if photo:
            caption = (
                f"{ore.get('emoji','')} *{ore.get('name', ore_id)}*\n"
                f"_{ore.get('desc','')}_\n"
                f"Nilai: `{ore.get('value',0):,}` koin"
            )
            if photo.get("caption"):
                caption += f"\n💬 _{photo['caption']}_"
            await callback.message.answer_photo(
                photo=photo["photo_id"],
                caption=caption,
                parse_mode="Markdown"
            )
            sent_any = True

    if not sent_any:
        await callback.message.answer(
            "📸 Belum ada foto ore yang dipasang admin.\n"
            "Admin bisa pasang foto dengan `/admin_setorephoto <ore_id>`",
            reply_markup=back_main_kb(),
            parse_mode="Markdown"
        )
