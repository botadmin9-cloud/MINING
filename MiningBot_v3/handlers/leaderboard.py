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
    try:
        await callback.message.edit_text(text, reply_markup=leaderboard_kb(), parse_mode="Markdown")
    except Exception:
        pass
    await callback.answer("🔄 Diperbarui!")


async def _build_lb(user_id: int) -> str:
    leaders = await get_leaderboard(10)
    rank    = await get_user_rank(user_id)
    lines   = ["🏆 *TOP 10 PENAMBANG*\n"]
    for i, p in enumerate(leaders):
        # ✅ Tampilkan display_name jika ada, fallback ke username/first_name
        display = (p.get("display_name") or "").strip()
        if not display:
            display = (f"@{p['username']}" if p.get("username")
                       else p.get("first_name", "???"))
        rebirth = f" 🔄{p['rebirth_count']}" if p.get("rebirth_count", 0) > 0 else ""
        total = p.get("total_earned", p.get("total_mined", 0))
        mc = p.get("mine_count", 0)
        lines.append(
            f"{MEDALS[i]} `{i+1}.` {display}{rebirth}\n"
            f"       Lv.{p['level']} | ⛏️{mc:,}x | 💰`{total:,}` koin"
        )
    lines.append(f"\n📊 Rank kamu: *#{rank}*")
    return "\n".join(lines)
