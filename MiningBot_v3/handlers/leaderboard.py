from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from database import get_leaderboard, get_user_rank, get_user
from keyboards import leaderboard_kb

router = Router()

MEDALS = ["🥇", "🥈", "🥉"] + ["🏅"] * 7


@router.message(F.text == "🏆 Leaderboard")
@router.message(Command("leaderboard"))
async def show_leaderboard(message: Message):
    text = await _build_lb(message.from_user.id)
    await message.answer(text, reply_markup=leaderboard_kb(), parse_mode="Markdown")


@router.callback_query(F.data == "lb_refresh")
async def cb_lb_refresh(callback: CallbackQuery):
    text = await _build_lb(callback.from_user.id)
    await callback.message.edit_text(text, reply_markup=leaderboard_kb(), parse_mode="Markdown")
    await callback.answer("🔄 Diperbarui!")


async def _build_lb(user_id: int) -> str:
    leaders = await get_leaderboard(10)
    rank    = await get_user_rank(user_id)
    lines   = ["🏆 *TOP 10 PENAMBANG*\n"]
    for i, p in enumerate(leaders):
        name = p.get("username") and f"@{p['username']}" or p.get("first_name", "???")
        rebirth = f" 🔄{p['rebirth_count']}" if p.get("rebirth_count", 0) > 0 else ""
        lines.append(
            f"{MEDALS[i]} `{i+1}.` {name}{rebirth}\n"
            f"       Lv.{p['level']} | `{p['total_mined']:,}` koin"
        )
    lines.append(f"\n📊 Rank kamu: *#{rank}*")
    return "\n".join(lines)
