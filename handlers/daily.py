from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from game import claim_daily

router = Router()


@router.message(F.text == "🎁 Daily")
@router.message(Command("daily"))
async def cmd_daily(message: Message):
    ok, msg = await claim_daily(message.from_user.id)
    await message.answer(msg, parse_mode="Markdown")
