from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from config import ADMIN_IDS
from database import get_leaderboard_by, get_user_rank, get_user
from keyboards import leaderboard_kb

router = Router()

MEDALS = ["🥇", "🥈", "🥉"] + ["🏅"] * 7

LB_FIELDS = {
    "balance":    ("💰 Total Saldo", "total_earned"),
    "mine_count": ("⛏️ Total Mining", "mine_count"),
    "total_kg":   ("⚖️ Total KG",     "total_kg_mined"),
    "ore_count":  ("🪨 Total Ore",    "total_mined"),
}

WEEKLY_REWARD = {
    1: 500000,
    2: 250000,
    3: 100000,
}


@router.message(F.text == "🏆 Leaderboard")
@router.message(Command("leaderboard"))
async def show_leaderboard(message: Message):
    text = await _build_lb(message.from_user.id, "balance", "weekly")
    await message.answer(text, reply_markup=leaderboard_kb(), parse_mode="Markdown")


@router.callback_query(F.data == "lb_refresh")
async def cb_lb_refresh(callback: CallbackQuery):
    text = await _build_lb(callback.from_user.id, "balance", "weekly")
    try:
        await callback.message.edit_text(text, reply_markup=leaderboard_kb(), parse_mode="Markdown")
    except Exception:
        pass
    await callback.answer("🔄 Diperbarui!")


@router.callback_query(F.data.startswith("lb_"))
async def cb_lb_switch(callback: CallbackQuery):
    data = callback.data
    # lb_weekly_balance, lb_monthly_mine_count, dll
    parts = data.split("_", 2)
    if len(parts) < 3:
        # lb_refresh sudah ditangani di atas, tapi jaga-jaga
        await callback.answer()
        return
    period = parts[1]   # weekly / monthly
    field  = parts[2]   # balance / mine_count / total_kg / ore_count
    if field not in LB_FIELDS:
        field = "balance"
    if period not in ("weekly", "monthly"):
        period = "weekly"

    text = await _build_lb(callback.from_user.id, field, period)
    try:
        await callback.message.edit_text(text, reply_markup=leaderboard_kb(period, field), parse_mode="Markdown")
    except Exception:
        pass
    await callback.answer()


async def _build_lb(user_id: int, field: str = "balance", period: str = "weekly") -> str:
    from database import get_leaderboard_by
    db_field = LB_FIELDS.get(field, ("💰 Total Saldo", "total_earned"))[1]
    label    = LB_FIELDS.get(field, ("💰 Total Saldo", "total_earned"))[0]
    leaders  = await get_leaderboard_by(db_field, 10)
    rank     = await get_user_rank(user_id)

    period_label = "📅 Weekly" if period == "weekly" else "🗓️ Monthly"
    reward_note = ""
    if period == "weekly":
        reward_note = "\n💡 Top 3 mendapat reward saldo saat reset weekly!\n🏆 Reward: 🥇500K | 🥈250K | 🥉100K\n"

    lines = [f"🏆 *TOP 10 — {label}*\n{period_label}{reward_note}\n"]
    for i, p in enumerate(leaders):
        display = (p.get("display_name") or "").strip()
        if not display:
            display = (f"@{p['username']}" if p.get("username") else p.get("first_name", "???"))
        rebirth = f" 🔄{p['rebirth_count']}" if p.get("rebirth_count", 0) > 0 else ""
        value = p.get(db_field, 0)
        if db_field == "total_kg_mined":
            from config import format_kg
            val_str = format_kg(value)
        else:
            val_str = f"{int(value):,}"
        lines.append(
            f"{MEDALS[i]} `{i+1}.` {display}{rebirth}\n"
            f"       Lv.{p['level']} | {label}: `{val_str}`"
        )
    lines.append(f"\n📊 Rank kamu: *#{rank}*")
    return "\n".join(lines)
