from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable

from database import get_user, create_user, update_user


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
