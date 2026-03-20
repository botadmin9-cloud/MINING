import logging
from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, PhotoSize
from aiogram.filters import Command

from config import ADMIN_IDS, VIP_PRICES, VIP_TRANSFER_INFO, TOPUP_TRANSFER_INFO
from database import get_user, update_user, add_balance
from keyboards import (vip_shop_kb, vip_proof_kb, topup_shop_kb,
                        topup_proof_kb, shop_main_kb, back_main_kb)

router = Router()
logger = logging.getLogger(__name__)

# Temporary state storage (in-memory, per session)
_pending_vip  = {}   # uid -> {"plan_id": ..., "waiting_proof": bool}
_pending_topup = {}  # uid -> {"package": ..., "waiting_proof": bool}


def _is_admin(uid: int) -> bool:
    return uid in ADMIN_IDS


def _vip_status_text(user: dict) -> str:
    exp = user.get("vip_expires_at")
    if not exp:
        return "❌ Tidak aktif"
    try:
        exp_dt = datetime.fromisoformat(exp)
        if exp_dt > datetime.now():
            delta = exp_dt - datetime.now()
            days = delta.days
            return f"✅ Aktif — {days} hari lagi (exp: {exp_dt.strftime('%d/%m/%Y')})"
    except Exception:
        pass
    return "❌ Sudah kadaluarsa"


# ── SHOP VIP ───────────────────────────────────────────────────

@router.callback_query(F.data == "shop_vip")
async def cb_shop_vip(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.answer("❌ Ketik /start")
        return
    from config import VIP_COOLDOWN_REDUCTION, VIP_ENERGY_REGEN_BONUS, VIP_LUCK_BONUS, VIP_CRIT_BONUS
    vip_status = _vip_status_text(user)
    text = (
        "👑 *VIP Member — Mining Bot*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📊 *Status VIP kamu:* {vip_status}\n\n"
        "✨ *Keuntungan VIP:*\n"
        f"   ⏱️ Cooldown mining `{int((1-VIP_COOLDOWN_REDUCTION)*100)}%` lebih cepat\n"
        f"   ⚡ Energy regen `+{VIP_ENERGY_REGEN_BONUS}` per tick\n"
        f"   🍀 Luck `+{int(VIP_LUCK_BONUS*100)}%`\n"
        f"   💥 Critical `+{int(VIP_CRIT_BONUS*100)}%`\n"
        f"   👑 Badge VIP di profil\n\n"
        "💳 *Metode Pembayaran:* Transfer Bank\n\n"
        "📌 Pilih paket VIP di bawah, lakukan transfer,\n"
        "lalu kirim bukti transfer ke bot.\n"
        "Admin akan mengaktifkan VIP dalam 1x24 jam."
    )
    await callback.message.edit_text(text, reply_markup=vip_shop_kb(), parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data.startswith("vip_buy_"))
async def cb_vip_buy(callback: CallbackQuery):
    plan_id = callback.data.replace("vip_buy_", "")
    plan = VIP_PRICES.get(plan_id)
    if not plan:
        await callback.answer("❌ Paket tidak ditemukan!")
        return

    uid = callback.from_user.id
    _pending_vip[uid] = {"plan_id": plan_id, "waiting_proof": False}

    text = (
        f"👑 *Paket VIP: {plan['label']}*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"💰 *Harga:* Rp `{plan['price']:,}`\n"
        f"📅 *Durasi:* {plan['label']} ({plan['days']} hari)\n\n"
        "💳 *Transfer ke:*\n"
        f"`{VIP_TRANSFER_INFO}`\n\n"
        "📝 *Catatan transfer:* `VIP_{plan_id}_{uid}`\n\n"
        "Setelah transfer, klik tombol di bawah\n"
        "dan kirim foto bukti transfer.\n\n"
        "⚠️ VIP akan diaktifkan setelah admin verifikasi (maks 1x24 jam)"
    ).replace("{plan_id}", plan_id).replace("{uid}", str(uid))

    await callback.message.edit_text(text, reply_markup=vip_proof_kb(), parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "vip_proof")
async def cb_vip_proof(callback: CallbackQuery):
    uid = callback.from_user.id
    if uid not in _pending_vip:
        # Pilih paket dulu
        await callback.answer("Pilih paket VIP terlebih dahulu!", show_alert=True)
        return
    _pending_vip[uid]["waiting_proof"] = True
    await callback.answer()
    await callback.message.edit_text(
        "📸 *Kirim Bukti Transfer*\n\n"
        "Silakan kirim foto bukti transfer kamu sebagai *foto* (bukan file).\n\n"
        "Bot akan meneruskan ke admin untuk verifikasi.",
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "vip_confirm_transfer")
async def cb_vip_confirm(callback: CallbackQuery):
    uid = callback.from_user.id
    _pending_vip[uid] = _pending_vip.get(uid, {})
    _pending_vip[uid]["waiting_proof"] = True
    await callback.answer()
    await callback.message.edit_text(
        "📸 *Kirim Foto Bukti Transfer*\n\n"
        "Kirim foto bukti transfer sekarang.\n"
        "Admin akan memverifikasi dalam 1x24 jam.",
        parse_mode="Markdown"
    )


# ── SHOP TOPUP ─────────────────────────────────────────────────

@router.callback_query(F.data == "shop_topup")
async def cb_shop_topup(callback: CallbackQuery):
    text = (
        "💰 *Top Up Saldo Koin*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Beli saldo koin dengan transfer bank!\n\n"
        "📦 *Paket Top Up:*\n"
        "• Rp 10.000 → 10 Juta Koin\n"
        "• Rp 25.000 → 30 Juta Koin\n"
        "• Rp 50.000 → 75 Juta Koin\n"
        "• Rp 100.000 → 200 Juta Koin\n"
        "• Rp 200.000 → 500 Juta Koin\n"
        "• Rp 500.000 → 2 Milyar Koin 💎\n\n"
        "Pilih paket, transfer, lalu kirim bukti!"
    )
    await callback.message.edit_text(text, reply_markup=topup_shop_kb(), parse_mode="Markdown")
    await callback.answer()


TOPUP_PACKAGES = {
    "topup_10k":  {"label": "Rp 10.000",  "coins": 10_000_000},
    "topup_25k":  {"label": "Rp 25.000",  "coins": 30_000_000},
    "topup_50k":  {"label": "Rp 50.000",  "coins": 75_000_000},
    "topup_100k": {"label": "Rp 100.000", "coins": 200_000_000},
    "topup_200k": {"label": "Rp 200.000", "coins": 500_000_000},
    "topup_500k": {"label": "Rp 500.000", "coins": 2_000_000_000},
}


@router.callback_query(F.data.startswith("topup_") & ~F.data.in_({"topup_proof", "topup_confirm_transfer"}))
async def cb_topup_select(callback: CallbackQuery):
    pkg_id = callback.data
    pkg = TOPUP_PACKAGES.get(pkg_id)
    if not pkg:
        await callback.answer("❌ Paket tidak ditemukan!")
        return

    uid = callback.from_user.id
    _pending_topup[uid] = {"package": pkg_id, "waiting_proof": False}

    text = (
        f"💰 *Top Up: {pkg['label']}*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🪙 *Koin diterima:* `{pkg['coins']:,}` koin\n\n"
        "💳 *Transfer ke:*\n"
        f"`{TOPUP_TRANSFER_INFO}`\n\n"
        f"📝 *Catatan transfer:* `TOPUP_{pkg_id}_{uid}`\n\n"
        "Setelah transfer, klik tombol dan kirim foto bukti.\n"
        "⚠️ Saldo akan ditambahkan setelah admin verifikasi (maks 1x24 jam)"
    ).replace("{pkg_id}", pkg_id).replace("{uid}", str(uid))

    await callback.message.edit_text(text, reply_markup=topup_proof_kb(), parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "topup_confirm_transfer")
async def cb_topup_confirm(callback: CallbackQuery):
    uid = callback.from_user.id
    _pending_topup[uid] = _pending_topup.get(uid, {})
    _pending_topup[uid]["waiting_proof"] = True
    await callback.answer()
    await callback.message.edit_text(
        "📸 *Kirim Foto Bukti Transfer*\n\n"
        "Kirim foto bukti transfer top up sekarang.\n"
        "Admin akan memverifikasi dalam 1x24 jam.",
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "topup_proof")
async def cb_topup_proof(callback: CallbackQuery):
    uid = callback.from_user.id
    if uid not in _pending_topup:
        await callback.answer("Pilih paket top up terlebih dahulu!", show_alert=True)
        return
    _pending_topup[uid]["waiting_proof"] = True
    await callback.answer()
    await callback.message.edit_text(
        "📸 *Kirim Foto Bukti Transfer*\n\n"
        "Silakan kirim foto bukti transfer sebagai foto.\n"
        "Admin akan memverifikasi dalam 1x24 jam.",
        parse_mode="Markdown"
    )


# ── PHOTO HANDLER (bukti transfer) ─────────────────────────────

@router.message(F.photo)
async def handle_proof_photo(message: Message):
    uid = message.from_user.id
    bot = message.bot

    # Cek apakah menunggu bukti VIP
    if uid in _pending_vip and _pending_vip[uid].get("waiting_proof"):
        plan_id = _pending_vip[uid].get("plan_id", "unknown")
        plan = VIP_PRICES.get(plan_id, {})
        photo = message.photo[-1]
        user = await get_user(uid)
        uname = f"@{message.from_user.username}" if message.from_user.username else message.from_user.full_name

        # Kirim ke semua admin
        for admin_id in ADMIN_IDS:
            try:
                caption = (
                    f"👑 *Bukti Transfer VIP*\n\n"
                    f"👤 User: {uname} (`{uid}`)\n"
                    f"📦 Paket: {plan.get('label', plan_id)}\n"
                    f"💰 Harga: Rp {plan.get('price', '?'):,}\n"
                    f"📅 Durasi: {plan.get('days', '?')} hari\n\n"
                    f"✅ Untuk approve: `/admin_givevip {uid} {plan_id}`\n"
                    f"❌ Untuk tolak: Abaikan saja"
                )
                await bot.send_photo(admin_id, photo.file_id, caption=caption, parse_mode="Markdown")
            except Exception as e:
                logger.warning(f"Gagal kirim bukti VIP ke admin {admin_id}: {e}")

        await message.answer(
            "✅ *Bukti transfer VIP berhasil dikirim!*\n\n"
            "Admin akan memverifikasi dalam 1x24 jam.\n"
            "Kamu akan mendapat notifikasi saat VIP aktif. 👑",
            parse_mode="Markdown"
        )
        _pending_vip.pop(uid, None)
        return

    # Cek apakah menunggu bukti Top Up
    if uid in _pending_topup and _pending_topup[uid].get("waiting_proof"):
        pkg_id = _pending_topup[uid].get("package", "unknown")
        pkg = TOPUP_PACKAGES.get(pkg_id, {})
        photo = message.photo[-1]
        uname = f"@{message.from_user.username}" if message.from_user.username else message.from_user.full_name

        for admin_id in ADMIN_IDS:
            try:
                caption = (
                    f"💰 *Bukti Transfer Top Up*\n\n"
                    f"👤 User: {uname} (`{uid}`)\n"
                    f"📦 Paket: {pkg.get('label', pkg_id)}\n"
                    f"🪙 Koin: `{pkg.get('coins', 0):,}` koin\n\n"
                    f"✅ Untuk approve: `/admin_addcoin {uid} {pkg.get('coins', 0)}`\n"
                    f"❌ Untuk tolak: Abaikan saja"
                )
                await bot.send_photo(admin_id, photo.file_id, caption=caption, parse_mode="Markdown")
            except Exception as e:
                logger.warning(f"Gagal kirim bukti topup ke admin {admin_id}: {e}")

        await message.answer(
            "✅ *Bukti transfer Top Up berhasil dikirim!*\n\n"
            "Admin akan memverifikasi dalam 1x24 jam.\n"
            "Kamu akan mendapat notifikasi saat saldo ditambahkan. 💰",
            parse_mode="Markdown"
        )
        _pending_topup.pop(uid, None)
        return


# ── ADMIN: GIVE VIP ────────────────────────────────────────────

@router.message(Command("admin_givevip"))
async def cmd_admin_givevip(message: Message):
    if not _is_admin(message.from_user.id):
        return

    parts = message.text.strip().split()
    if len(parts) < 3:
        await message.answer(
            "❌ Format salah!\n"
            "Gunakan: `/admin_givevip <user_id> <plan_id>`\n\n"
            "Plan ID: `1_month`, `3_months`, `6_months`, `lifetime`",
            parse_mode="Markdown"
        )
        return

    try:
        target_uid = int(parts[1])
        plan_id = parts[2]
    except ValueError:
        await message.answer("❌ user_id harus angka!", parse_mode="Markdown")
        return

    plan = VIP_PRICES.get(plan_id)
    if not plan:
        await message.answer(
            f"❌ Plan `{plan_id}` tidak ditemukan!\n"
            "Plan tersedia: `1_month`, `3_months`, `6_months`, `lifetime`",
            parse_mode="Markdown"
        )
        return

    user = await get_user(target_uid)
    if not user:
        await message.answer(f"❌ User `{target_uid}` tidak ditemukan!", parse_mode="Markdown")
        return

    # Hitung expiry — extend jika sudah VIP
    now = datetime.now()
    current_exp = user.get("vip_expires_at")
    if current_exp:
        try:
            current_exp_dt = datetime.fromisoformat(current_exp)
            if current_exp_dt > now:
                base_dt = current_exp_dt  # extend dari expiry saat ini
            else:
                base_dt = now
        except Exception:
            base_dt = now
    else:
        base_dt = now

    new_exp = base_dt + timedelta(days=plan["days"])
    await update_user(target_uid,
                      vip_expires_at=new_exp.isoformat(),
                      vip_type=plan_id)

    # Grant achievement
    if "vip_member" not in user.get("achievements", []):
        from config import ACHIEVEMENTS
        ach = ACHIEVEMENTS.get("vip_member", {})
        new_ach = user.get("achievements", []) + ["vip_member"]
        await update_user(target_uid, achievements=new_ach)
        if ach.get("reward"):
            await add_balance(target_uid, ach["reward"], "Achievement: VIP Member")

    # Notifikasi ke user
    try:
        bot = message.bot
        uname = user.get("first_name") or f"User {target_uid}"
        await bot.send_message(
            target_uid,
            f"🎉 *Selamat! VIP kamu telah diaktifkan!*\n\n"
            f"👑 Paket: *{plan['label']}*\n"
            f"📅 Berlaku hingga: *{new_exp.strftime('%d/%m/%Y')}*\n\n"
            f"✨ Nikmati keuntungan VIP:\n"
            f"   ⏱️ Cooldown mining lebih cepat\n"
            f"   ⚡ Energy regen lebih cepat\n"
            f"   🍀 Luck lebih tinggi\n"
            f"   💥 Critical lebih tinggi\n\n"
            f"Terima kasih sudah mendukung Mining Bot! 🙏",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.warning(f"Gagal notifikasi VIP ke user {target_uid}: {e}")

    admin_uname = message.from_user.full_name
    await message.answer(
        f"✅ *VIP berhasil diberikan!*\n\n"
        f"👤 User: `{target_uid}`\n"
        f"📦 Paket: *{plan['label']}*\n"
        f"📅 Expire: *{new_exp.strftime('%d/%m/%Y %H:%M')}*\n"
        f"👑 Diberikan oleh: {admin_uname}",
        parse_mode="Markdown"
    )


@router.message(Command("admin_revokevip"))
async def cmd_admin_revokevip(message: Message):
    if not _is_admin(message.from_user.id):
        return

    parts = message.text.strip().split()
    if len(parts) < 2:
        await message.answer("❌ Format: `/admin_revokevip <user_id>`", parse_mode="Markdown")
        return

    try:
        target_uid = int(parts[1])
    except ValueError:
        await message.answer("❌ user_id harus angka!", parse_mode="Markdown")
        return

    user = await get_user(target_uid)
    if not user:
        await message.answer(f"❌ User `{target_uid}` tidak ditemukan!", parse_mode="Markdown")
        return

    await update_user(target_uid, vip_expires_at=None, vip_type=None)

    try:
        await message.bot.send_message(
            target_uid,
            "⚠️ *VIP kamu telah dicabut oleh admin.*\n\nHubungi admin jika ada pertanyaan.",
            parse_mode="Markdown"
        )
    except Exception:
        pass

    await message.answer(f"✅ VIP user `{target_uid}` berhasil dicabut.", parse_mode="Markdown")


@router.message(Command("vip"))
async def cmd_vip_status(message: Message):
    """Cek status VIP."""
    user = await get_user(message.from_user.id)
    if not user:
        await message.answer("❌ Ketik /start dulu!")
        return

    from config import VIP_COOLDOWN_REDUCTION, VIP_ENERGY_REGEN_BONUS, VIP_LUCK_BONUS, VIP_CRIT_BONUS
    vip_status = _vip_status_text(user)
    text = (
        "👑 *Status VIP Kamu*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📊 Status: {vip_status}\n\n"
        "✨ *Keuntungan VIP:*\n"
        f"   ⏱️ Cooldown `{int((1-VIP_COOLDOWN_REDUCTION)*100)}%` lebih cepat\n"
        f"   ⚡ Energy regen `+{VIP_ENERGY_REGEN_BONUS}` per tick\n"
        f"   🍀 Luck `+{int(VIP_LUCK_BONUS*100)}%`\n"
        f"   💥 Critical `+{int(VIP_CRIT_BONUS*100)}%`\n\n"
        "💳 Beli VIP di *🏪 Shop → 👑 VIP Member*"
    )
    await message.answer(text, parse_mode="Markdown")
