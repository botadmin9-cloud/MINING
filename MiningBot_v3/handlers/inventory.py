from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from datetime import datetime

from database import get_user
from game import use_item, get_active_buffs
from keyboards import inventory_kb
from config import ITEMS
from middlewares import register_message_owner

router = Router()


@router.message(F.text == "🎁 Inventaris")
@router.message(Command("inventory"))
async def show_inventory(message: Message):
    user = await get_user(message.from_user.id)
    if not user:
        _sent = await message.answer("❌ Ketik /start!")
        if _sent: register_message_owner(_sent.chat.id, _sent.message_id, message.from_user.id)
        return

    text, kb = _build_inventory_text(user)
    _sent = await message.answer(text, reply_markup=kb, parse_mode="Markdown")
    if _sent: register_message_owner(_sent.chat.id, _sent.message_id, message.from_user.id)


def _build_inventory_text(user: dict):
    """Build inventory text dan keyboard — dipakai ulang agar konsisten."""
    inv = {}
    raw = user.get("inventory") or {}
    if isinstance(raw, dict):
        inv = {k: v for k, v in raw.items() if v > 0}

    if inv:
        lines = []
        for item_id, qty in inv.items():
            item = ITEMS.get(item_id)
            if item:
                lines.append(f"   {item['emoji']} *{item['name']}* x{qty}\n      _{item['description']}_")
        inv_txt = "\n".join(lines) if lines else "   _Inventaris kosong. Beli item di 🏪 Shop!_"
    else:
        inv_txt = "   _Inventaris kosong. Beli item di 🏪 Shop!_"

    buffs = get_active_buffs(user)
    buff_txt = ""
    if buffs:
        buff_txt = "\n\n⚡ *Buff Aktif:*\n"
        for k, v in buffs.items():
            exp = v.get("expires", "")
            try:
                exp_dt = datetime.fromisoformat(exp)
                rem = exp_dt - datetime.now()
                mins = max(0, int(rem.total_seconds() // 60))
                buff_txt += f"   • {k}: {mins} menit tersisa\n"
            except Exception:
                buff_txt += f"   • {k}\n"

    text = (
        f"🎁 *Inventaris Item*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{inv_txt}"
        f"{buff_txt}\n\n"
        f"Tekan item untuk menggunakannya:"
    )
    kb = inventory_kb(inv)
    return text, kb


@router.callback_query(F.data.startswith("use_item_"))
async def cb_use_item(callback: CallbackQuery):
    item_id = callback.data.replace("use_item_", "")
    ok, msg = await use_item(callback.from_user.id, item_id)
    await callback.answer(msg[:200], show_alert=True)

    # ✅ Selalu refresh full pesan setelah pakai item (bukan hanya markup)
    user = await get_user(callback.from_user.id)
    if user:
        text, kb = _build_inventory_text(user)
        try:
            await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
        except Exception:
            try:
                _sent = await callback.message.answer(text, reply_markup=kb, parse_mode="Markdown")
                if _sent: register_message_owner(_sent.chat.id, _sent.message_id, callback.from_user.id)
            except Exception:
                pass
