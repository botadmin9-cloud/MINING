from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable

from database import get_user, create_user, update_user

# ─── Message Owner Cache ───────────────────────────────────────────────────────
# Simpan siapa yang memiliki setiap pesan bot yang punya inline keyboard.
# Key: (chat_id, message_id)  →  Value: user_id pemilik
_message_owner: Dict[tuple, int] = {}
_MAX_CACHE = 5000  # batas agar RAM tidak penuh


def register_message_owner(chat_id: int, message_id: int, user_id: int) -> None:
    """Daftarkan pemilik pesan bot (dipanggil setelah bot kirim pesan dengan tombol)."""
    global _message_owner
    if len(_message_owner) >= _MAX_CACHE:
        # Hapus 500 entry terlama jika cache penuh
        for key in list(_message_owner.keys())[:500]:
            del _message_owner[key]
    _message_owner[(chat_id, message_id)] = user_id


def get_message_owner(chat_id: int, message_id: int) -> int | None:
    """Ambil user_id pemilik pesan, atau None jika tidak terdaftar."""
    return _message_owner.get((chat_id, message_id))


# Callback data yang boleh dipencet siapa saja (tidak perlu cek pemilik)
_PUBLIC_CALLBACKS = {
    "noop",
    "close_welcome",
    "main_menu",
    "lb_refresh",
}

# Prefix callback data yang boleh dipencet siapa saja
_PUBLIC_PREFIXES = (
    "lb_",
)


class OwnerOnlyCallbackMiddleware(BaseMiddleware):
    """
    Blokir inline keyboard callback dari user yang BUKAN pemilik pesan.
    Hanya berlaku jika pesan sudah terdaftar via register_message_owner().
    """
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        if isinstance(event, CallbackQuery) and event.message:
            cb_data = event.data or ""

            # Lewati callback yang memang publik
            if cb_data in _PUBLIC_CALLBACKS:
                return await handler(event, data)
            if cb_data.startswith(_PUBLIC_PREFIXES):
                return await handler(event, data)

            chat_id = event.message.chat.id
            msg_id  = event.message.message_id
            uid     = event.from_user.id
            owner   = get_message_owner(chat_id, msg_id)

            if owner is not None and owner != uid:
                await event.answer(
                    "⛔ Tombol ini hanya bisa digunakan oleh pemain yang membuka menu ini.",
                    show_alert=True
                )
                return  # Blokir handler, jangan lanjutkan

        return await handler(event, data)


class AutoRegisterMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        if isinstance(event, (Message, CallbackQuery)):
            tg_user = event.from_user
            if tg_user and not tg_user.is_bot:
                existing = await get_user(tg_user.id)
                if not existing:
                    await create_user(
                        tg_user.id,
                        tg_user.username or "",
                        tg_user.first_name or "Miner"
                    )
                else:
                    # Cek apakah user di-ban
                    if existing.get("is_banned"):
                        reason = existing.get("ban_reason") or "Tidak ada alasan"
                        ban_msg = (
                            f"🚫 *Akun kamu telah dibanned!*\n\n"
                            f"📋 Alasan: _{reason}_\n\n"
                            f"Hubungi admin jika ini adalah kesalahan."
                        )
                        try:
                            if isinstance(event, Message):
                                await event.answer(ban_msg, parse_mode="Markdown")
                            elif isinstance(event, CallbackQuery):
                                await event.answer("🚫 Akun kamu dibanned!", show_alert=True)
                        except Exception:
                            pass
                        return  # Blokir handler

                    # Update username/first_name jika berubah
                    new_username = tg_user.username or ""
                    new_fname = tg_user.first_name or "Miner"
                    needs_update = {}
                    if existing.get("username") != new_username:
                        needs_update["username"] = new_username
                    if existing.get("first_name") != new_fname:
                        needs_update["first_name"] = new_fname
                        old_fname = existing.get("first_name", "")
                        old_display = existing.get("display_name", "")
                        if not old_display or old_display == old_fname:
                            needs_update["display_name"] = new_fname
                    if needs_update:
                        await update_user(tg_user.id, **needs_update)
        return await handler(event, data)
