from aiogram import Router, F
from aiogram.types import Message, PhotoSize
from aiogram.filters import Command

from config import ADMIN_IDS, TOOLS, ITEMS, ZONES, ORES, MAX_LEVEL
from database import (get_user, update_user, get_all_users, get_total_users,
                       add_balance, save_admin_photo, get_admin_photos,
                       delete_admin_photo, set_ore_photo, get_ore_photo,
                       get_all_ore_photos, delete_ore_photo,
                       set_tool_photo, get_tool_photo, get_all_tool_photos, delete_tool_photo,
                       set_zone_photo, get_zone_photo, get_all_zone_photos, delete_zone_photo,
                       add_ore_to_inventory)
from keyboards import admin_kb, back_main_kb

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


@router.message(Command("adminhelp"))
async def cmd_adminhelp(message: Message):
    if not is_admin(message.from_user.id):
        return

    lines = [
        "<b>🔐 PANEL ADMIN — Mining Bot v6</b>",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "",
        "<b>👑 Keistimewaan Admin:</b>",
        "• ⚡ Energy tidak pernah berkurang",
        "• 💰 Beli semua alat & item tanpa biaya",
        "• 🌍 Buka zona tanpa biaya & level req",
        "• ⏱ Speed mining: 1 detik (tercepat)",
        "• 🪨 Beli alat Legendary tanpa ore",
        "• 🔑 Akses semua perintah admin",
        "",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "<b>📋 DAFTAR PERINTAH ADMIN:</b>",
        "",
        "<b>👤 Manajemen User:</b>",
        "/admin_info [user_id] — Lihat info user",
        "/admin_addcoin [user_id] [jumlah] — Tambah koin",
        "/admin_setlevel [user_id] [level] — Set level",
        "/admin_setenergy [user_id] [jumlah] — Set energy",
        "/admin_givetool [user_id] [tool_id] — Beri alat",
        "/admin_giveitem [user_id] [item_id] [qty] — Beri item",
        "/admin_giveore [user_id] [ore_id] [qty] — Beri ore",
        "/admin_givezone [user_id] [zone_id] — Buka zona",
        "/admin_reset [user_id] — Reset data user",
        "",
        "<b>👑 VIP Management:</b>",
        "/admin_givevip [user_id] [plan_id] — Beri VIP",
        "/admin_revokevip [user_id] — Cabut VIP",
        "<i>Plan ID: 1_month, 3_months, 6_months, lifetime</i>",
        "",
        "<b>📸 Foto Admin, Ore, Alat & Zona:</b>",
        "/admin_setphoto — Upload foto profil admin",
        "/admin_myphotos — Lihat foto profil admin",
        "/admin_deletephoto [id] — Hapus foto profil",
        "/admin_setorephoto [ore_id] — Pasang foto ORE",
        "/admin_listorephoto — Lihat semua ore berphoto",
        "/admin_delorephoto [ore_id] — Hapus foto ore",
        "/admin_settoolphoto [tool_id] — Pasang foto ALAT MINING",
        "/admin_listtoolphoto — Lihat semua alat berphoto",
        "/admin_deltoolphoto [tool_id] — Hapus foto alat",
        "/admin_setzonephoto [zone_id] — Pasang foto ZONA",
        "/admin_listzonephoto — Lihat semua zona berphoto",
        "/admin_delzonephoto [zone_id] — Hapus foto zona",
        "",
        "<b>📊 Statistik & Broadcast:</b>",
        "/admin_stats — Statistik bot keseluruhan",
        "/admin_users — Daftar semua user",
        "/admin_broadcast [pesan] — Broadcast ke semua user",
        "",
        "<b>🎲 Game Control:</b>",
        "/admin_tools — Daftar semua tool_id",
        "/admin_items — Daftar semua item_id",
        "/admin_zones — Daftar semua zone_id",
        "/admin_ores — Daftar semua ore_id",
        "",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "<b>💡 Tips:</b>",
        "• Gunakan Shop normal untuk beli tanpa bayar",
        "• /buyslot dan /buyenergy gratis untuk admin",
        "• Admin otomatis terdeteksi dari ADMIN_IDS di .env",
    ]
    text = "\n".join(lines)
    await message.answer(text, parse_mode="HTML")


@router.message(Command("admin_setphoto"))
async def cmd_setphoto(message: Message):
    if not is_admin(message.from_user.id):
        return
    if message.reply_to_message and message.reply_to_message.photo:
        photo = message.reply_to_message.photo[-1]
        caption = message.text.replace("/admin_setphoto", "").strip() or ""
        await save_admin_photo(message.from_user.id, photo.file_id, caption)
        await message.answer(f"✅ *Foto berhasil disimpan!*\n📸 `{photo.file_id}`", parse_mode="Markdown")
    elif message.photo:
        photo = message.photo[-1]
        caption = message.caption or ""
        await save_admin_photo(message.from_user.id, photo.file_id, caption)
        await message.answer(f"✅ *Foto berhasil disimpan!*", parse_mode="Markdown")
    else:
        await message.answer(
            "📸 Reply foto dengan `/admin_setphoto [caption]`\natau kirim foto dengan caption `/admin_setphoto`.",
            parse_mode="Markdown"
        )


@router.message(F.photo & F.caption.startswith("/admin_setphoto"))
async def cmd_setphoto_direct(message: Message):
    if not is_admin(message.from_user.id):
        return
    photo = message.photo[-1]
    caption = (message.caption or "").replace("/admin_setphoto", "").strip()
    await save_admin_photo(message.from_user.id, photo.file_id, caption)
    await message.answer(f"✅ *Foto berhasil disimpan!*", parse_mode="Markdown")


@router.message(Command("admin_myphotos"))
async def cmd_myphotos(message: Message):
    if not is_admin(message.from_user.id):
        return
    photos = await get_admin_photos(message.from_user.id)
    if not photos:
        await message.answer("📸 Belum ada foto.", parse_mode="Markdown")
        return
    await message.answer(f"📸 *Foto Admin ({len(photos)}):*", parse_mode="Markdown")
    for p in photos[:5]:
        caption = p.get("caption", "") or "_(tanpa caption)_"
        await message.bot.send_photo(
            message.chat.id, photo=p["photo_id"],
            caption=f"🆔 ID: `{p['id']}`\n💬 {caption}\n📅 {p['uploaded_at'][:10]}",
            parse_mode="Markdown"
        )


@router.message(Command("admin_deletephoto"))
async def cmd_deletephoto(message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("Penggunaan: `/admin_deletephoto <id>`", parse_mode="Markdown")
        return
    try:
        photo_id = int(parts[1])
    except ValueError:
        await message.answer("❌ ID harus angka!")
        return
    await delete_admin_photo(photo_id, message.from_user.id)
    await message.answer(f"✅ Foto ID `{photo_id}` dihapus.", parse_mode="Markdown")


@router.message(Command("admin_stats"))
async def cmd_admin_stats(message: Message):
    if not is_admin(message.from_user.id):
        return
    total = await get_total_users()
    users = await get_all_users()
    total_coins = sum(u.get("balance", 0) for u in users)
    total_mined = sum(u.get("mine_count", 0) for u in users)
    top = sorted(users, key=lambda x: x.get("total_earned", 0), reverse=True)[:3]
    top_txt = "\n".join(
        f"  {i+1}. {u.get('display_name') or u.get('username') or u.get('first_name','?')} — {u.get('total_earned',0):,}"
        for i, u in enumerate(top)
    )
    text = (
        f"📊 *Statistik Bot*\n"
        f"━━━━━━━━━━━━━━━━━\n"
        f"👥 Total User    : `{total}`\n"
        f"💰 Total Koin    : `{total_coins:,}`\n"
        f"⛏️ Total Mine    : `{total_mined:,}` kali\n\n"
        f"🏆 Top 3 Earner:\n{top_txt}"
    )
    await message.answer(text, parse_mode="Markdown")


@router.message(Command("admin_info"))
async def cmd_admin_info(message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("Penggunaan: `/admin_info <user_id>`", parse_mode="Markdown")
        return
    try:
        uid = int(parts[1])
    except ValueError:
        await message.answer("❌ user_id harus angka!")
        return
    user = await get_user(uid)
    if not user:
        await message.answer(f"❌ User `{uid}` tidak ditemukan.")
        return

    ore_count = sum(user.get("ore_inventory", {}).values())
    display = user.get("display_name") or user.get("first_name", "-")
    text = (
        f"👤 *Info User `{uid}`*\n"
        f"Nama Game : *{display}*\n"
        f"TG Name   : {user.get('first_name','-')} @{user.get('username','-')}\n"
        f"Balance   : `{user['balance']:,}`\n"
        f"Mine Count: `{user['mine_count']}`\n"
        f"Level     : `{user['level']}`\n"
        f"Energy    : `{user['energy']}/{user['max_energy']}`\n"
        f"Alat      : `{user['current_tool']}`\n"
        f"Zona      : `{user.get('current_zone','surface')}`\n"
        f"Streak    : `{user.get('daily_streak',0)}`\n"
        f"Rebirth   : `{user.get('rebirth_count',0)}`\n"
        f"Ore Inv   : `{ore_count}` buah total\n"
        f"Bag Slots : `{user.get('bag_slots',50)}`"
    )
    await message.answer(text, parse_mode="Markdown")


@router.message(Command("admin_addcoin"))
async def cmd_addcoin(message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 3:
        await message.answer("Penggunaan: `/admin_addcoin <user_id> <jumlah>`", parse_mode="Markdown")
        return
    try:
        uid, amount = int(parts[1]), int(parts[2])
    except ValueError:
        await message.answer("❌ Format salah! Gunakan angka.")
        return
    await add_balance(uid, amount, f"Admin grant by {message.from_user.id}")
    await message.answer(f"✅ `+{amount:,}` koin → user `{uid}`", parse_mode="Markdown")


@router.message(Command("admin_setlevel"))
async def cmd_setlevel(message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 3:
        await message.answer("Penggunaan: `/admin_setlevel <user_id> <level>`", parse_mode="Markdown")
        return
    try:
        uid, lv = int(parts[1]), int(parts[2])
    except ValueError:
        await message.answer("❌ Format salah!")
        return
    lv = max(1, min(lv, MAX_LEVEL))
    await update_user(uid, level=lv, xp=0)
    await message.answer(f"✅ Level user `{uid}` → `{lv}`", parse_mode="Markdown")


@router.message(Command("admin_setenergy"))
async def cmd_setenergy(message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 3:
        await message.answer("Penggunaan: `/admin_setenergy <user_id> <jumlah>`", parse_mode="Markdown")
        return
    try:
        uid, en = int(parts[1]), int(parts[2])
    except ValueError:
        await message.answer("❌ Format salah!")
        return
    user = await get_user(uid)
    if not user:
        await message.answer("❌ User tidak ditemukan!")
        return
    # ✅ Cap energy ke max_energy user yang sebenarnya
    max_e = user.get("max_energy", 500)
    new_e = max(0, min(en, max_e))
    await update_user(uid, energy=new_e)
    await message.answer(f"✅ Energy user `{uid}` → `{new_e}/{max_e}`", parse_mode="Markdown")


@router.message(Command("admin_givetool"))
async def cmd_givetool(message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 3:
        await message.answer("Penggunaan: `/admin_givetool <user_id> <tool_id>`", parse_mode="Markdown")
        return
    try:
        uid = int(parts[1])
    except ValueError:
        await message.answer("❌ user_id harus angka!")
        return
    tool_id = parts[2]
    if tool_id not in TOOLS:
        await message.answer(f"❌ tool_id tidak valid. Cek `/admin_tools`", parse_mode="Markdown")
        return
    from game import buy_tool
    ok, msg = await buy_tool(uid, tool_id, admin=True)
    await message.answer(f"{'✅' if ok else '❌'} {msg}", parse_mode="Markdown")


@router.message(Command("admin_giveitem"))
async def cmd_giveitem(message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 3:
        await message.answer("Penggunaan: `/admin_giveitem <user_id> <item_id> [qty]`", parse_mode="Markdown")
        return
    try:
        uid = int(parts[1])
    except ValueError:
        await message.answer("❌ user_id harus angka!")
        return
    item_id = parts[2]
    try:
        qty = int(parts[3]) if len(parts) > 3 else 1
    except ValueError:
        qty = 1
    if item_id not in ITEMS:
        await message.answer(f"❌ item_id tidak valid. Cek `/admin_items`", parse_mode="Markdown")
        return
    user = await get_user(uid)
    if not user:
        await message.answer("❌ User tidak ditemukan!")
        return
    inv = dict(user["inventory"])
    inv[item_id] = inv.get(item_id, 0) + qty
    await update_user(uid, inventory=inv)
    await message.answer(f"✅ `{qty}x {ITEMS[item_id]['name']}` → user `{uid}`", parse_mode="Markdown")


@router.message(Command("admin_giveore"))
async def cmd_giveore(message: Message):
    """✅ Perintah baru: beri ore langsung ke user"""
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 4:
        await message.answer("Penggunaan: `/admin_giveore <user_id> <ore_id> <qty>`", parse_mode="Markdown")
        return
    try:
        uid = int(parts[1])
    except ValueError:
        await message.answer("❌ user_id harus angka!")
        return
    ore_id = parts[2]
    try:
        qty = int(parts[3])
    except ValueError:
        await message.answer("❌ qty harus angka!")
        return
    if ore_id not in ORES:
        await message.answer(f"❌ ore_id tidak valid. Cek `/admin_ores`", parse_mode="Markdown")
        return
    user = await get_user(uid)
    if not user:
        await message.answer("❌ User tidak ditemukan!")
        return
    ore = ORES[ore_id]
    from config import get_random_kg
    # Tambahkan dengan KG midpoint
    avg_kg = (ore.get("kg_min", 0.5) + ore.get("kg_max", 2.0)) / 2 * qty
    await add_ore_to_inventory(uid, ore_id, qty, avg_kg)
    await message.answer(
        f"✅ `{qty}x {ore['emoji']} {ore['name']}` → user `{uid}`",
        parse_mode="Markdown"
    )


@router.message(Command("admin_givezone"))
async def cmd_givezone(message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 3:
        await message.answer("Penggunaan: `/admin_givezone <user_id> <zone_id>`", parse_mode="Markdown")
        return
    try:
        uid = int(parts[1])
    except ValueError:
        await message.answer("❌ user_id harus angka!")
        return
    zone_id = parts[2]
    from game import unlock_zone
    ok, msg = await unlock_zone(uid, zone_id, admin=True)
    await message.answer(f"{'✅' if ok else '❌'} {msg}", parse_mode="Markdown")


@router.message(Command("admin_reset"))
async def cmd_reset(message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("Penggunaan: `/admin_reset <user_id>`", parse_mode="Markdown")
        return
    try:
        uid = int(parts[1])
    except ValueError:
        await message.answer("❌ user_id harus angka!")
        return
    # ✅ achievements harus list [], bukan dict {}
    await update_user(uid,
        balance=1000, total_earned=0, total_mined=0, mine_count=0,
        energy=500, max_energy=500, level=1, xp=0,
        current_tool="stone_pick", current_zone="surface",
        owned_tools=["stone_pick"], unlocked_zones=["surface"],
        inventory={}, active_buffs={}, achievements=[],
        ore_inventory={}, ore_kg_data={},
        bag_slots=50, bag_kg_used=0.0, bag_kg_max=999999.0,
        daily_streak=0, rebirth_count=0, perm_coin_mult=1.0, perm_xp_mult=1.0
    )
    await message.answer(f"✅ User `{uid}` berhasil direset.", parse_mode="Markdown")


@router.message(Command("admin_broadcast"))
async def cmd_broadcast(message: Message):
    if not is_admin(message.from_user.id):
        return
    text = message.text.replace("/admin_broadcast", "").strip()
    if not text:
        await message.answer("Penggunaan: `/admin_broadcast <pesan>`", parse_mode="Markdown")
        return
    users = await get_all_users()
    sent = failed = 0
    for u in users:
        try:
            await message.bot.send_message(
                u["user_id"],
                f"📢 *Pengumuman:*\n\n{text}",
                parse_mode="Markdown"
            )
            sent += 1
        except Exception:
            failed += 1
    await message.answer(f"✅ Broadcast selesai!\nTerkirim: `{sent}` | Gagal: `{failed}`", parse_mode="Markdown")


@router.message(Command("admin_tools"))
async def cmd_admin_tools(message: Message):
    if not is_admin(message.from_user.id):
        return
    lines = ["⛏️ *Daftar Tool ID:*\n"]
    for tid, t in TOOLS.items():
        ore_txt = " [🪨 Butuh Ore]" if t.get("ore_req") else ""
        lines.append(f"`{tid}` — {t['emoji']} {t['name']} (Tier {t['tier']}){ore_txt}")
    # Split if too long
    full = "\n".join(lines)
    if len(full) > 4000:
        mid = len(lines) // 2
        await message.answer("\n".join(lines[:mid]), parse_mode="Markdown")
        await message.answer("\n".join(lines[mid:]), parse_mode="Markdown")
    else:
        await message.answer(full, parse_mode="Markdown")


@router.message(Command("admin_items"))
async def cmd_admin_items(message: Message):
    if not is_admin(message.from_user.id):
        return
    lines = ["🎒 *Daftar Item ID:*\n"]
    for iid, item in ITEMS.items():
        lines.append(f"`{iid}` — {item['emoji']} {item['name']}")
    full = "\n".join(lines)
    if len(full) > 4000:
        mid = len(lines) // 2
        await message.answer("\n".join(lines[:mid]), parse_mode="Markdown")
        await message.answer("\n".join(lines[mid:]), parse_mode="Markdown")
    else:
        await message.answer(full, parse_mode="Markdown")


@router.message(Command("admin_zones"))
async def cmd_admin_zones(message: Message):
    if not is_admin(message.from_user.id):
        return
    lines = ["🌍 *Daftar Zone ID:*\n"]
    for zid, z in ZONES.items():
        lines.append(f"`{zid}` — {z['name']} (Lv.{z['level_req']})")
    await message.answer("\n".join(lines), parse_mode="Markdown")


@router.message(Command("admin_ores"))
async def cmd_admin_ores(message: Message):
    if not is_admin(message.from_user.id):
        return
    lines = ["🪨 *Daftar Ore ID:*\n"]
    for oid, ore in ORES.items():
        lines.append(f"`{oid}` — {ore['emoji']} {ore['name']} (value: {ore['value']:,})")
    full = "\n".join(lines)
    if len(full) > 4000:
        mid = len(lines) // 2
        await message.answer("\n".join(lines[:mid]), parse_mode="Markdown")
        await message.answer("\n".join(lines[mid:]), parse_mode="Markdown")
    else:
        await message.answer(full, parse_mode="Markdown")


@router.message(Command("admin_users"))
async def cmd_admin_users(message: Message):
    if not is_admin(message.from_user.id):
        return
    users = await get_all_users()
    lines = [f"👥 *Daftar User ({len(users)}):*\n"]
    for u in users[:20]:
        name = u.get("display_name") or u.get("username") or u.get("first_name", "?")
        lines.append(f"`{u['user_id']}` {name} Lv.{u['level']} — {u.get('balance',0):,}🪙")
    if len(users) > 20:
        lines.append(f"\n_...dan {len(users)-20} lainnya_")
    await message.answer("\n".join(lines), parse_mode="Markdown")


@router.message(Command("admin_setorephoto"))
async def cmd_setorephoto(message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    ore_id_arg = parts[1] if len(parts) > 1 else None
    photo = None
    if message.reply_to_message and message.reply_to_message.photo:
        photo = message.reply_to_message.photo[-1]
    elif message.photo:
        photo = message.photo[-1]

    if not ore_id_arg:
        await message.answer("Cara: reply foto dengan `/admin_setorephoto <ore_id>`", parse_mode="Markdown")
        return
    if not photo:
        await message.answer("❌ Tidak ada foto! Reply foto dengan perintah ini.", parse_mode="Markdown")
        return

    ore = ORES.get(ore_id_arg)
    if not ore:
        await message.answer(f"❌ Ore ID `{ore_id_arg}` tidak ditemukan!", parse_mode="Markdown")
        return

    caption = " ".join(parts[2:]) if len(parts) > 2 else ""
    await set_ore_photo(ore_id_arg, photo.file_id, caption, message.from_user.id)
    await message.answer(f"✅ Foto {ore['emoji']} *{ore['name']}* dipasang!", parse_mode="Markdown")


@router.message(F.photo & F.caption.regexp(r"^/admin_setorephoto"))
async def cmd_setorephoto_direct(message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = message.caption.split() if message.caption else []
    ore_id_arg = parts[1] if len(parts) > 1 else None
    if not ore_id_arg:
        await message.answer("❌ Sertakan ore_id.", parse_mode="Markdown")
        return
    ore = ORES.get(ore_id_arg)
    if not ore:
        await message.answer(f"❌ Ore ID `{ore_id_arg}` tidak ditemukan!", parse_mode="Markdown")
        return
    photo = message.photo[-1]
    caption = " ".join(parts[2:]) if len(parts) > 2 else ""
    await set_ore_photo(ore_id_arg, photo.file_id, caption, message.from_user.id)
    await message.answer(f"✅ Foto {ore['emoji']} *{ore['name']}* dipasang!", parse_mode="Markdown")


@router.message(Command("admin_listorephoto"))
async def cmd_listorephoto(message: Message):
    if not is_admin(message.from_user.id):
        return
    photos = await get_all_ore_photos()
    if not photos:
        await message.answer("📸 Belum ada foto ore.", parse_mode="Markdown")
        return
    lines = [f"📸 *Foto Ore ({len(photos)}):*\n"]
    for p in photos:
        ore = ORES.get(p["ore_id"], {})
        lines.append(f"{ore.get('emoji','')} `{p['ore_id']}` — {ore.get('name', p['ore_id'])}")
    await message.answer("\n".join(lines), parse_mode="Markdown")


@router.message(Command("admin_delorephoto"))
async def cmd_delorephoto(message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("Penggunaan: `/admin_delorephoto <ore_id>`", parse_mode="Markdown")
        return
    ore_id = parts[1]
    photo = await get_ore_photo(ore_id)
    if not photo:
        await message.answer(f"❌ Tidak ada foto untuk ore `{ore_id}`.", parse_mode="Markdown")
        return
    await delete_ore_photo(ore_id)
    ore = ORES.get(ore_id, {})
    await message.answer(f"✅ Foto {ore.get('emoji','')} *{ore.get('name', ore_id)}* dihapus.", parse_mode="Markdown")


# ── INLINE CALLBACK for admin panel ──────────────────────────

@router.callback_query(F.data == "admin_stats")
async def cb_admin_stats(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Bukan admin!", show_alert=True)
        return
    from database import get_total_users
    total = await get_total_users()
    from config import TOOLS, ORES, ZONES
    text = (
        "📊 *Statistik Bot*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 Total User : `{total}`\n"
        f"⛏️ Total Alat : `{len(TOOLS)}`\n"
        f"🪨 Total Ore  : `{len(ORES)}`\n"
        f"🌍 Total Zona : `{len(ZONES)}`\n"
    )
    await callback.message.edit_text(text, reply_markup=admin_kb(), parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "admin_users")
async def cb_admin_users(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Bukan admin!", show_alert=True)
        return
    from database import get_all_users
    users = await get_all_users()
    if not users:
        await callback.answer("Tidak ada user.", show_alert=True)
        return
    lines = ["👥 *Daftar User (maks 20):*", ""]
    for u in users[:20]:
        name = u.get("display_name") or u.get("first_name") or f"User {u['user_id']}"
        lines.append(f"• `{u['user_id']}` — {name} (Lv.{u['level']})")
    text = "\n".join(lines)
    await callback.message.edit_text(text, reply_markup=admin_kb(), parse_mode="Markdown")
    await callback.answer()


# ══════════════════════════════════════════════════════════════
# FOTO ALAT MINING
# ══════════════════════════════════════════════════════════════
@router.message(Command("admin_settoolphoto"))
async def cmd_settoolphoto(message: Message):
    if not is_admin(message.from_user.id):
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer(
            "ℹ️ *Cara pasang foto alat:*\n\n"
            "1. Reply foto dengan `/admin_settoolphoto [tool_id]`\n"
            "2. Atau kirim foto dengan caption `/admin_settoolphoto [tool_id]`\n\n"
            "Contoh tool_id: `stone_pick`, `diamond_drill`, dll.\n"
            "Gunakan `/admin_tools` untuk melihat semua tool_id.",
            parse_mode="Markdown"
        )
        return
    tool_id = args[1].strip()
    if tool_id not in TOOLS:
        await message.answer(f"❌ Tool `{tool_id}` tidak ditemukan!", parse_mode="Markdown")
        return

    photo = None
    caption = ""
    if message.reply_to_message and message.reply_to_message.photo:
        photo = message.reply_to_message.photo[-1]
        caption = " ".join(args[2:]) if len(args) > 2 else ""
    elif message.photo:
        photo = message.photo[-1]
        caption = message.caption or ""

    if not photo:
        await message.answer("❌ Kirim/reply foto bersamaan dengan perintah!")
        return

    tool = TOOLS[tool_id]
    await set_tool_photo(tool_id, photo.file_id, caption, message.from_user.id)
    await message.answer(
        f"✅ *Foto alat berhasil dipasang!*\n\n"
        f"🔧 Alat: *{tool['name']}*\n"
        f"🆔 ID: `{tool_id}`",
        parse_mode="Markdown"
    )


@router.message(Command("admin_listtoolphoto"))
async def cmd_listtoolphoto(message: Message):
    if not is_admin(message.from_user.id):
        return
    photos = await get_all_tool_photos()
    if not photos:
        await message.answer("📋 Belum ada foto alat yang dipasang.")
        return
    lines = ["📋 *Daftar Alat Berphoto:*\n"]
    for p in photos:
        tool = TOOLS.get(p["tool_id"], {})
        lines.append(
            f"• *{tool.get('name', p['tool_id'])}*\n"
            f"  ID: `{p['tool_id']}`\n"
            f"  Caption: _{p.get('caption','') or 'Tidak ada'}_"
        )
    await message.answer("\n".join(lines), parse_mode="Markdown")


@router.message(Command("admin_deltoolphoto"))
async def cmd_deltoolphoto(message: Message):
    if not is_admin(message.from_user.id):
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer("❌ Format: `/admin_deltoolphoto [tool_id]`", parse_mode="Markdown")
        return
    tool_id = args[1].strip()
    ok = await delete_tool_photo(tool_id)
    if ok:
        await message.answer(f"✅ Foto alat `{tool_id}` berhasil dihapus!", parse_mode="Markdown")
    else:
        await message.answer(f"❌ Foto alat `{tool_id}` tidak ditemukan!", parse_mode="Markdown")


# ══════════════════════════════════════════════════════════════
# FOTO ZONA
# ══════════════════════════════════════════════════════════════
@router.message(Command("admin_setzonephoto"))
async def cmd_setzonephoto(message: Message):
    if not is_admin(message.from_user.id):
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer(
            "ℹ️ *Cara pasang foto zona:*\n\n"
            "1. Reply foto dengan `/admin_setzonephoto [zone_id]`\n"
            "2. Atau kirim foto dengan caption `/admin_setzonephoto [zone_id]`\n\n"
            "Contoh zone_id: `surface`, `cave`, `lava_cave`, dll.\n"
            "Gunakan `/admin_zones` untuk melihat semua zone_id.",
            parse_mode="Markdown"
        )
        return
    zone_id = args[1].strip()
    if zone_id not in ZONES:
        await message.answer(f"❌ Zona `{zone_id}` tidak ditemukan!", parse_mode="Markdown")
        return

    photo = None
    caption = ""
    if message.reply_to_message and message.reply_to_message.photo:
        photo = message.reply_to_message.photo[-1]
        caption = " ".join(args[2:]) if len(args) > 2 else ""
    elif message.photo:
        photo = message.photo[-1]
        caption = message.caption or ""

    if not photo:
        await message.answer("❌ Kirim/reply foto bersamaan dengan perintah!")
        return

    zone = ZONES[zone_id]
    await set_zone_photo(zone_id, photo.file_id, caption, message.from_user.id)
    await message.answer(
        f"✅ *Foto zona berhasil dipasang!*\n\n"
        f"📍 Zona: *{zone['name']}*\n"
        f"🆔 ID: `{zone_id}`",
        parse_mode="Markdown"
    )


@router.message(Command("admin_listzonephoto"))
async def cmd_listzonephoto(message: Message):
    if not is_admin(message.from_user.id):
        return
    photos = await get_all_zone_photos()
    if not photos:
        await message.answer("📋 Belum ada foto zona yang dipasang.")
        return
    lines = ["📋 *Daftar Zona Berphoto:*\n"]
    for p in photos:
        zone = ZONES.get(p["zone_id"], {})
        lines.append(
            f"• *{zone.get('name', p['zone_id'])}*\n"
            f"  ID: `{p['zone_id']}`\n"
            f"  Caption: _{p.get('caption','') or 'Tidak ada'}_"
        )
    await message.answer("\n".join(lines), parse_mode="Markdown")


@router.message(Command("admin_delzonephoto"))
async def cmd_delzonephoto(message: Message):
    if not is_admin(message.from_user.id):
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer("❌ Format: `/admin_delzonephoto [zone_id]`", parse_mode="Markdown")
        return
    zone_id = args[1].strip()
    ok = await delete_zone_photo(zone_id)
    if ok:
        await message.answer(f"✅ Foto zona `{zone_id}` berhasil dihapus!", parse_mode="Markdown")
    else:
        await message.answer(f"❌ Foto zona `{zone_id}` tidak ditemukan!", parse_mode="Markdown")
