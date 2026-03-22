from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from game import claim_daily
from middlewares import register_message_owner

router = Router()


@router.message(F.text == "📅 Daily")
@router.message(Command("daily"))
async def cmd_daily(message: Message):
    ok, msg = await claim_daily(message.from_user.id)
    _sent = await message.answer(msg, parse_mode="Markdown")
    if _sent: register_message_owner(_sent.chat.id, _sent.message_id, message.from_user.id)
