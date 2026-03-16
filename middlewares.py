"""
🛡️ Middlewares — Auto-create user on first message
"""
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable

from database import get_user, create_user


class AutoRegisterMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        user = None
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
        return await handler(event, data)
