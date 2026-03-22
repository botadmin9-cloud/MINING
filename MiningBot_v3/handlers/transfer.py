from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import ORES, ADMIN_IDS, TRANSFER_ORE_MAX_SEND_WEEKLY, TRANSFER_ORE_MAX_RECEIVE_WEEKLY
from database import (get_user, update_user, add_ore_to_inventory,
                      remove_ore_from_inventory, get_transfer_week_counts,
                      increment_transfer_send, increment_transfer_receive,
                      is_dynamic_admin)
from keyboards import back_main_kb

router = Router()


class TransferOreState(StatesGroup):
    waiting_target_id = State()
    waiting_ore       = State()
    waiting_qty       = State()
    waiting_confirm   = State()


async def _is_admin(uid: int) -> bool:
    """Cek admin statis (.env) ATAU dinamis (DB)."""
    if uid in ADMIN_IDS:
        return True
    return await is_dynamic_admin(uid)


# ══════════════════════════════════════════════════════════════
# /transfer — Mulai proses transfer
# ══════════════════════════════════════════════════════════════
@router.message(Command("transfer"))
async def cmd_transfer(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    if not user:
        await message.answer("❌ Ketik /start terlebih dahulu!")
        return

    ore_inv = {k: v for k, v in user.get("ore_inventory", {}).items() if v > 0}
    if not ore_inv:
        await message.answer(
            "📦 *Inventory Ore Kosong!*\n\nMulai mining dulu untuk mendapat ore.",
            parse_mode="Markdown"
        )
        return

    # Cek batas kirim mingguan
    counts = await get_transfer_week_counts(message.from_user.id)
    send_left = TRANSFER_ORE_MAX_SEND_WEEKLY - counts["send"]

    if send_left <= 0 and not await _is_admin(message.from_user.id):
        await message.answer(
            f"⛔ *Batas Transfer Mingguan Tercapai!*\n\n"
            f"Kamu sudah mengirim {TRANSFER_ORE_MAX_SEND_WEEKLY}x transfer minggu ini.\n"
            f"Batas reset setiap hari Senin pukul 00.00.",
            parse_mode="Markdown"
        )
        return

    await state.set_state(TransferOreState.waiting_target_id)
    await message.answer(
        f"📦 *Transfer Ore ke Pemain Lain*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📊 Sisa kirim minggu ini: *{send_left}x* dari {TRANSFER_ORE_MAX_SEND_WEEKLY}x\n\n"
        f"Masukkan *Telegram User ID* penerima:\n"
        f"_(Minta penerima ketik /profile untuk lihat ID mereka)_",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Batal", callback_data="transfer_cancel")]
        ])
    )


@router.callback_query(F.data == "transfer_cancel")
async def cb_transfer_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await callback.message.edit_text(
            "❌ Transfer dibatalkan.",
            reply_markup=back_main_kb()
        )
    except Exception:
        pass
    await callback.answer()


# ── Step 1: Terima User ID target ─────────────────────────────
@router.message(TransferOreState.waiting_target_id)
async def process_transfer_target(message: Message, state: FSMContext):
    try:
        target_id = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Masukkan angka User ID yang valid! Coba lagi:")
        return

    if target_id == message.from_user.id:
        await message.answer("❌ Tidak bisa transfer ke diri sendiri!")
        return

    target_user = await get_user(target_id)
    if not target_user:
        await message.answer(
            f"❌ User dengan ID `{target_id}` tidak ditemukan.\n"
            f"Pastikan ID benar dan user sudah pernah /start.",
            parse_mode="Markdown"
        )
        return

    # Cek batas terima mingguan penerima
    target_counts = await get_transfer_week_counts(target_id)
    receive_left = TRANSFER_ORE_MAX_RECEIVE_WEEKLY - target_counts["receive"]
    if receive_left <= 0 and not await _is_admin(message.from_user.id):
        target_name = target_user.get("display_name") or target_user.get("first_name", "User")
        await message.answer(
            f"⛔ *Penerima sudah mencapai batas!*\n\n"
            f"*{target_name}* sudah menerima {TRANSFER_ORE_MAX_RECEIVE_WEEKLY}x transfer minggu ini.\n"
            f"Coba lagi minggu depan.",
            parse_mode="Markdown"
        )
        return

    # Simpan target, minta pilih ore
    target_name = target_user.get("display_name") or target_user.get("first_name", "User")
    await state.update_data(target_id=target_id, target_name=target_name)

    # Tampilkan daftar ore yang dimiliki
    user = await get_user(message.from_user.id)
    ore_inv = {k: v for k, v in user.get("ore_inventory", {}).items() if v > 0}
    sorted_ores = sorted(ore_inv.items(), key=lambda x: ORES.get(x[0], {}).get("value", 0), reverse=True)

    rows = []
    for ore_id, qty in sorted_ores[:20]:
        ore = ORES.get(ore_id, {})
        rows.append([InlineKeyboardButton(
            text=f"{ore.get('emoji','')} {ore.get('name', ore_id)} x{qty}",
            callback_data=f"transfer_ore_{ore_id}"
        )])
    rows.append([InlineKeyboardButton(text="❌ Batal", callback_data="transfer_cancel")])

    await state.set_state(TransferOreState.waiting_ore)
    await message.answer(
        f"✅ Penerima: *{target_name}* (ID: `{target_id}`)\n\n"
        f"Pilih ore yang ingin ditransfer:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
    )


# ── Step 2: Pilih ore ─────────────────────────────────────────
@router.callback_query(TransferOreState.waiting_ore, F.data.startswith("transfer_ore_"))
async def cb_transfer_ore_select(callback: CallbackQuery, state: FSMContext):
    ore_id = callback.data.replace("transfer_ore_", "")
    ore = ORES.get(ore_id)
    user = await get_user(callback.from_user.id)

    if not ore or not user:
        await callback.answer("❌ Ore tidak ditemukan!")
        return

    qty_have = user.get("ore_inventory", {}).get(ore_id, 0)
    if qty_have <= 0:
        await callback.answer("❌ Ore sudah habis!", show_alert=True)
        return

    await state.update_data(ore_id=ore_id, ore_name=ore["name"],
                             ore_emoji=ore["emoji"], qty_have=qty_have)
    await state.set_state(TransferOreState.waiting_qty)

    try:
        await callback.message.edit_text(
            f"📦 Ore dipilih: {ore['emoji']} *{ore['name']}*\n"
            f"Kamu punya: `{qty_have}` buah\n\n"
            f"Ketik jumlah yang ingin ditransfer (1 - {qty_have}):",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❌ Batal", callback_data="transfer_cancel")]
            ])
        )
    except Exception:
        pass
    await callback.answer()


# ── Step 3: Jumlah ore ────────────────────────────────────────
@router.message(TransferOreState.waiting_qty)
async def process_transfer_qty(message: Message, state: FSMContext):
    try:
        qty = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Masukkan angka yang valid!")
        return

    data = await state.get_data()
    if qty <= 0 or qty > data["qty_have"]:
        await message.answer(f"❌ Jumlah harus antara 1 dan {data['qty_have']}!")
        return

    await state.update_data(qty=qty)
    await state.set_state(TransferOreState.waiting_confirm)

    await message.answer(
        f"📋 *Konfirmasi Transfer*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📦 Ore   : {data['ore_emoji']} *{data['ore_name']}* x{qty}\n"
        f"👤 Ke    : *{data['target_name']}* (ID: `{data['target_id']}`)\n\n"
        f"⚠️ Transfer tidak bisa dibatalkan setelah dikonfirmasi!\n\n"
        f"Lanjutkan?",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Ya, Transfer!", callback_data="transfer_confirm_yes"),
                InlineKeyboardButton(text="❌ Batal", callback_data="transfer_cancel"),
            ]
        ])
    )


# ── Step 4: Konfirmasi dan eksekusi ───────────────────────────
@router.callback_query(TransferOreState.waiting_confirm, F.data == "transfer_confirm_yes")
async def cb_transfer_confirm(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    sender_id  = callback.from_user.id
    target_id  = data["target_id"]
    ore_id     = data["ore_id"]
    qty        = data["qty"]
    ore_name   = data["ore_name"]
    ore_emoji  = data["ore_emoji"]
    target_name = data["target_name"]
    is_admin   = await _is_admin(sender_id)

    await state.clear()

    # Cek ulang stok
    sender = await get_user(sender_id)
    if not sender or sender.get("ore_inventory", {}).get(ore_id, 0) < qty:
        await callback.answer("❌ Ore tidak cukup!", show_alert=True)
        return

    # Cek ulang batas mingguan (double-check)
    if not is_admin:
        counts_s = await get_transfer_week_counts(sender_id)
        if counts_s["send"] >= TRANSFER_ORE_MAX_SEND_WEEKLY:
            await callback.answer("⛔ Batas kirim mingguan tercapai!", show_alert=True)
            return
        counts_r = await get_transfer_week_counts(target_id)
        if counts_r["receive"] >= TRANSFER_ORE_MAX_RECEIVE_WEEKLY:
            await callback.answer("⛔ Penerima sudah mencapai batas terima!", show_alert=True)
            return

    # FIX: Cek kapasitas bag penerima sebelum eksekusi transfer
    target_user = await get_user(target_id)
    if not target_user:
        await callback.answer("❌ Penerima tidak ditemukan!", show_alert=True)
        return
    if not is_admin:
        target_ore_inv = target_user.get("ore_inventory", {})
        target_bag_used = sum(target_ore_inv.values())
        target_bag_slots = target_user.get("bag_slots", 50)
        if target_bag_used + qty > target_bag_slots:
            await callback.answer(
                f"❌ Bag penerima penuh! ({target_bag_used}/{target_bag_slots} slot). "
                f"Tidak bisa menerima {qty} ore lagi.",
                show_alert=True
            )
            return

    # Hitung KG yang akan ditransfer SEBELUM remove, karena data masih fresh di sender
    _ore_kg_data = sender.get("ore_kg_data", {})
    _total_sender_kg = _ore_kg_data.get(ore_id, 0.0)
    _sender_qty_before = sender.get("ore_inventory", {}).get(ore_id, 0)
    if _total_sender_kg > 0 and _sender_qty_before > 0:
        # Gunakan berat rata-rata aktual milik sender
        _avg_kg = round((_total_sender_kg / _sender_qty_before) * qty, 4)
    else:
        # Fallback ke rata-rata berdasarkan config
        _ore_data = ORES.get(ore_id, {})
        _avg_kg = round((_ore_data.get("kg_min", 0.5) + _ore_data.get("kg_max", 2.0)) / 2 * qty, 4)

    # Eksekusi transfer
    removed = await remove_ore_from_inventory(sender_id, ore_id, qty)
    if not removed:
        await callback.answer("❌ Gagal mengurangi ore!", show_alert=True)
        return

    await add_ore_to_inventory(target_id, ore_id, qty, _avg_kg)

    # Update hitungan (skip untuk admin)
    if not is_admin:
        await increment_transfer_send(sender_id)
        await increment_transfer_receive(target_id)

    # Achievement first transfer
    from game import _grant_if_new
    await _grant_if_new(sender_id, "transfer_ore_first")

    sender_tag = f"@{callback.from_user.username}" if callback.from_user.username else callback.from_user.first_name

    # Notifikasi ke penerima
    try:
        await callback.bot.send_message(
            target_id,
            f"🎁 *Kamu menerima Transfer Ore!*\n\n"
            f"{ore_emoji} *{ore_name}* x{qty}\n"
            f"👤 Dari: {sender_tag}\n\n"
            f"Ore sudah masuk ke Bag kamu!",
            parse_mode="Markdown"
        )
    except Exception:
        pass

    # Cek sisa limit
    counts_after = await get_transfer_week_counts(sender_id)
    send_used = counts_after["send"] if not is_admin else 0
    send_left = max(0, TRANSFER_ORE_MAX_SEND_WEEKLY - send_used)

    try:
        await callback.message.edit_text(
            f"✅ *Transfer Berhasil!*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{ore_emoji} *{ore_name}* x{qty}\n"
            f"👤 Dikirim ke: *{target_name}*\n\n"
            f"📊 Sisa kirim minggu ini: *{send_left}x*",
            parse_mode="Markdown",
            reply_markup=back_main_kb()
        )
    except Exception:
        pass
    await callback.answer("✅ Transfer berhasil!")


# ── Info transfer ─────────────────────────────────────────────
@router.message(Command("transferinfo"))
async def cmd_transfer_info(message: Message):
    user = await get_user(message.from_user.id)
    if not user:
        await message.answer("❌ Ketik /start!")
        return

    counts = await get_transfer_week_counts(message.from_user.id)
    send_used    = counts["send"]
    receive_used = counts["receive"]
    send_left    = max(0, TRANSFER_ORE_MAX_SEND_WEEKLY - send_used)
    receive_left = max(0, TRANSFER_ORE_MAX_RECEIVE_WEEKLY - receive_used)

    await message.answer(
        f"📦 *Info Transfer Ore*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📤 Kirim minggu ini    : `{send_used}/{TRANSFER_ORE_MAX_SEND_WEEKLY}` (sisa: {send_left}x)\n"
        f"📥 Terima minggu ini   : `{receive_used}/{TRANSFER_ORE_MAX_RECEIVE_WEEKLY}` (sisa: {receive_left}x)\n\n"
        f"🔄 Reset: setiap hari *Senin* pukul 00.00\n\n"
        f"Gunakan /transfer untuk kirim ore!",
        parse_mode="Markdown"
    )
