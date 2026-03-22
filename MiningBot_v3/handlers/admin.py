import asyncio
from aiogram import Router, F
from aiogram.types import Message, PhotoSize, CallbackQuery
from aiogram.filters import Command

from config import ADMIN_IDS, STATIC_ADMIN_IDS, TOOLS, ITEMS, ZONES, ORES, MAX_LEVEL
from database import (get_user, update_user, get_all_users, get_total_users,
                       add_balance, save_admin_photo, get_admin_photos,
                       delete_admin_photo, set_ore_photo, get_ore_photo,
                       get_all_ore_photos, delete_ore_photo,
                       set_tool_photo, get_tool_photo, get_all_tool_photos, delete_tool_photo,
                       set_zone_photo, get_zone_photo, get_all_zone_photos, delete_zone_photo,
                       set_item_photo, get_item_photo, get_all_item_photos, delete_item_photo,
                       set_vip_photo, get_vip_photo, delete_vip_photo,
                       set_topup_photo, get_topup_photo, delete_topup_photo,
                       add_ore_to_inventory,
                       add_dynamic_admin, remove_dynamic_admin, get_dynamic_admins,
                       is_dynamic_admin, reset_all_users,
                       ban_user, unban_user)
from keyboards import admin_kb, back_main_kb

router = Router()


async def is_admin(user_id: int) -> bool:
    """Cek apakah user adalah admin (statis dari .env ATAU dinamis dari DB)."""
    if user_id in STATIC_ADMIN_IDS:
        return True
    return await is_dynamic_admin(user_id)


@router.message(Command("adminhelp"))
async def cmd_adminhelp(message: Message):
    if not await is_admin(message.from_user.id):
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
        "/admin_reset [user_id] — Reset data 1 user",
        "/admin_resetall KONFIRMASI — ⚠️ Reset SEMUA data pemain",
        "/admin_ban [user_id] [alasan] — 🚫 Ban user",
        "/admin_unban [user_id] — ✅ Unban user",
        "",
        "<b>🛡️ Manajemen Admin:</b>",
        "/admin_listadmin — Lihat semua admin",
        "/admin_addadmin [user_id] [catatan] — Tambah admin baru",
        "/admin_removeadmin [user_id] — Hapus admin dinamis",
        "<i>⚠️ addadmin & removeadmin hanya untuk super-admin (.env)</i>",
        "",
        "<b>👑 VIP Management:</b>",
        "/admin_givevip [user_id] [plan_id] — Beri VIP",
        "/admin_revokevip [user_id] — Cabut VIP",
        "<i>Plan ID: 3_days, 7_days, 14_days, 30_days</i>",
        "",
        "<b>📸 Foto Admin, Ore, Alat, Zona, Item, VIP & TopUp:</b>",
        "/admin_setphoto — Upload foto profil admin",
        "/admin_myphotos — Lihat foto profil admin",
        "/admin_deletephoto [id] — Hapus foto profil",
        "/admin_setorephoto [ore_id] — Pasang foto/GIF ORE",
        "/admin_listorephoto — Lihat semua ore berphoto",
        "/admin_delorephoto [ore_id] — Hapus foto ore",
        "/admin_settoolphoto [tool_id] — Pasang foto/GIF ALAT MINING",
        "/admin_listtoolphoto — Lihat semua alat berphoto",
        "/admin_deltoolphoto [tool_id] — Hapus foto alat",
        "/admin_setzonephoto [zone_id] — Pasang foto/GIF ZONA",
        "/admin_listzonephoto — Lihat semua zona berphoto",
        "/admin_delzonephoto [zone_id] — Hapus foto zona",
        "/admin_setitemphoto [item_id] — Pasang foto/GIF ITEM",
        "/admin_listitemphoto — Lihat semua item berphoto",
        "/admin_delitemphoto [item_id] — Hapus foto item",
        "/admin_setvipphoto — Pasang foto/GIF halaman VIP",
        "/admin_delvipphoto — Hapus foto VIP",
        "/admin_settopupphoto — Pasang foto/GIF halaman TopUp",
        "/admin_deltopupphoto — Hapus foto TopUp",
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
        "• /shop → Upgrade: slot bag & energy gratis untuk admin",
        "• Admin otomatis terdeteksi dari ADMIN_IDS di .env",
    ]
    text = "\n".join(lines)
    await message.answer(text, parse_mode="HTML")


@router.message(Command("admin_setphoto"))
async def cmd_setphoto(message: Message):
    if not await is_admin(message.from_user.id):
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
    if not await is_admin(message.from_user.id):
        return
    photo = message.photo[-1]
    caption = (message.caption or "").replace("/admin_setphoto", "").strip()
    await save_admin_photo(message.from_user.id, photo.file_id, caption)
    await message.answer(f"✅ *Foto berhasil disimpan!*", parse_mode="Markdown")


@router.message(Command("admin_myphotos"))
async def cmd_myphotos(message: Message):
    if not await is_admin(message.from_user.id):
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
    if not await is_admin(message.from_user.id):
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
    if not await is_admin(message.from_user.id):
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
    if not await is_admin(message.from_user.id):
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
    if not await is_admin(message.from_user.id):
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
    # Clamp: max 1 triliun per grant, boleh negatif (debit) tapi max -1M
    MAX_GRANT = 1_000_000_000_000
    if abs(amount) > MAX_GRANT:
        await message.answer(f"❌ Jumlah terlalu besar! Maksimal: `{MAX_GRANT:,}`", parse_mode="Markdown")
        return
    user = await get_user(uid)
    if not user:
        await message.answer(f"❌ User `{uid}` tidak ditemukan!")
        return
    await add_balance(uid, amount, f"Admin grant by {message.from_user.id}")
    user_after = await get_user(uid)
    action = "+" if amount >= 0 else ""
    await message.answer(
        f"✅ `{action}{amount:,}` koin → user `{uid}`\n"
        f"💰 Saldo baru: `{user_after['balance']:,}` koin",
        parse_mode="Markdown"
    )


@router.message(Command("admin_setlevel"))
async def cmd_setlevel(message: Message):
    if not await is_admin(message.from_user.id):
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
    user = await get_user(uid)
    if not user:
        await message.answer(f"❌ User `{uid}` tidak ditemukan!")
        return
    await update_user(uid, level=lv, xp=0)
    await message.answer(f"✅ Level user `{uid}` → `{lv}`", parse_mode="Markdown")


@router.message(Command("admin_setenergy"))
async def cmd_setenergy(message: Message):
    if not await is_admin(message.from_user.id):
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
    if not await is_admin(message.from_user.id):
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
    if not await is_admin(message.from_user.id):
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
    if not await is_admin(message.from_user.id):
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
    # Cek kapasitas bag user (admin bisa override, tapi beri warning)
    ore_inv_now = user.get("ore_inventory", {})
    total_in_bag = sum(ore_inv_now.values())
    bag_slots = user.get("bag_slots", 50)
    bag_note = ""
    if total_in_bag + qty > bag_slots:
        bag_note = f"\n⚠️ Bag user melebihi kapasitas ({total_in_bag + qty}/{bag_slots})!"
    # FIX Bug #5: gunakan kg_min (berat teringan) agar tidak meledakkan bag_kg_used
    # saat admin give ore dengan kg_max sangat besar (misal ancient_fossil = 15.000 kg)
    unit_kg = ore.get("kg_min", 0.5)
    avg_kg  = round(unit_kg * qty, 2)
    await add_ore_to_inventory(uid, ore_id, qty, avg_kg)
    await message.answer(
        f"✅ `{qty}x {ore['emoji']} {ore['name']}` → user `{uid}`{bag_note}",
        parse_mode="Markdown"
    )


@router.message(Command("admin_givezone"))
async def cmd_givezone(message: Message):
    if not await is_admin(message.from_user.id):
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
    if not await is_admin(message.from_user.id):
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
    from config import STARTING_BALANCE
    # ✅ Reset semua field ke nilai awal (lengkap)
    await update_user(uid,
        balance=STARTING_BALANCE, total_earned=0, total_mined=0, mine_count=0,
        energy=500, max_energy=500, level=1, xp=0,
        current_tool="stone_pick", current_zone="surface",
        owned_tools=["stone_pick"], unlocked_zones=["surface"],
        inventory={}, active_buffs={}, achievements=[],
        ore_inventory={}, ore_kg_data={},
        museum_ores=[], favorite_ores=[],
        bag_slots=50, bag_kg_used=0.0, bag_kg_max=100.0,
        total_kg_mined=0.0,
        daily_streak=0, last_daily=None, last_energy_regen=None,
        last_mine_time=None, last_auto_mine=None,
        rebirth_count=0, perm_coin_mult=1.0, perm_xp_mult=1.0,
        vip_expires_at=None, vip_type=None,
        transfer_send_count=0, transfer_receive_count=0, transfer_week_start=None,
        last_name_change=None,
        is_mining_multi=0, mining_multi_type=None, mining_multi_started=None
    )
    await message.answer(f"✅ User `{uid}` berhasil direset.", parse_mode="Markdown")


@router.message(Command("admin_broadcast"))
async def cmd_broadcast(message: Message):
    if not await is_admin(message.from_user.id):
        return
    text = message.text.replace("/admin_broadcast", "").strip()
    if not text:
        await message.answer("Penggunaan: `/admin_broadcast <pesan>`", parse_mode="Markdown")
        return
    users = await get_all_users()
    sent = failed = 0
    status_msg = await message.answer(f"📢 Memulai broadcast ke {len(users)} user...")
    for i, u in enumerate(users):
        try:
            await message.bot.send_message(
                u["user_id"],
                f"📢 *Pengumuman:*\n\n{text}",
                parse_mode="Markdown"
            )
            sent += 1
        except Exception:
            failed += 1
        # Rate limiting: 30 pesan/detik max (Telegram limit)
        await asyncio.sleep(0.05)
        # Update progress setiap 50 user
        if (i + 1) % 50 == 0:
            try:
                await status_msg.edit_text(
                    f"📢 Broadcast berjalan... {i+1}/{len(users)} user"
                )
            except Exception:
                pass
    try:
        await status_msg.edit_text(
            f"✅ Broadcast selesai!\nTerkirim: `{sent}` | Gagal: `{failed}`",
            parse_mode="Markdown"
        )
    except Exception:
        await message.answer(f"✅ Broadcast selesai!\nTerkirim: `{sent}` | Gagal: `{failed}`", parse_mode="Markdown")


@router.message(Command("admin_tools"))
async def cmd_admin_tools(message: Message):
    if not await is_admin(message.from_user.id):
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
    if not await is_admin(message.from_user.id):
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
    if not await is_admin(message.from_user.id):
        return
    lines = ["🌍 *Daftar Zone ID:*\n"]
    for zid, z in ZONES.items():
        lines.append(f"`{zid}` — {z['name']} (Lv.{z['level_req']})")
    full = "\n".join(lines)
    if len(full) > 4000:
        chunk, chunk_len = [], 0
        for line in lines:
            if chunk_len + len(line) + 1 > 3800 and chunk:
                await message.answer("\n".join(chunk), parse_mode="Markdown")
                chunk, chunk_len = [], 0
            chunk.append(line)
            chunk_len += len(line) + 1
        if chunk:
            await message.answer("\n".join(chunk), parse_mode="Markdown")
    else:
        await message.answer(full, parse_mode="Markdown")


@router.message(Command("admin_ores"))
async def cmd_admin_ores(message: Message):
    if not await is_admin(message.from_user.id):
        return
    lines = ["🪨 *Daftar Ore ID:*\n"]
    for oid, ore in ORES.items():
        lines.append(f"`{oid}` — {ore['emoji']} {ore['name']} (value: {ore['value']:,})")
    # Kirim dalam chunks agar tidak melebihi batas Telegram 4096 karakter
    chunk, chunk_len = [], 0
    for line in lines:
        line_len = len(line) + 1
        if chunk_len + line_len > 3800 and chunk:
            await message.answer("\n".join(chunk), parse_mode="Markdown")
            chunk, chunk_len = [], 0
        chunk.append(line)
        chunk_len += line_len
    if chunk:
        await message.answer("\n".join(chunk), parse_mode="Markdown")


@router.message(Command("admin_users"))
async def cmd_admin_users(message: Message):
    if not await is_admin(message.from_user.id):
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
    if not await is_admin(message.from_user.id):
        return
    parts = message.text.split()
    ore_id_arg = parts[1] if len(parts) > 1 else None
    photo = None
    is_animation = False
    if message.reply_to_message:
        if message.reply_to_message.photo:
            photo = message.reply_to_message.photo[-1]
        elif message.reply_to_message.animation:
            photo = message.reply_to_message.animation
            is_animation = True
    elif message.photo:
        photo = message.photo[-1]

    if not ore_id_arg:
        await message.answer("Cara: reply foto/GIF dengan `/admin_setorephoto <ore_id>`", parse_mode="Markdown")
        return
    if not photo:
        await message.answer("❌ Tidak ada foto/GIF! Reply foto atau GIF dengan perintah ini.", parse_mode="Markdown")
        return

    ore = ORES.get(ore_id_arg)
    if not ore:
        await message.answer(f"❌ Ore ID `{ore_id_arg}` tidak ditemukan!", parse_mode="Markdown")
        return

    caption = " ".join(parts[2:]) if len(parts) > 2 else ""
    await set_ore_photo(ore_id_arg, photo.file_id, caption, message.from_user.id)
    kind = "GIF" if is_animation else "Foto"
    await message.answer(f"✅ {kind} {ore['emoji']} *{ore['name']}* dipasang!", parse_mode="Markdown")


@router.message(F.photo & F.caption.regexp(r"^/admin_setorephoto"))
async def cmd_setorephoto_direct(message: Message):
    if not await is_admin(message.from_user.id):
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
    if not await is_admin(message.from_user.id):
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
    if not await is_admin(message.from_user.id):
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
    if not await is_admin(callback.from_user.id):
        await callback.answer("❌ Bukan admin!", show_alert=True)
        return
    total = await get_total_users()
    text = (
        "📊 *Statistik Bot*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 Total User : `{total}`\n"
        f"⛏️ Total Alat : `{len(TOOLS)}`\n"
        f"🪨 Total Ore  : `{len(ORES)}`\n"
        f"🌍 Total Zona : `{len(ZONES)}`\n"
    )
    try:
        await callback.message.edit_text(text, reply_markup=admin_kb(), parse_mode="Markdown")
    except Exception:
        pass
    await callback.answer()


@router.callback_query(F.data == "admin_users")
async def cb_admin_users(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        await callback.answer("❌ Bukan admin!", show_alert=True)
        return
    users = await get_all_users()
    if not users:
        await callback.answer("Tidak ada user.", show_alert=True)
        return
    lines = ["👥 *Daftar User (maks 20):*", ""]
    for u in users[:20]:
        name = u.get("display_name") or u.get("first_name") or f"User {u['user_id']}"
        lines.append(f"• `{u['user_id']}` — {name} (Lv.{u['level']})")
    text = "\n".join(lines)
    try:
        await callback.message.edit_text(text, reply_markup=admin_kb(), parse_mode="Markdown")
    except Exception:
        pass
    await callback.answer()


# ══════════════════════════════════════════════════════════════
# FOTO ALAT MINING
# ══════════════════════════════════════════════════════════════
@router.message(Command("admin_settoolphoto"))
async def cmd_settoolphoto(message: Message):
    if not await is_admin(message.from_user.id):
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
    is_animation = False
    caption = ""
    if message.reply_to_message:
        if message.reply_to_message.photo:
            photo = message.reply_to_message.photo[-1]
            caption = " ".join(args[2:]) if len(args) > 2 else ""
        elif message.reply_to_message.animation:
            photo = message.reply_to_message.animation
            is_animation = True
            caption = " ".join(args[2:]) if len(args) > 2 else ""
    elif message.photo:
        photo = message.photo[-1]
        caption = message.caption or ""

    if not photo:
        await message.answer("❌ Kirim/reply foto atau GIF bersamaan dengan perintah!")
        return

    tool = TOOLS[tool_id]
    await set_tool_photo(tool_id, photo.file_id, caption, message.from_user.id)
    kind = "GIF" if is_animation else "Foto"
    await message.answer(
        f"✅ *{kind} alat berhasil dipasang!*\n\n"
        f"🔧 Alat: *{tool['name']}*\n"
        f"🆔 ID: `{tool_id}`",
        parse_mode="Markdown"
    )


@router.message(Command("admin_listtoolphoto"))
async def cmd_listtoolphoto(message: Message):
    if not await is_admin(message.from_user.id):
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
    if not await is_admin(message.from_user.id):
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
    if not await is_admin(message.from_user.id):
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
    is_animation = False
    caption = ""
    if message.reply_to_message:
        if message.reply_to_message.photo:
            photo = message.reply_to_message.photo[-1]
            caption = " ".join(args[2:]) if len(args) > 2 else ""
        elif message.reply_to_message.animation:
            photo = message.reply_to_message.animation
            is_animation = True
            caption = " ".join(args[2:]) if len(args) > 2 else ""
    elif message.photo:
        photo = message.photo[-1]
        caption = message.caption or ""

    if not photo:
        await message.answer("❌ Kirim/reply foto atau GIF bersamaan dengan perintah!")
        return

    zone = ZONES[zone_id]
    await set_zone_photo(zone_id, photo.file_id, caption, message.from_user.id)
    kind = "GIF" if is_animation else "Foto"
    await message.answer(
        f"✅ *{kind} zona berhasil dipasang!*\n\n"
        f"📍 Zona: *{zone['name']}*\n"
        f"🆔 ID: `{zone_id}`",
        parse_mode="Markdown"
    )


@router.message(Command("admin_listzonephoto"))
async def cmd_listzonephoto(message: Message):
    if not await is_admin(message.from_user.id):
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
    if not await is_admin(message.from_user.id):
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


# ══════════════════════════════════════════════════════════════
# MANAJEMEN ADMIN DINAMIS
# ══════════════════════════════════════════════════════════════

@router.message(Command("admin_addadmin"))
async def cmd_addadmin(message: Message):
    """Tambah admin baru secara dinamis (hanya super-admin dari .env yang bisa)."""
    if message.from_user.id not in STATIC_ADMIN_IDS:
        return  # Hanya super-admin yang bisa tambah admin
    parts = message.text.split(None, 2)
    if len(parts) < 2:
        await message.answer(
            "ℹ️ *Cara tambah admin:*\n\n"
            "`/admin_addadmin <user_id> [catatan]`\n\n"
            "Contoh:\n"
            "`/admin_addadmin 123456789`\n"
            "`/admin_addadmin 123456789 Admin backup`",
            parse_mode="Markdown"
        )
        return
    try:
        target_id = int(parts[1])
    except ValueError:
        await message.answer("❌ user_id harus angka!", parse_mode="Markdown")
        return
    if target_id in STATIC_ADMIN_IDS:
        await message.answer(
            f"⚠️ User `{target_id}` sudah menjadi super-admin (dari .env).",
            parse_mode="Markdown"
        )
        return
    note = parts[2] if len(parts) > 2 else ""
    already = await is_dynamic_admin(target_id)
    if already:
        await message.answer(
            f"⚠️ User `{target_id}` sudah terdaftar sebagai admin dinamis.",
            parse_mode="Markdown"
        )
        return
    await add_dynamic_admin(target_id, message.from_user.id, note)
    # Refresh ADMIN_IDS global
    from config import get_all_admin_ids
    await get_all_admin_ids()
    user_info = await get_user(target_id)
    name = ""
    if user_info:
        name = f" ({user_info.get('display_name') or user_info.get('first_name', '')})"
    await message.answer(
        f"✅ *Admin baru berhasil ditambahkan!*\n\n"
        f"👤 User ID: `{target_id}`{name}\n"
        f"📝 Catatan: _{note or 'Tidak ada'}_\n"
        f"👑 Ditambahkan oleh: `{message.from_user.id}`",
        parse_mode="Markdown"
    )


@router.message(Command("admin_removeadmin"))
async def cmd_removeadmin(message: Message):
    """Hapus admin dinamis (hanya super-admin dari .env yang bisa)."""
    if message.from_user.id not in STATIC_ADMIN_IDS:
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer(
            "ℹ️ Cara hapus admin:\n`/admin_removeadmin <user_id>`",
            parse_mode="Markdown"
        )
        return
    try:
        target_id = int(parts[1])
    except ValueError:
        await message.answer("❌ user_id harus angka!")
        return
    if target_id in STATIC_ADMIN_IDS:
        await message.answer(
            f"❌ Tidak bisa hapus super-admin `{target_id}` (didefinisikan di .env).",
            parse_mode="Markdown"
        )
        return
    ok = await remove_dynamic_admin(target_id)
    # Refresh ADMIN_IDS global
    from config import get_all_admin_ids
    await get_all_admin_ids()
    if ok:
        await message.answer(
            f"✅ Admin `{target_id}` berhasil dihapus.", parse_mode="Markdown"
        )
    else:
        await message.answer(
            f"❌ User `{target_id}` tidak ditemukan di daftar admin dinamis.",
            parse_mode="Markdown"
        )


@router.message(Command("admin_listadmin"))
async def cmd_listadmin(message: Message):
    """Tampilkan semua admin (statis + dinamis)."""
    if not await is_admin(message.from_user.id):
        return
    lines = ["👑 *Daftar Admin Bot*\n━━━━━━━━━━━━━━━━━━━━\n"]
    lines.append("*🔒 Super Admin (dari .env):*")
    for uid in STATIC_ADMIN_IDS:
        u = await get_user(uid)
        name = u.get("display_name") or u.get("first_name", "-") if u else "-"
        lines.append(f"  • `{uid}` — {name}")
    dynamic = await get_dynamic_admins()
    lines.append(f"\n*🛡️ Admin Dinamis ({len(dynamic)}):*")
    if dynamic:
        for d in dynamic:
            u = await get_user(d["user_id"])
            name = u.get("display_name") or u.get("first_name", "-") if u else "-"
            note = f" _{d['note']}_" if d.get("note") else ""
            added = d.get("added_at", "")[:10]
            lines.append(f"  • `{d['user_id']}` — {name}{note} (ditambah: {added})")
    else:
        lines.append("  _(Belum ada admin dinamis)_")
    lines.append(
        "\n💡 Gunakan `/admin_addadmin <user_id>` untuk tambah admin\n"
        "💡 Gunakan `/admin_removeadmin <user_id>` untuk hapus admin"
    )
    await message.answer("\n".join(lines), parse_mode="Markdown")


# ══════════════════════════════════════════════════════════════
# RESET SEMUA DATA PEMAIN
# ══════════════════════════════════════════════════════════════

@router.message(Command("admin_resetall"))
async def cmd_resetall(message: Message):
    """Reset SEMUA data pemain ke nilai awal. Hanya super-admin."""
    if message.from_user.id not in STATIC_ADMIN_IDS:
        await message.answer("❌ Perintah ini hanya untuk super-admin!", parse_mode="Markdown")
        return
    # Konfirmasi pertama
    parts = message.text.split()
    if len(parts) < 2 or parts[1].upper() != "KONFIRMASI":
        await message.answer(
            "⚠️ *PERINGATAN KERAS!*\n\n"
            "Perintah ini akan *mereset semua data pemain* ke nilai awal:\n"
            "• Balance → 1,000 koin\n"
            "• Level → 1\n"
            "• Alat → Stone Pick\n"
            "• Ore, Inventory, Museum, Favorit → kosong\n"
            "• Mining log & Market → dihapus\n\n"
            "❗ Tindakan ini *TIDAK BISA DIBATALKAN!*\n\n"
            "Ketik `/admin_resetall KONFIRMASI` untuk melanjutkan.",
            parse_mode="Markdown"
        )
        return

    await message.answer("⏳ Mereset semua data pemain...", parse_mode="Markdown")
    count = await reset_all_users()
    await message.answer(
        f"✅ *Reset selesai!*\n\n"
        f"👥 Total pemain direset: `{count}`\n"
        f"🗑️ Mining log, transaksi & market listing dihapus.\n"
        f"⚙️ Semua pemain kembali ke awal.",
        parse_mode="Markdown"
    )


# ══════════════════════════════════════════════════════════════
# BAN / UNBAN USER
# ══════════════════════════════════════════════════════════════

@router.message(Command("admin_ban"))
async def cmd_ban_user(message: Message):
    """Ban user: /admin_ban <user_id> [alasan]"""
    if not await is_admin(message.from_user.id):
        return
    parts = message.text.split(None, 2)
    if len(parts) < 2:
        await message.answer(
            "ℹ️ *Format:* `/admin_ban <user_id> [alasan]`\n\n"
            "Contoh:\n`/admin_ban 123456789 Cheating`",
            parse_mode="Markdown"
        )
        return
    try:
        target_id = int(parts[1])
    except ValueError:
        await message.answer("❌ user_id harus angka!")
        return
    if target_id in STATIC_ADMIN_IDS:
        await message.answer("❌ Tidak bisa ban super-admin!")
        return
    reason = parts[2] if len(parts) > 2 else "Tidak ada alasan"
    user_info = await get_user(target_id)
    if not user_info:
        await message.answer(f"❌ User `{target_id}` tidak ditemukan!", parse_mode="Markdown")
        return
    await ban_user(target_id, reason)
    name = user_info.get("display_name") or user_info.get("first_name", "-")
    await message.answer(
        f"🚫 *User berhasil dibanned!*\n\n"
        f"👤 Nama: *{name}*\n"
        f"🆔 ID: `{target_id}`\n"
        f"📋 Alasan: _{reason}_",
        parse_mode="Markdown"
    )


@router.message(Command("admin_unban"))
async def cmd_unban_user(message: Message):
    """Unban user: /admin_unban <user_id>"""
    if not await is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer(
            "ℹ️ *Format:* `/admin_unban <user_id>`",
            parse_mode="Markdown"
        )
        return
    try:
        target_id = int(parts[1])
    except ValueError:
        await message.answer("❌ user_id harus angka!")
        return
    user_info = await get_user(target_id)
    if not user_info:
        await message.answer(f"❌ User `{target_id}` tidak ditemukan!", parse_mode="Markdown")
        return
    ok = await unban_user(target_id)
    name = user_info.get("display_name") or user_info.get("first_name", "-")
    if ok:
        await message.answer(
            f"✅ *User berhasil di-unban!*\n\n"
            f"👤 Nama: *{name}*\n"
            f"🆔 ID: `{target_id}`",
            parse_mode="Markdown"
        )
    else:
        await message.answer(f"⚠️ User `{target_id}` tidak dalam status banned.", parse_mode="Markdown")


# ══════════════════════════════════════════════════════════════
# FOTO ITEM
# ══════════════════════════════════════════════════════════════

@router.message(Command("admin_setitemphoto"))
async def cmd_setitemphoto(message: Message):
    if not await is_admin(message.from_user.id):
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer(
            "📸 *Format:* Reply foto dengan `/admin_setitemphoto <item_id>`\n\n"
            "Gunakan /admin_items untuk lihat daftar item_id.",
            parse_mode="Markdown"
        )
        return
    item_id = args[1].strip()
    from config import ITEMS
    if item_id not in ITEMS:
        await message.answer(f"❌ item_id `{item_id}` tidak ditemukan!\nGunakan /admin_items.", parse_mode="Markdown")
        return
    if message.reply_to_message and message.reply_to_message.photo:
        photo = message.reply_to_message.photo[-1]
    elif message.reply_to_message and message.reply_to_message.animation:
        photo = message.reply_to_message.animation
        await set_item_photo(item_id, photo.file_id, "", message.from_user.id)
        item = ITEMS.get(item_id, {})
        await message.answer(f"✅ GIF item *{item.get('name', item_id)}* berhasil dipasang!", parse_mode="Markdown")
        return
    else:
        await message.answer("❌ Reply ke foto/GIF item dulu!", parse_mode="Markdown")
        return
    caption = " ".join(args[2:]) if len(args) > 2 else ""
    await set_item_photo(item_id, photo.file_id, caption, message.from_user.id)
    item = ITEMS.get(item_id, {})
    await message.answer(
        f"✅ Foto item *{item.get('name', item_id)}* berhasil dipasang!\n"
        f"🆔 item_id: `{item_id}`",
        parse_mode="Markdown"
    )


@router.message(F.photo & F.caption.regexp(r"^/admin_setitemphoto\s+\S+"))
async def cmd_setitemphoto_direct(message: Message):
    if not await is_admin(message.from_user.id):
        return
    args = (message.caption or "").split()
    item_id = args[1].strip() if len(args) > 1 else ""
    from config import ITEMS
    if item_id not in ITEMS:
        await message.answer(f"❌ item_id `{item_id}` tidak ditemukan!", parse_mode="Markdown")
        return
    photo = message.photo[-1]
    caption = " ".join(args[2:]) if len(args) > 2 else ""
    await set_item_photo(item_id, photo.file_id, caption, message.from_user.id)
    item = ITEMS.get(item_id, {})
    await message.answer(f"✅ Foto item *{item.get('name', item_id)}* berhasil dipasang!", parse_mode="Markdown")


@router.message(Command("admin_listitemphoto"))
async def cmd_listitemphoto(message: Message):
    if not await is_admin(message.from_user.id):
        return
    from config import ITEMS
    photos = await get_all_item_photos()
    if not photos:
        await message.answer("📋 Belum ada foto item yang dipasang.")
        return
    lines = ["📋 *Daftar Item Berphoto:*\n"]
    for p in photos:
        item = ITEMS.get(p["item_id"], {})
        lines.append(
            f"• {item.get('emoji','')} *{item.get('name', p['item_id'])}*\n"
            f"  ID: `{p['item_id']}`"
        )
    await message.answer("\n".join(lines), parse_mode="Markdown")


@router.message(Command("admin_delitemphoto"))
async def cmd_delitemphoto(message: Message):
    if not await is_admin(message.from_user.id):
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer("❌ Format: `/admin_delitemphoto <item_id>`", parse_mode="Markdown")
        return
    item_id = args[1].strip()
    ok = await delete_item_photo(item_id)
    if ok:
        await message.answer(f"✅ Foto item `{item_id}` berhasil dihapus!", parse_mode="Markdown")
    else:
        await message.answer(f"❌ Foto item `{item_id}` tidak ditemukan!", parse_mode="Markdown")


# ══════════════════════════════════════════════════════════════
# FOTO VIP
# ══════════════════════════════════════════════════════════════

@router.message(Command("admin_setvipphoto"))
async def cmd_setvipphoto(message: Message):
    if not await is_admin(message.from_user.id):
        return
    if message.reply_to_message and message.reply_to_message.photo:
        photo = message.reply_to_message.photo[-1]
    elif message.reply_to_message and message.reply_to_message.animation:
        photo = message.reply_to_message.animation
        await set_vip_photo(photo.file_id, "VIP", message.from_user.id)
        await message.answer("✅ *GIF halaman VIP berhasil dipasang!*", parse_mode="Markdown")
        return
    elif message.photo:
        photo = message.photo[-1]
    else:
        await message.answer("❌ Reply ke foto/GIF atau kirim foto dengan caption `/admin_setvipphoto`", parse_mode="Markdown")
        return
    caption = (message.caption or message.text or "").replace("/admin_setvipphoto", "").strip()
    await set_vip_photo(photo.file_id, caption, message.from_user.id)
    await message.answer("✅ *Foto halaman VIP berhasil dipasang!*", parse_mode="Markdown")


@router.message(F.photo & F.caption.startswith("/admin_setvipphoto"))
async def cmd_setvipphoto_direct(message: Message):
    if not await is_admin(message.from_user.id):
        return
    photo = message.photo[-1]
    caption = (message.caption or "").replace("/admin_setvipphoto", "").strip()
    await set_vip_photo(photo.file_id, caption, message.from_user.id)
    await message.answer("✅ *Foto halaman VIP berhasil dipasang!*", parse_mode="Markdown")


@router.message(Command("admin_delvipphoto"))
async def cmd_delvipphoto(message: Message):
    if not await is_admin(message.from_user.id):
        return
    ok = await delete_vip_photo()
    await message.answer("✅ Foto VIP dihapus." if ok else "❌ Tidak ada foto VIP.", parse_mode="Markdown")


# ══════════════════════════════════════════════════════════════
# FOTO TOPUP
# ══════════════════════════════════════════════════════════════

@router.message(Command("admin_settopupphoto"))
async def cmd_settopupphoto(message: Message):
    if not await is_admin(message.from_user.id):
        return
    if message.reply_to_message and message.reply_to_message.photo:
        photo = message.reply_to_message.photo[-1]
    elif message.reply_to_message and message.reply_to_message.animation:
        photo = message.reply_to_message.animation
        await set_topup_photo(photo.file_id, "TopUp", message.from_user.id)
        await message.answer("✅ *GIF halaman TopUp berhasil dipasang!*", parse_mode="Markdown")
        return
    elif message.photo:
        photo = message.photo[-1]
    else:
        await message.answer("❌ Reply ke foto/GIF atau kirim foto dengan caption `/admin_settopupphoto`", parse_mode="Markdown")
        return
    caption = (message.caption or message.text or "").replace("/admin_settopupphoto", "").strip()
    await set_topup_photo(photo.file_id, caption, message.from_user.id)
    await message.answer("✅ *Foto halaman TopUp berhasil dipasang!*", parse_mode="Markdown")


@router.message(F.photo & F.caption.startswith("/admin_settopupphoto"))
async def cmd_settopupphoto_direct(message: Message):
    if not await is_admin(message.from_user.id):
        return
    photo = message.photo[-1]
    caption = (message.caption or "").replace("/admin_settopupphoto", "").strip()
    await set_topup_photo(photo.file_id, caption, message.from_user.id)
    await message.answer("✅ *Foto halaman TopUp berhasil dipasang!*", parse_mode="Markdown")


@router.message(Command("admin_deltopupphoto"))
async def cmd_deltopupphoto(message: Message):
    if not await is_admin(message.from_user.id):
        return
    ok = await delete_topup_photo()
    await message.answer("✅ Foto TopUp dihapus." if ok else "❌ Tidak ada foto TopUp.", parse_mode="Markdown")


# ══════════════════════════════════════════════════════════════
# GIVE VIP / REVOKE VIP
# ══════════════════════════════════════════════════════════════

@router.message(Command("admin_givevip"))
async def cmd_givevip(message: Message):
    if not await is_admin(message.from_user.id):
        return
    args = message.text.split()[1:]
    if len(args) < 2:
        await message.answer(
            "❌ Format: `/admin_givevip [user_id] [plan_id]`\n"
            "Plan tersedia: `3_days`, `7_days`, `14_days`, `30_days`",
            parse_mode="Markdown"
        )
        return
    try:
        target_id = int(args[0])
        plan_id = args[1]
    except ValueError:
        await message.answer("❌ `user_id` harus berupa angka!", parse_mode="Markdown")
        return
    from config import VIP_PRICES
    plan = VIP_PRICES.get(plan_id)
    if not plan:
        valid = ", ".join(f"`{k}`" for k in VIP_PRICES.keys())
        await message.answer(
            f"❌ Plan tidak valid!\nPilihan yang tersedia: {valid}",
            parse_mode="Markdown"
        )
        return
    target = await get_user(target_id)
    if not target:
        await message.answer(f"❌ User `{target_id}` tidak ditemukan!", parse_mode="Markdown")
        return
    from datetime import datetime, timedelta
    # Jika sudah VIP aktif, perpanjang dari waktu sekarang
    existing_exp = target.get("vip_expires_at")
    base_dt = datetime.now()
    if existing_exp:
        try:
            exp_dt = datetime.fromisoformat(existing_exp)
            if exp_dt > base_dt:
                base_dt = exp_dt  # perpanjang dari expiry yang ada
        except Exception:
            pass
    new_exp = base_dt + timedelta(days=plan["days"])
    await update_user(target_id, vip_expires_at=new_exp.isoformat())
    target_name = target.get("display_name") or target.get("first_name", str(target_id))
    await message.answer(
        f"✅ *VIP {plan['label']} diberikan!*\n\n"
        f"👤 User  : *{target_name}* (`{target_id}`)\n"
        f"📅 Expires: `{new_exp.strftime('%d/%m/%Y %H:%M')}`",
        parse_mode="Markdown"
    )


@router.message(Command("admin_revokevip"))
async def cmd_revokevip(message: Message):
    if not await is_admin(message.from_user.id):
        return
    args = message.text.split()[1:]
    if not args:
        await message.answer(
            "❌ Format: `/admin_revokevip [user_id]`",
            parse_mode="Markdown"
        )
        return
    try:
        target_id = int(args[0])
    except ValueError:
        await message.answer("❌ `user_id` harus berupa angka!", parse_mode="Markdown")
        return
    target = await get_user(target_id)
    if not target:
        await message.answer(f"❌ User `{target_id}` tidak ditemukan!", parse_mode="Markdown")
        return
    target_name = target.get("display_name") or target.get("first_name", str(target_id))
    await update_user(target_id, vip_expires_at=None)
    await message.answer(
        f"✅ *VIP dicabut!*\n\n"
        f"👤 User: *{target_name}* (`{target_id}`)\n"
        f"VIP user ini telah dinonaktifkan.",
        parse_mode="Markdown"
    )
