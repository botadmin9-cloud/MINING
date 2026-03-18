import random
import logging
from datetime import datetime, timedelta
from typing import Tuple, Optional

from config import (TOOLS, ORES, ITEMS, ACHIEVEMENTS, ZONES,
                    ENERGY_REGEN_RATE, ENERGY_COOLDOWN_MINUTES,
                    LUCKY_CHANCE, CRITICAL_CHANCE,
                    xp_for_level, MAX_LEVEL, ADMIN_IDS,
                    calculate_sell_price, get_random_kg, format_kg,
                    KG_PRICE_MULTIPLIER, XP_BASE_MULTIPLIER)
from database import (get_user, update_user, log_mine, add_balance,
                       add_ore_to_inventory, remove_ore_from_inventory)

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════
# ENERGY SYSTEM
# ══════════════════════════════════════════════════════════════
async def regen_energy(user: dict) -> dict:
    now = datetime.now()
    last = user.get("last_energy_regen")
    if last:
        try:
            last_dt = datetime.fromisoformat(last)
            minutes = (now - last_dt).total_seconds() / 60
            gain = int(minutes / ENERGY_COOLDOWN_MINUTES)
            if gain > 0:
                new_e = min(user["energy"] + gain, user["max_energy"])
                await update_user(user["user_id"], energy=new_e,
                                  last_energy_regen=now.isoformat())
                user["energy"] = new_e
        except Exception:
            pass
    else:
        await update_user(user["user_id"], last_energy_regen=now.isoformat())
    return user


def energy_full_in(user: dict) -> str:
    if user["energy"] >= user["max_energy"]:
        return "✅ PENUH"
    needed = user["max_energy"] - user["energy"]
    total_mins = needed * ENERGY_COOLDOWN_MINUTES
    h, m = divmod(int(total_mins), 60)
    return f"{h}j {m}m" if h else f"{m}m"


# ══════════════════════════════════════════════════════════════
# SPEED COOLDOWN SYSTEM
# ══════════════════════════════════════════════════════════════
def get_mine_cooldown_seconds(user: dict, is_admin: bool = False) -> int:
    if is_admin:
        return 1
    tool_id = user.get("current_tool", "stone_pick")
    tool = TOOLS.get(tool_id, TOOLS["stone_pick"])
    base_delay = tool.get("speed_delay", 60)
    buffs = get_active_buffs(user)
    speed_mult = get_buff_val(buffs, "speed_boost", 1.0)
    if speed_mult < 1.0:
        base_delay = int(base_delay * speed_mult)
    return max(5, base_delay)


async def check_mine_cooldown(user: dict, is_admin: bool = False) -> Tuple[bool, str]:
    if is_admin:
        return True, ""
    last_mine = user.get("last_mine_time")
    if not last_mine:
        return True, ""
    try:
        last_dt = datetime.fromisoformat(last_mine)
        cooldown = get_mine_cooldown_seconds(user, is_admin)
        elapsed = (datetime.now() - last_dt).total_seconds()
        if elapsed < cooldown:
            remaining = cooldown - elapsed
            return False, f"⏰ Cooldown: tunggu *{remaining:.1f}* detik lagi!"
    except Exception:
        pass
    return True, ""


# ══════════════════════════════════════════════════════════════
# BUFF SYSTEM
# ══════════════════════════════════════════════════════════════
def get_active_buffs(user: dict) -> dict:
    buffs = user.get("active_buffs", {})
    now = datetime.now()
    clean = {}
    for k, v in buffs.items():
        exp = v.get("expires")
        if exp:
            try:
                if datetime.fromisoformat(exp) > now:
                    clean[k] = v
            except Exception:
                pass
        else:
            clean[k] = v
    return clean


def get_buff_val(buffs: dict, key: str, default=0):
    b = buffs.get(key, {})
    return b.get("value", default)


# ══════════════════════════════════════════════════════════════
# ORE ROLLER
# ══════════════════════════════════════════════════════════════
def roll_ore(user: dict, buffs: dict, zone_id: str) -> Tuple[str, dict]:
    zone = ZONES.get(zone_id, ZONES["surface"])
    ore_bonus = zone.get("ore_bonus", {})
    luck_buff = get_buff_val(buffs, "luck_buff", 0)
    tool = TOOLS.get(user["current_tool"], TOOLS["stone_pick"])
    luck_bonus = tool["luck_bonus"] + luck_buff

    ores = list(ORES.items())
    weights = []
    for oid, ore in ores:
        w = ore["rarity"]
        if oid in ore_bonus:
            w *= ore_bonus[oid]
        # Rare ore benefit more from luck
        if ore.get("tier") in ("legendary", "mythical", "cosmic", "divine"):
            w *= (1 + luck_bonus * 3)
        elif ore.get("tier") in ("epic",):
            w *= (1 + luck_bonus * 2)
        weights.append(max(w, 0.0001))

    total = sum(weights)
    weights = [w / total for w in weights]
    chosen = random.choices(ores, weights=weights, k=1)[0]
    return chosen[0], chosen[1]


# ══════════════════════════════════════════════════════════════
# KG CALCULATION
# ══════════════════════════════════════════════════════════════
def calculate_ore_kg(ore_id: str, user: dict, buffs: dict, tool_id: str, zone_id: str) -> float:
    """Hitung berat KG ore yang didapat, termasuk semua bonus."""
    ore = ORES.get(ore_id, {})
    base_kg = get_random_kg(ore_id)

    # Bonus dari alat
    tool = TOOLS.get(tool_id, TOOLS["stone_pick"])
    tool_kg_bonus = tool.get("kg_bonus", 1.0)

    # Bonus dari zona
    zone = ZONES.get(zone_id, ZONES["surface"])
    zone_kg_bonus = zone.get("kg_bonus", 1.0)

    # Bonus dari buff (kg_boost item)
    kg_buff = get_buff_val(buffs, "kg_boost", 1.0)
    if kg_buff <= 0:
        kg_buff = 1.0

    final_kg = base_kg * tool_kg_bonus * zone_kg_bonus * kg_buff

    # Kalau critical atau lucky, KG juga naik
    return round(final_kg, 2)


# ══════════════════════════════════════════════════════════════
# MINING ENGINE v4
# ══════════════════════════════════════════════════════════════
async def perform_mine(user_id: int, is_admin: bool = False) -> dict:
    """Execute one mine action. Returns hasil mining."""
    user = await get_user(user_id)
    if not user:
        return {"ok": False, "msg": "❌ User tidak ditemukan. Ketik /start"}

    user = await regen_energy(user)
    buffs = get_active_buffs(user)

    tool_id     = user["current_tool"]
    tool        = TOOLS.get(tool_id, TOOLS["stone_pick"])
    zone_id     = user.get("current_zone", "surface")
    zone        = ZONES.get(zone_id, ZONES["surface"])
    energy_cost = tool["energy_cost"]

    # Admin tidak perlu energy
    if not is_admin and user["energy"] < energy_cost:
        return {
            "ok": False,
            "msg": (
                f"⚡ *Energy tidak cukup!*\n\n"
                f"Energy kamu: `{user['energy']}/{user['max_energy']}`\n"
                f"Dibutuhkan : `{energy_cost}` energy\n"
                f"⏰ Energy penuh dalam: *{energy_full_in(user)}*\n\n"
                f"💡 Gunakan ⚡ *Energy Potion* dari inventaris!\n"
                f"💡 Atau beli tambahan energy: `/buyenergy`"
            )
        }

    # Cek kapasitas bag (slot)
    ore_inv = user.get("ore_inventory", {})
    total_ore_in_bag = sum(ore_inv.values())
    bag_slots = user.get("bag_slots", 50)
    if not is_admin and total_ore_in_bag >= bag_slots:
        return {
            "ok": False,
            "msg": (
                f"🎒 *Bag penuh! (slot)*\n\n"
                f"Kapasitas: `{total_ore_in_bag}/{bag_slots}` slot\n\n"
                f"💡 Jual ore di *🛒 Market* atau gunakan `/bag`\n"
                f"💡 Tambah slot: `/buyslot`"
            )
        }

    # Cek kapasitas bag (KG)
    current_kg = user.get("bag_kg_used", 0.0)
    max_kg = user.get("bag_kg_max", 100.0)
    # Estimasi kg ore terberat yang mungkin didapat, jika hampir penuh, tolak
    if not is_admin and current_kg >= max_kg * 0.98:
        return {
            "ok": False,
            "msg": (
                f"🎒 *Bag terlalu berat!*\n\n"
                f"Berat saat ini: `{format_kg(current_kg)}/{format_kg(max_kg)}`\n\n"
                f"💡 Jual ore di *🛒 Market* atau gunakan `/bag`\n"
                f"💡 Upgrade kapasitas KG: `/buykg`"
            )
        }

    # ── Roll ore ──────────────────────────────────────────────
    ore_id, ore = roll_ore(user, buffs, zone_id)

    # ── Calculate KG ore ──────────────────────────────────────
    ore_kg = calculate_ore_kg(ore_id, user, buffs, tool_id, zone_id)

    # ── XP Calculation (FOKUS XP, bukan koin) ─────────────────
    xp_mult  = get_buff_val(buffs, "xp_mult", 1.0) or 1.0
    perm_xp_mult = user.get("perm_xp_mult", 1.0) or 1.0  # permanent XP dari rebirth
    tool_xp_bonus = tool.get("xp_bonus", 1.0)
    zone_xp_bonus = zone.get("kg_bonus", 1.0)  # zona yang lebih dalam = XP lebih banyak

    # XP dasar dari ore, dikalikan semua bonus
    base_xp = ore["xp"]
    # Bonus XP berbasis KG: ore lebih berat = XP lebih banyak
    kg_xp_bonus = 1.0 + (ore_kg / ore.get("kg_max", 2.0)) * 0.5  # max +50% XP dari KG
    xp_gain = int(base_xp * XP_BASE_MULTIPLIER * xp_mult * perm_xp_mult * tool_xp_bonus * kg_xp_bonus)

    # Tool special XP
    if tool.get("special") and "XP" in tool.get("special", ""):
        xp_gain = int(xp_gain * 1.1)

    # ── Critical hit (XP bonus) ────────────────────────────────
    crit_chance = CRITICAL_CHANCE + tool["crit_bonus"]
    is_crit = random.random() < crit_chance
    if is_crit:
        xp_gain = int(xp_gain * 2)
        ore_kg = round(ore_kg * 1.5, 2)  # crit = ore lebih berat

    # ── Lucky bonus (XP & KG) ──────────────────────────────────
    luck_bonus_val = LUCKY_CHANCE + tool["luck_bonus"] + get_buff_val(buffs, "luck_buff", 0)
    is_lucky = random.random() < luck_bonus_val
    if is_lucky and not is_crit:
        xp_gain = int(xp_gain * 1.5)
        ore_kg = round(ore_kg * 1.2, 2)  # lucky = ore sedikit lebih berat

    # ── Special tool effects ──────────────────────────────────
    special_hit = None
    if tool_id == "electric_drill" and random.random() < 0.08:
        xp_gain *= 2
        special_hit = "⚡ Double XP!"
    elif tool_id == "sonic_drill" and random.random() < 0.05:
        xp_gain *= 3
        special_hit = "🔊 Sonic Boom! 3x XP!"
    elif tool_id == "plasma_drill" and random.random() < 0.12:
        xp_gain = int(xp_gain * 3)
        special_hit = "🌟 Plasma Burst! 3x XP!"
    elif tool_id == "quantum_miner" and random.random() < 0.15:
        # Get 2 ore at once (add extra ore to bag)
        xp_gain *= 2
        await add_ore_to_inventory(user_id, ore_id, 1, ore_kg)
        special_hit = "🌀 Quantum Shift! 2 ore sekaligus!"
    elif tool_id == "void_extractor" and random.random() < 0.20:
        xp_gain *= 2
        ore_kg = round(ore_kg * 2.0, 2)
        special_hit = "🕳️ Void Pull! KG 2x!"
    elif tool_id == "dark_matter_drill" and random.random() < 0.18:
        xp_gain *= 3
        special_hit = "🌌 Dark Energy! 3x XP!"
    elif tool_id == "antimatter_borer" and random.random() < 0.20:
        xp_gain *= 4
        special_hit = "💥 Annihilation! 4x XP!"
    elif tool_id == "celestial_hammer" and random.random() < 0.25:
        xp_gain *= 5
        ore_kg = round(ore_kg * 2.0, 2)
        special_hit = "☄️ Meteor Strike! 5x XP & KG 2x!"
    elif tool_id == "god_hammer" and random.random() < 0.30:
        xp_gain *= 10
        special_hit = "⚡ Divine Strike! 10x XP!"
    elif tool_id == "genesis_pick" and random.random() < 0.35:
        xp_gain *= 15
        ore_kg = round(ore_kg * 2.0, 2)
        special_hit = "🌅 Genesis Burst! 15x XP & KG 2x!"
    elif tool_id == "singularity_drill" and random.random() < 0.40:
        xp_gain *= 10
        ore_kg = round(ore_kg * 5.0, 2)
        special_hit = "🌀 Singularity! 10x XP & KG 5x!"
    elif tool_id == "nano_extractor" and random.random() < 0.15:
        xp_gain *= 4
        special_hit = "🧬 Nano Swarm! 4x XP!"
    elif tool_id == "photon_extractor" and random.random() < 0.10:
        special_hit = "💡 Light Speed! Energy gratis!"
    elif tool_id == "tachyon_drill" and random.random() < 0.12:
        xp_gain *= 4
        ore_kg = round(ore_kg * 1.5, 2)
        special_hit = "🌀 Tachyon! 4x XP & KG 1.5x!"
    elif tool_id == "psionic_drill" and random.random() < 0.12:
        xp_gain *= 4
        special_hit = "🧠 Psionic! 4x XP!"
    elif tool_id == "entropy_drill" and random.random() < 0.18:
        xp_gain *= 3
        ore_kg = round(ore_kg * 2.0, 2)
        special_hit = "🌪️ Entropy! 3x XP & KG 2x!"
    elif tool_id == "wormhole_drill" and random.random() < 0.20:
        xp_gain *= 4
        await add_ore_to_inventory(user_id, ore_id, 1, ore_kg)
        special_hit = "🌐 Wormhole! 4x XP + ore bonus!"
    elif tool_id == "star_forge" and random.random() < 0.25:
        xp_gain *= 6
        ore_kg = round(ore_kg * 2.0, 2)
        special_hit = "⭐ Star Forge! 6x XP & KG 2x!"
    elif tool_id == "eternal_pick" and random.random() < 0.30:
        xp_gain *= 8
        ore_kg = round(ore_kg * 3.0, 2)
        special_hit = "♾️ Eternal! 8x XP & KG 3x!"
    elif tool_id == "omega_drill" and random.random() < 0.38:
        xp_gain *= 10
        ore_kg = round(ore_kg * 2.5, 2)
        special_hit = "🔱 Omega! 10x XP & KG 2.5x!"
    elif tool_id == "cosmos_hammer" and random.random() < 0.45:
        xp_gain *= 15
        ore_kg = round(ore_kg * 5.0, 2)
        special_hit = "🌌 Cosmos! 15x XP & KG 5x!"
    elif tool_id == "neutron_drill" and random.random() < 0.10:
        xp_gain = int(xp_gain * 3.5)
        special_hit = "⚛️ Neutron Burst! 3.5x XP!"
    elif tool_id == "magma_drill" and random.random() < 0.08:
        xp_gain = int(xp_gain * 2.5)
        special_hit = "🌋 Magma Burst! 2.5x XP!"
    elif tool_id == "cobalt_drill" and random.random() < 0.10:
        ore_kg = round(ore_kg * 1.5, 2)
        special_hit = "🔵 Cobalt! KG 1.5x!"
    elif tool_id == "meteor_hammer" and random.random() < 0.12:
        xp_gain = int(xp_gain * 3)
        special_hit = "☄️ Meteor! 3x XP!"

    # ── Apply changes ─────────────────────────────────────────
    new_energy = user["energy"] - (0 if is_admin else energy_cost)
    new_xp     = user["xp"] + xp_gain
    new_level  = user["level"]
    leveled_up = False

    while new_level < MAX_LEVEL and new_xp >= xp_for_level(new_level):
        new_xp    -= xp_for_level(new_level)
        new_level += 1
        leveled_up = True

    # Update KG used
    new_kg_used = round(current_kg + ore_kg, 2)
    if new_kg_used > max_kg and not is_admin:
        new_kg_used = max_kg  # cap, tidak bisa lebih dari max

    updates = dict(
        energy=new_energy,
        xp=new_xp, level=new_level,
        last_energy_regen=datetime.now().isoformat(),
        last_mine_time=datetime.now().isoformat(),
        bag_kg_used=new_kg_used,
    )
    await update_user(user_id, **updates)

    # Tambah ore ke ore_inventory (dengan KG)
    await add_ore_to_inventory(user_id, ore_id, 1, ore_kg)

    # Hitung bag usage setelah tambah
    user_after = await get_user(user_id)
    bag_used = sum(user_after.get("ore_inventory", {}).values()) if user_after else 0

    await log_mine(user_id, tool_id, tool["name"], zone_id,
                   ore_id, ore["name"], 0, xp_gain,
                   is_crit, is_lucky, special_hit)

    # Update total KG mined (untuk achievement)
    await update_total_kg_mined(user_id, ore_kg)

    # ── Check achievements ────────────────────────────────────
    new_achievements = await check_achievements(user_id)

    # Harga jual ore ini (informasi)
    sell_price = calculate_sell_price(ore_id, ore_kg)

    return {
        "ok":           True,
        "tool":         tool,
        "tool_id":      tool_id,
        "zone":         zone,
        "ore_id":       ore_id,
        "ore":          ore,
        "ore_kg":       ore_kg,
        "sell_price":   sell_price,
        "xp_gain":      xp_gain,
        "is_crit":      is_crit,
        "is_lucky":     is_lucky,
        "special_hit":  special_hit,
        "new_energy":   new_energy,
        "max_energy":   user["max_energy"],
        "new_balance":  user_after["balance"] if user_after else user["balance"],
        "new_level":    new_level,
        "leveled_up":   leveled_up,
        "new_achievements": new_achievements,
        "bag_used":     bag_used,
        "bag_slots":    user.get("bag_slots", 50),
        "bag_kg_used":  new_kg_used,
        "bag_kg_max":   max_kg,
        "new_xp":       new_xp,
        "xp_needed":    xp_for_level(new_level),
    }


async def update_total_kg_mined(user_id: int, kg: float):
    """Update total kg mined untuk achievement tracking."""
    user = await get_user(user_id)
    if user:
        current_total = user.get("total_kg_mined", 0.0)
        await update_user(user_id, total_kg_mined=round(current_total + kg, 2))


def build_mine_result_text(r: dict) -> str:
    """Build formatted mining result message dengan sistem KG."""
    tool  = r["tool"]
    ore   = r["ore"]
    zone  = r["zone"]
    ore_kg = r.get("ore_kg", 0.0)
    sell_price = r.get("sell_price", 0)

    badges = []
    if r["is_crit"]:     badges.append("💥 CRITICAL!")
    if r["is_lucky"]:    badges.append("🍀 LUCKY!")
    if r["special_hit"]: badges.append(r["special_hit"])
    badge_line = "  ".join(badges)

    energy_bar = make_bar(r["new_energy"], r["max_energy"], 8)
    xp_bar = make_bar(r["new_xp"], r["xp_needed"], 8) if r.get("xp_needed", 0) > 0 else "░░░░░░░░"

    ore_desc = ore.get("desc", "Ore yang kamu temukan.")
    ore_tier = ore.get("tier", "common")
    from config import ORE_TIER_COLORS
    tier_color = ORE_TIER_COLORS.get(ore_tier, "⬜")

    # Estimasi berat kategori
    kg_desc = "ringan"
    if ore_kg >= 10.0: kg_desc = "sangat berat"
    elif ore_kg >= 5.0: kg_desc = "berat"
    elif ore_kg >= 2.0: kg_desc = "cukup berat"
    elif ore_kg >= 0.5: kg_desc = "ringan"
    else: kg_desc = "sangat ringan"

    lines = [
        f"⛏️ *HASIL MINING*",
        f"━━━━━━━━━━━━━━━━━━━━━━",
        f"",
        f"📍 Zona  : {zone['name']}",
        f"🔧 Alat  : {tool['emoji']} *{tool['name']}*",
        f"",
        f"🪨 *Bijih Ditemukan:*",
        f"   {tier_color} {ore['emoji']} *{ore['name']}*",
        f"   └ 💬 _{ore_desc}_",
        f"   └ ⚖️ Berat: `{format_kg(ore_kg)}` _{kg_desc}_",
        f"   └ 💰 Est. jual: `{sell_price:,}` koin",
        f"",
    ]

    if badge_line:
        lines.append(f"✨ *{badge_line}*")
        lines.append("")

    lines += [
        f"╔════════════════════╗",
        f"  ⭐  +*{r['xp_gain']:,}* XP",
        f"  📦  +1 {ore['emoji']} {ore['name']} ({format_kg(ore_kg)})",
        f"  💰  Est. jual: `{sell_price:,}` koin",
        f"╚════════════════════╝",
        f"",
        f"⚡ Energy : {energy_bar} `{r['new_energy']}/{r['max_energy']}`",
        f"⭐ XP     : {xp_bar} `{r['new_xp']:,}/{r['xp_needed']:,}`",
        f"🎒 Bag    : `{r.get('bag_used',0)}/{r.get('bag_slots',50)}` slot | `{format_kg(r.get('bag_kg_used',0))}/{format_kg(r.get('bag_kg_max',100))}` kg",
    ]

    if r["leveled_up"]:
        lines.append(f"")
        lines.append(f"🎉 *LEVEL UP! ➜ Level {r['new_level']}!*")

    if r["new_achievements"]:
        lines.append(f"")
        for ach in r["new_achievements"]:
            lines.append(f"🏅 *Prestasi baru: {ach['name']}* (+{ach['reward']:,}🪙)")

    lines.append(f"")
    lines.append(f"💡 Jual ore di 🎒 *Bag* atau 🛒 *Market*!")

    return "\n".join(lines)


def make_bar(current: int, maximum: int, length: int = 10) -> str:
    if maximum <= 0:
        return "█" * length
    pct = min(current / maximum, 1.0)
    filled = round(pct * length)
    return "█" * filled + "░" * (length - filled)


# ══════════════════════════════════════════════════════════════
# ACHIEVEMENTS v4
# ══════════════════════════════════════════════════════════════
async def check_achievements(user_id: int) -> list:
    user = await get_user(user_id)
    if not user:
        return []
    achieved = user["achievements"]
    new_ones = []

    async def grant(ach_id: str):
        if ach_id in ACHIEVEMENTS and ach_id not in achieved:
            ach = ACHIEVEMENTS[ach_id]
            achieved.append(ach_id)
            await add_balance(user_id, ach["reward"], f"Achievement: {ach['name']}")
            new_ones.append(ach)

    mc  = user["mine_count"]
    bal = user["total_earned"]
    lv  = user["level"]
    total_kg = user.get("total_kg_mined", 0.0)

    if mc >= 1:       await grant("first_mine")
    if mc >= 10:      await grant("mine_10")
    if mc >= 100:     await grant("mine_100")
    if mc >= 1000:    await grant("mine_1000")
    if mc >= 10000:   await grant("mine_10000")
    if mc >= 100000:  await grant("mine_100000")
    if bal >= 100000:        await grant("rich_100k")
    if bal >= 1000000:       await grant("rich_1m")
    if bal >= 1000000000:    await grant("rich_1b")
    if bal >= 1000000000000: await grant("rich_1t")
    if lv >= 10:   await grant("lvl_10")
    if lv >= 50:   await grant("lvl_50")
    if lv >= 100:  await grant("lvl_100")
    if lv >= 200:  await grant("lvl_200")
    if lv >= 500:  await grant("lvl_500")

    # KG achievements (tons: 1 ton = 1000 kg)
    if total_kg >= 1000:       await grant("heavy_miner")
    if total_kg >= 10000:      await grant("super_heavy")
    if total_kg >= 100000:     await grant("kg_master")
    if total_kg >= 1000000:    await grant("ton_miner")     # 1000 ton
    if total_kg >= 30000000:   await grant("mega_ton")      # 30000 ton

    # Ore achievements
    ore_inv = user.get("ore_inventory", {})
    if ore_inv.get("void_shard", 0) > 0:
        await grant("void_shard")
    if ore_inv.get("cosmic_dust", 0) > 0:
        await grant("cosmic_find")
    if ore_inv.get("eternity_stone", 0) > 0:
        await grant("divine_find")

    # Mythical / Cosmic / Divine first find
    mythical_ores = {"dragonstone","stardust","phoenix_ash","lunar_crystal","void_shard","dragon_heart","leviathan_scale","thunder_stone","glacial_shard","cursed_gem"}
    cosmic_ores = {"cosmic_dust","nebula_ore","time_crystal","dark_energy_ore","pulsar_fragment","quasar_crystal","antimatter_shard","neutron_core","singularity_ore","gamma_crystal"}
    divine_ores = {"soul_fragment","eternity_stone","universe_core","god_tear","creation_spark","omega_shard","infinity_gem"}
    if any(ore_inv.get(o, 0) > 0 for o in mythical_ores):
        await grant("first_mythical")
    if any(ore_inv.get(o, 0) > 0 for o in cosmic_ores):
        await grant("first_cosmic")
    if any(ore_inv.get(o, 0) > 0 for o in divine_ores):
        await grant("first_divine")
    if ore_inv.get("neutron_core", 0) > 0:
        await grant("neutron_miner")
    if ore_inv.get("infinity_gem", 0) > 0:
        await grant("infinity_hunter")

    # Legendary first find
    legendary_ores = {"diamond","amethyst","opal","mythril","alexandrite","painite","benitoite","jadeite","larimar","musgravite"}
    if any(ore_inv.get(o, 0) > 0 for o in legendary_ores):
        await grant("legendary_find")

    # Collector achievements
    unique_ores = sum(1 for v in ore_inv.values() if v > 0)
    if unique_ores >= 10:  await grant("collector_10")
    if unique_ores >= 25:  await grant("collector_25")

    # Tool master
    owned_tools = user.get("owned_tools", [])
    if len(owned_tools) >= 10:
        await grant("tool_master")

    # All zones
    all_zone_ids = set(["surface","cave","mine_shaft","underground","volcanic_field","lava_cave","deep_mine","crystal_cavern","gem_paradise","ancient_ruins","dragon_lair","void_realm","sky_island","frozen_core","deep_space","pulsar_belt","time_rift","antimatter_zone","soul_realm","genesis_realm"])
    unlocked_zones = set(user.get("unlocked_zones", []))
    if all_zone_ids.issubset(unlocked_zones):
        await grant("all_zones")

    if new_ones:
        await update_user(user_id, achievements=achieved)
    return new_ones


# ══════════════════════════════════════════════════════════════
# SHOP: BUY TOOL
# ══════════════════════════════════════════════════════════════
async def buy_tool(user_id: int, tool_id: str,
                   admin: bool = False) -> Tuple[bool, str]:
    user = await get_user(user_id)
    if not user:
        return False, "❌ User tidak ditemukan."
    tool = TOOLS.get(tool_id)
    if not tool:
        return False, "❌ Alat tidak ditemukan."
    if tool_id in user["owned_tools"]:
        return False, f"❌ Kamu sudah punya *{tool['name']}*!"
    if not admin and user["level"] < tool["level_req"]:
        return False, f"❌ Butuh Level *{tool['level_req']}*! (Kamu Level {user['level']})"
    if not admin and user["balance"] < tool["price"]:
        return False, (f"❌ Koin tidak cukup!\nButuh: `{tool['price']:,}`\nPunya: `{user['balance']:,}`")

    ore_req = tool.get("ore_req", {})
    if not admin and ore_req:
        ore_inv = user.get("ore_inventory", {})
        missing = []
        for oid, qty_needed in ore_req.items():
            have = ore_inv.get(oid, 0)
            if have < qty_needed:
                ore = ORES.get(oid, {})
                missing.append(f"{ore.get('emoji','')} {ore.get('name', oid)}: {have}/{qty_needed}")
        if missing:
            return False, (
                f"❌ *Ore tidak cukup!*\n\nAlat ini butuh ore:\n" +
                "\n".join(f"  • {m}" for m in missing)
            )
        for oid, qty_needed in ore_req.items():
            await remove_ore_from_inventory(user_id, oid, qty_needed)
        user = await get_user(user_id)

    new_owned = user["owned_tools"] + [tool_id]
    updates = dict(owned_tools=new_owned, current_tool=tool_id)
    if not admin:
        updates["balance"] = user["balance"] - tool["price"]
    await update_user(user_id, **updates)

    ore_txt = ""
    if ore_req and not admin:
        ore_txt = "\n📦 Ore yang digunakan:\n" + "\n".join(
            f"  • {ORES.get(k,{}).get('emoji','')} {ORES.get(k,{}).get('name',k)}: -{v}"
            for k, v in ore_req.items()
        )

    return True, (
        f"✅ *{tool['name']}* berhasil dibeli!\n"
        f"⚒️ Alat otomatis dipasang.\n"
        f"💰 Sisa saldo: `{updates.get('balance', user['balance']):,}` koin"
        f"{ore_txt}"
    )


async def equip_tool(user_id: int, tool_id: str) -> Tuple[bool, str]:
    user = await get_user(user_id)
    if not user:
        return False, "❌ User tidak ditemukan."
    if tool_id not in user["owned_tools"]:
        return False, "❌ Kamu tidak punya alat ini."
    tool = TOOLS[tool_id]
    await update_user(user_id, current_tool=tool_id)
    return True, f"✅ *{tool['name']}* dipasang!"


# ══════════════════════════════════════════════════════════════
# SHOP: BUY ITEM
# ══════════════════════════════════════════════════════════════
async def buy_item(user_id: int, item_id: str,
                   admin: bool = False) -> Tuple[bool, str]:
    user = await get_user(user_id)
    if not user:
        return False, "❌ User tidak ditemukan."
    item = ITEMS.get(item_id)
    if not item:
        return False, "❌ Item tidak ditemukan."
    if not admin and user["balance"] < item["price"]:
        return False, f"❌ Koin tidak cukup! Butuh `{item['price']:,}` koin.\nPunya: `{user['balance']:,}` koin."

    inv = dict(user["inventory"])
    inv[item_id] = inv.get(item_id, 0) + 1
    updates = {"inventory": inv}
    if not admin:
        updates["balance"] = user["balance"] - item["price"]
    await update_user(user_id, **updates)

    sisa = updates.get("balance", user["balance"])
    return True, (
        f"✅ *{item['name']}* berhasil dibeli!\n"
        f"💰 Sisa saldo: `{sisa:,}` koin\n"
        f"📦 Cek /inventory untuk menggunakannya."
    )


async def use_item(user_id: int, item_id: str) -> Tuple[bool, str]:
    user = await get_user(user_id)
    if not user:
        return False, "❌ User tidak ditemukan."
    item = ITEMS.get(item_id)
    if not item:
        return False, "❌ Item tidak ditemukan."
    inv = dict(user["inventory"])
    if inv.get(item_id, 0) <= 0:
        return False, "❌ Item ini tidak ada di inventarismu."

    inv[item_id] -= 1
    if inv[item_id] <= 0:
        del inv[item_id]

    updates = {"inventory": inv}
    effect = item["effect"]
    msg_lines = [f"✅ *{item['name']}* digunakan!"]

    if "energy" in effect:
        new_e = min(user["energy"] + effect["energy"], user["max_energy"])
        updates["energy"] = new_e
        msg_lines.append(f"⚡ Energy: `{user['energy']} → {new_e}/{user['max_energy']}`")

    elif "mystery" in effect:
        reward = _mystery_box_reward(premium=False)
        msg_lines.extend(await _apply_mystery_reward(user_id, user, reward))

    elif "mystery_premium" in effect:
        reward = _mystery_box_reward(premium=True)
        msg_lines.extend(await _apply_mystery_reward(user_id, user, reward))

    elif "bag_expand" in effect:
        cur_slots = user.get("bag_slots", 50)
        cur_kg = user.get("bag_kg_max", 100.0)
        from config import BAG_SLOT_MAX, BAG_KG_MAX
        new_slots = min(cur_slots + 5, BAG_SLOT_MAX)
        new_kg = min(cur_kg + 10.0, BAG_KG_MAX)
        updates["bag_slots"] = new_slots
        updates["bag_kg_max"] = new_kg
        msg_lines.append(f"🎒 Slot bag: `{cur_slots} → {new_slots}`")
        msg_lines.append(f"⚖️ Kapasitas KG: `{format_kg(cur_kg)} → {format_kg(new_kg)}`")

    elif "mega_bag_expand" in effect:
        cur_slots = user.get("bag_slots", 50)
        cur_kg = user.get("bag_kg_max", 100.0)
        from config import BAG_SLOT_MAX, BAG_KG_MAX
        new_slots = min(cur_slots + 15, BAG_SLOT_MAX)
        new_kg = min(cur_kg + 50.0, BAG_KG_MAX)
        updates["bag_slots"] = new_slots
        updates["bag_kg_max"] = new_kg
        msg_lines.append(f"🎒 Slot bag: `{cur_slots} → {new_slots}` (+15)")
        msg_lines.append(f"⚖️ Kapasitas KG: `{format_kg(cur_kg)} → {format_kg(new_kg)}` (+50kg)")

    elif "mystery_divine" in effect:
        reward = _mystery_box_reward(premium=True, divine=True)
        msg_lines.extend(await _apply_mystery_reward(user_id, user, reward))

    elif any(k in effect for k in ("kg_boost","luck_buff","xp_mult","speed_boost","coin_mult")):
        buffs = get_active_buffs(user)
        now = datetime.now()
        dur = effect.get("duration", 20)
        exp = (now + timedelta(minutes=dur)).isoformat()
        if "kg_boost" in effect:
            buffs["kg_boost"] = {"value": effect["kg_boost"], "expires": exp}
            msg_lines.append(f"⚖️ Ore {effect['kg_boost']}x lebih berat selama {dur} menit!")
        if "luck_buff" in effect:
            buffs["luck_buff"] = {"value": effect["luck_buff"], "expires": exp}
            msg_lines.append(f"🍀 Luck +{int(effect['luck_buff']*100)}% selama {dur} menit!")
        if "xp_mult" in effect:
            buffs["xp_mult"] = {"value": effect["xp_mult"], "expires": exp}
            msg_lines.append(f"⭐ {effect['xp_mult']}x XP selama {dur} menit!")
        if "speed_boost" in effect:
            buffs["speed_boost"] = {"value": effect["speed_boost"], "expires": exp}
            msg_lines.append(f"🚀 Cooldown mining -{int((1-effect['speed_boost'])*100)}% selama {dur} menit!")
        if "coin_mult" in effect:
            buffs["coin_mult"] = {"value": effect["coin_mult"], "expires": exp}
            msg_lines.append(f"💰 Harga jual ore {effect['coin_mult']}x selama {dur} menit!")
        updates["active_buffs"] = buffs

    elif "rebirth" in effect:
        if user["level"] < MAX_LEVEL:
            return False, f"❌ Rebirth butuh Level *{MAX_LEVEL}*! Kamu Level {user['level']}."
        perm_xp = user.get("perm_xp_mult", 1.0) + 0.50
        rb_count = user.get("rebirth_count", 0) + 1
        updates.update({
            "level": 1, "xp": 0, "rebirth_count": rb_count,
            "perm_xp_mult": perm_xp,
            "owned_tools": ["stone_pick"], "current_tool": "stone_pick",
        })
        msg_lines.append(f"🔄 *REBIRTH #{rb_count}!* Level direset. Permanent XP: `{perm_xp:.1f}x`")

    await update_user(user_id, **updates)
    return True, "\n".join(msg_lines)


async def _apply_mystery_reward(user_id: int, user: dict, reward: dict) -> list:
    lines = []
    if reward["type"] == "xp":
        new_xp = user["xp"] + reward["amount"]
        new_level = user["level"]
        while new_level < MAX_LEVEL and new_xp >= xp_for_level(new_level):
            new_xp -= xp_for_level(new_level)
            new_level += 1
        await update_user(user_id, xp=new_xp, level=new_level)
        lines.append(f"📦 Mystery Box berisi: ⭐ *+{reward['amount']:,} XP!*")
    elif reward["type"] == "coins":
        await add_balance(user_id, reward["amount"], "Mystery Box")
        lines.append(f"📦 Mystery Box berisi: 💰 *+{reward['amount']:,} koin!*")
    elif reward["type"] == "item":
        inv2 = dict(user["inventory"])
        inv2[reward["item_id"]] = inv2.get(reward["item_id"], 0) + 1
        await update_user(user_id, inventory=inv2)
        lines.append(f"📦 Mystery Box berisi: 🎁 *{ITEMS.get(reward['item_id'],{}).get('name','Item')}!*")
    elif reward["type"] == "ore":
        ore_id = reward["ore_id"]
        ore_kg = get_random_kg(ore_id)
        await add_ore_to_inventory(user_id, ore_id, 1, ore_kg)
        ore = ORES.get(ore_id, {})
        lines.append(f"📦 Mystery Box berisi: {ore.get('emoji','')} *{ore.get('name',ore_id)} ({format_kg(ore_kg)})!*")
    return lines


def _mystery_box_reward(premium: bool = False, divine: bool = False) -> dict:
    if divine:
        roll = random.random()
        mythical_ores = ["dragonstone","stardust","phoenix_ash","lunar_crystal","void_shard","dragon_heart","leviathan_scale","thunder_stone","glacial_shard","cursed_gem"]
        cosmic_ores = ["cosmic_dust","nebula_ore","time_crystal","dark_energy_ore","pulsar_fragment","quasar_crystal","antimatter_shard","neutron_core","singularity_ore","gamma_crystal"]
        divine_ores = ["soul_fragment","eternity_stone","universe_core","god_tear","creation_spark","omega_shard","infinity_gem"]
        if roll < 0.50:
            return {"type": "ore", "ore_id": random.choice(mythical_ores)}
        elif roll < 0.80:
            return {"type": "ore", "ore_id": random.choice(cosmic_ores)}
        elif roll < 0.95:
            return {"type": "ore", "ore_id": random.choice(divine_ores)}
        else:
            amount = random.randint(100000, 1000000)
            return {"type": "xp", "amount": amount}
    if premium:
        roll = random.random()
        if roll < 0.40:
            items_list = ["xp_boost", "xp_mega_boost", "luck_elixir", "mega_luck_potion", "weight_enhancer"]
            return {"type": "item", "item_id": random.choice(items_list)}
        elif roll < 0.70:
            amount = random.randint(10000, 100000)
            return {"type": "xp", "amount": amount}
        elif roll < 0.90:
            amount = random.randint(5000, 50000)
            return {"type": "coins", "amount": amount}
        else:
            # Rare ore dari premium box
            rare_ores = ["diamond", "amethyst", "opal", "mythril"]
            return {"type": "ore", "ore_id": random.choice(rare_ores)}
    else:
        roll = random.random()
        if roll < 0.55:
            amount = random.randint(1000, 15000)
            return {"type": "xp", "amount": amount}
        elif roll < 0.80:
            amount = random.randint(500, 5000)
            return {"type": "coins", "amount": amount}
        elif roll < 0.95:
            items_list = ["energy_drink", "energy_potion", "luck_elixir", "xp_boost", "speed_boost"]
            return {"type": "item", "item_id": random.choice(items_list)}
        else:
            rare_ores = ["sapphire", "emerald", "ruby", "topaz"]
            return {"type": "ore", "ore_id": random.choice(rare_ores)}


# ══════════════════════════════════════════════════════════════
# ZONE UNLOCK
# ══════════════════════════════════════════════════════════════
async def unlock_zone(user_id: int, zone_id: str,
                      admin: bool = False) -> Tuple[bool, str]:
    user = await get_user(user_id)
    if not user:
        return False, "❌ User tidak ditemukan."
    zone = ZONES.get(zone_id)
    if not zone:
        return False, "❌ Zona tidak ditemukan."
    if zone_id in user["unlocked_zones"]:
        return False, "❌ Zona sudah dibuka!"
    if not admin and user["level"] < zone["level_req"]:
        return False, f"❌ Butuh Level *{zone['level_req']}*!"
    if not admin and user["balance"] < zone["unlock_cost"]:
        return False, f"❌ Koin tidak cukup! Butuh `{zone['unlock_cost']:,}`"
    new_zones = user["unlocked_zones"] + [zone_id]
    updates = {"unlocked_zones": new_zones, "current_zone": zone_id}
    if not admin:
        updates["balance"] = user["balance"] - zone["unlock_cost"]
    await update_user(user_id, **updates)
    return True, f"✅ *{zone['name']}* terbuka! Zona aktif diganti."


async def set_zone(user_id: int, zone_id: str) -> Tuple[bool, str]:
    user = await get_user(user_id)
    if not user:
        return False, "❌ User tidak ditemukan."
    if zone_id not in user["unlocked_zones"]:
        return False, "❌ Zona belum dibuka."
    zone = ZONES[zone_id]
    await update_user(user_id, current_zone=zone_id)
    return True, f"✅ Zona aktif: *{zone['name']}*"


# ══════════════════════════════════════════════════════════════
# DAILY BONUS
# ══════════════════════════════════════════════════════════════
async def claim_daily(user_id: int) -> Tuple[bool, str]:
    from config import DAILY_BONUS_BASE, DAILY_BONUS_LEVEL
    user = await get_user(user_id)
    if not user:
        return False, "❌ User tidak ditemukan."
    now = datetime.now()
    last = user.get("last_daily")
    streak = user.get("daily_streak", 0)

    if last:
        try:
            last_dt = datetime.fromisoformat(last)
            diff = now - last_dt
            if diff.total_seconds() < 86400:
                rem = timedelta(seconds=86400) - diff
                h, s = divmod(int(rem.total_seconds()), 3600)
                m = s // 60
                return False, (
                    f"⏰ *Daily bonus belum bisa diklaim!*\n\n"
                    f"Tunggu lagi: *{h}j {m}m*\n"
                    f"🔥 Streak sekarang: `{streak}` hari"
                )
            if diff.total_seconds() < 172800:
                streak += 1
            else:
                streak = 1
        except Exception:
            streak = 1
    else:
        streak = 1

    bonus = DAILY_BONUS_BASE + (user["level"] * DAILY_BONUS_LEVEL)
    streak_mult = 1.0 + (min(streak, 30) * 0.05)
    bonus = int(bonus * streak_mult)

    # Daily juga kasih XP bonus
    xp_bonus = int(xp_for_level(user["level"]) * 0.1 * streak_mult)

    await add_balance(user_id, bonus, "Daily Bonus")
    new_xp = user["xp"] + xp_bonus
    new_level = user["level"]
    while new_level < MAX_LEVEL and new_xp >= xp_for_level(new_level):
        new_xp -= xp_for_level(new_level)
        new_level += 1

    await update_user(user_id,
                      energy=user["max_energy"],
                      daily_streak=streak,
                      last_daily=now.isoformat(),
                      xp=new_xp, level=new_level)

    new_ach = []
    if streak >= 7:
        ach = await _grant_if_new(user_id, "daily_streak_7")
        if ach: new_ach.append(ach)
    if streak >= 30:
        ach = await _grant_if_new(user_id, "daily_streak_30")
        if ach: new_ach.append(ach)
    if streak >= 100:
        ach = await _grant_if_new(user_id, "daily_streak_100")
        if ach: new_ach.append(ach)

    lines = [
        f"🎁 *Daily Bonus Diklaim!*",
        f"",
        f"💰 +*{bonus:,}* koin",
        f"⭐ +*{xp_bonus:,}* XP",
        f"⚡ Energy diisi *PENUH!*",
        f"🔥 Streak: *{streak} hari* (`{streak_mult:.1f}x` multiplier)",
    ]
    if new_ach:
        for a in new_ach:
            lines.append(f"🏅 Prestasi: *{a['name']}* (+{a['reward']:,}🪙)")
    return True, "\n".join(lines)


async def _grant_if_new(user_id: int, ach_id: str):
    from config import ACHIEVEMENTS
    user = await get_user(user_id)
    if user and ach_id not in user["achievements"]:
        ach = ACHIEVEMENTS[ach_id]
        user["achievements"].append(ach_id)
        await add_balance(user_id, ach["reward"], f"Achievement: {ach['name']}")
        await update_user(user_id, achievements=user["achievements"])
        return ach
    return None


# ══════════════════════════════════════════════════════════════
# BUY ENERGY UPGRADE
# ══════════════════════════════════════════════════════════════
async def buy_energy_upgrade(user_id: int, admin: bool = False) -> Tuple[bool, str]:
    from config import ENERGY_UPGRADE_MAX, ENERGY_UPGRADE_STEP, ENERGY_UPGRADE_BASE_COST
    user = await get_user(user_id)
    if not user:
        return False, "❌ User tidak ditemukan."

    cur_max = user.get("max_energy", 500)
    if cur_max >= ENERGY_UPGRADE_MAX:
        return False, f"❌ *Max Energy sudah di batas maksimal!*\nMaksimal: `{ENERGY_UPGRADE_MAX}` energy"

    steps_done = (cur_max - 500) // ENERGY_UPGRADE_STEP
    price = ENERGY_UPGRADE_BASE_COST + (steps_done * 5000)

    if not admin and user["balance"] < price:
        return False, f"❌ Koin tidak cukup!\nButuh  : `{price:,}` koin\nPunya  : `{user['balance']:,}` koin"

    new_max = min(cur_max + ENERGY_UPGRADE_STEP, ENERGY_UPGRADE_MAX)
    updates = {"max_energy": new_max}
    if not admin:
        updates["balance"] = user["balance"] - price
    await update_user(user_id, **updates)

    return True, (
        f"✅ *Max Energy Ditingkatkan!*\n\n"
        f"⚡ Max Energy : `{cur_max}` → `{new_max}`\n"
        f"💰 Biaya      : `{price:,}` koin\n"
        f"💰 Sisa saldo : `{updates.get('balance', user['balance']):,}` koin\n\n"
        f"Upgrade berikutnya: `{ENERGY_UPGRADE_BASE_COST + (steps_done+1)*5000:,}` koin\n"
        f"_(Max: {ENERGY_UPGRADE_MAX} energy)_"
    )


# ══════════════════════════════════════════════════════════════
# BUY BAG SLOT
# ══════════════════════════════════════════════════════════════
async def buy_bag_slot(user_id: int, admin: bool = False) -> Tuple[bool, str]:
    from config import BAG_SLOT_MAX, BAG_SLOT_STEP, BAG_SLOT_BASE_COST
    user = await get_user(user_id)
    if not user:
        return False, "❌ User tidak ditemukan."

    cur_slots = user.get("bag_slots", 50)
    if cur_slots >= BAG_SLOT_MAX:
        return False, f"❌ *Slot Bag sudah di batas maksimal!*\nMaksimal: `{BAG_SLOT_MAX}` slot"

    steps_done = (cur_slots - 50) // BAG_SLOT_STEP
    price = BAG_SLOT_BASE_COST + (steps_done * 2000)

    if not admin and user["balance"] < price:
        return False, f"❌ Koin tidak cukup!\nButuh  : `{price:,}` koin\nPunya  : `{user['balance']:,}` koin"

    new_slots = min(cur_slots + BAG_SLOT_STEP, BAG_SLOT_MAX)
    updates = {"bag_slots": new_slots}
    if not admin:
        updates["balance"] = user["balance"] - price
    await update_user(user_id, **updates)

    return True, (
        f"✅ *Slot Bag Ditambah!*\n\n"
        f"🎒 Slot Bag : `{cur_slots}` → `{new_slots}` slot\n"
        f"💰 Biaya    : `{price:,}` koin\n"
        f"💰 Saldo    : `{updates.get('balance', user['balance']):,}` koin\n\n"
        f"Upgrade berikutnya: `{BAG_SLOT_BASE_COST + (steps_done+1)*2000:,}` koin\n"
        f"_(Max: {BAG_SLOT_MAX} slot)_"
    )


# ══════════════════════════════════════════════════════════════
# BUY BAG KG UPGRADE (BARU)
# ══════════════════════════════════════════════════════════════
async def buy_bag_kg(user_id: int, admin: bool = False) -> Tuple[bool, str]:
    from config import BAG_KG_MAX, BAG_KG_UPGRADE_STEP, BAG_KG_UPGRADE_COST
    user = await get_user(user_id)
    if not user:
        return False, "❌ User tidak ditemukan."

    cur_kg = user.get("bag_kg_max", 100.0)
    if cur_kg >= BAG_KG_MAX:
        return False, f"❌ *Kapasitas KG sudah maksimal!*\nMaksimal: `{format_kg(BAG_KG_MAX)}`"

    steps_done = int((cur_kg - 100.0) // BAG_KG_UPGRADE_STEP)
    price = BAG_KG_UPGRADE_COST + (steps_done * 1000)

    if not admin and user["balance"] < price:
        return False, f"❌ Koin tidak cukup!\nButuh  : `{price:,}` koin\nPunya  : `{user['balance']:,}` koin"

    new_kg = min(cur_kg + BAG_KG_UPGRADE_STEP, BAG_KG_MAX)
    updates = {"bag_kg_max": new_kg}
    if not admin:
        updates["balance"] = user["balance"] - price
    await update_user(user_id, **updates)

    return True, (
        f"✅ *Kapasitas KG Ditingkatkan!*\n\n"
        f"⚖️ Kapasitas KG : `{format_kg(cur_kg)}` → `{format_kg(new_kg)}`\n"
        f"💰 Biaya        : `{price:,}` koin\n"
        f"💰 Saldo        : `{updates.get('balance', user['balance']):,}` koin\n\n"
        f"Upgrade berikutnya: `{BAG_KG_UPGRADE_COST + (steps_done+1)*1000:,}` koin\n"
        f"_(Max: {format_kg(BAG_KG_MAX)})_"
    )
