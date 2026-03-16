from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import ORES, ADMIN_IDS, MARKET_FEE_PERCENT, calculate_sell_price, format_kg
from database import (get_user, get_market_listings, get_listing_by_id,
                       buy_market_listing, cancel_market_listing,
                       get_user_market_listings, create_market_listing,
                       remove_ore_from_inventory)
from keyboards import (market_main_kb, market_listing_kb, market_my_listings_kb,
                        ore_inventory_kb, back_main_kb)

router = Router()


class SellOreState(StatesGroup):
    waiting_ore    = State()
    waiting_qty    = State()
    waiting_price  = State()


# ══════════════════════════════════════════════════════════════
# MARKET MENU
# ══════════════════════════════════════════════════════════════
@router.message(F.text == "🛒 Market")
@router.message(Command("market"))
async def show_market(message: Message):
    await message.answer(
        "🛒 *Market Ore*\n\n"
        "Jual beli ore dengan pemain lain!\n"
        f"💡 Biaya listing: *{MARKET_FEE_PERCENT}%* dari total harga jual.",
        reply_markup=market_main_kb(),
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "market_menu")
async def cb_market_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "🛒 *Market Ore*\n\n"
        "Jual beli ore dengan pemain lain!\n"
        f"💡 Biaya listing: *{MARKET_FEE_PERCENT}%* dari total harga jual.",
        reply_markup=market_main_kb(),
        parse_mode="Markdown"
    )
    await callback.answer()


# ══════════════════════════════════════════════════════════════
# LIST SEMUA LISTING
# ══════════════════════════════════════════════════════════════
@router.callback_query(F.data.startswith("market_list_"))
async def cb_market_list(callback: CallbackQuery):
    page = int(callback.data.split("_")[-1])
    listings = await get_market_listings(limit=50)
    if not listings:
        await callback.message.edit_text(
            "🛒 *Market Ore*\n\n📋 Belum ada listing tersedia.\nJadi yang pertama menjual!",
            reply_markup=market_main_kb(),
            parse_mode="Markdown"
        )
        await callback.answer()
        return

    text = (
        f"📋 *Listing Market Aktif ({len(listings)} item)*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Klik untuk membeli:"
    )
    await callback.message.edit_text(
        text,
        reply_markup=market_listing_kb(listings, page),
        parse_mode="Markdown"
    )
    await callback.answer()


# ══════════════════════════════════════════════════════════════
# BELI LISTING
# ══════════════════════════════════════════════════════════════
@router.callback_query(F.data.startswith("market_buy_"))
async def cb_market_buy_detail(callback: CallbackQuery):
    listing_id = int(callback.data.replace("market_buy_", ""))
    listing = await get_listing_by_id(listing_id)
    if not listing or listing["status"] != "active":
        await callback.answer("❌ Listing tidak tersedia!", show_alert=True)
        return

    user = await get_user(callback.from_user.id)
    can_afford = user and user["balance"] >= listing["price_total"]

    seller_tag = f"@{listing['seller_username']}" if listing["seller_username"] else listing["seller_name"]
    ore = ORES.get(listing["ore_type"], {})
    ore_desc = ore.get("desc", "")

    text = (
        f"🛒 *Detail Listing #{listing['id']}*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{listing['ore_emoji']} *{listing['ore_name']}*\n"
        f"   └ _{ore_desc}_\n\n"
        f"📦 Jumlah      : `{listing['quantity']}` buah\n"
        f"💰 Harga/buah  : `{listing['price_each']:,}` koin\n"
        f"💰 Total       : `{listing['price_total']:,}` koin\n\n"
        f"👤 Penjual     : {seller_tag}\n"
        f"🆔 ID Penjual  : `{listing['seller_id']}`\n\n"
        f"{'✅ Kamu punya cukup koin.' if can_afford else '❌ Koin tidak cukup!'}"
    )

    kb_rows = []
    if listing["seller_id"] != callback.from_user.id and can_afford:
        kb_rows.append([
            __import__("aiogram.types", fromlist=["InlineKeyboardButton"]).InlineKeyboardButton(
                text=f"💰 Beli Sekarang ({listing['price_total']:,}🪙)",
                callback_data=f"market_confirm_buy_{listing_id}"
            )
        ])
    elif listing["seller_id"] == callback.from_user.id:
        kb_rows.append([
            __import__("aiogram.types", fromlist=["InlineKeyboardButton"]).InlineKeyboardButton(
                text="❌ Batalkan Listing Ini",
                callback_data=f"market_cancel_{listing_id}"
            )
        ])
    kb_rows.append([
        __import__("aiogram.types", fromlist=["InlineKeyboardButton"]).InlineKeyboardButton(
            text="🔙 Kembali", callback_data="market_list_0"
        )
    ])
    from aiogram.types import InlineKeyboardMarkup
    kb = InlineKeyboardMarkup(inline_keyboard=kb_rows)

    await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data.startswith("market_confirm_buy_"))
async def cb_market_confirm_buy(callback: CallbackQuery):
    listing_id = int(callback.data.replace("market_confirm_buy_", ""))
    buyer_username = callback.from_user.username or callback.from_user.first_name

    ok, msg, listing = await buy_market_listing(listing_id, callback.from_user.id, buyer_username)
    if ok:
        seller_tag = f"@{listing['seller_username']}" if listing["seller_username"] else listing["seller_name"]
        fee = int(listing["price_total"] * MARKET_FEE_PERCENT / 100)
        seller_gets = listing["price_total"] - fee
        full_msg = (
            f"✅ *Pembelian Berhasil!*\n\n"
            f"{listing['ore_emoji']} *{listing['ore_name']}* x{listing['quantity']}\n\n"
            f"💰 Dibayar     : `{listing['price_total']:,}` koin\n"
            f"📦 Ore masuk ke inventaris ore-mu!\n\n"
            f"👤 Penjual     : {seller_tag}\n"
            f"🆔 ID Penjual  : `{listing['seller_id']}`\n"
            f"🆔 ID Kamu     : `{callback.from_user.id}`"
        )
        await callback.answer("✅ Berhasil dibeli!", show_alert=True)
        await callback.message.edit_text(full_msg, reply_markup=back_main_kb(), parse_mode="Markdown")

        # Notifikasi ke penjual
        try:
            buyer_tag = f"@{buyer_username}" if callback.from_user.username else f"ID:{callback.from_user.id}"
            await callback.bot.send_message(
                listing["seller_id"],
                f"💰 *Ore kamu terjual!*\n\n"
                f"{listing['ore_emoji']} *{listing['ore_name']}* x{listing['quantity']}\n"
                f"💰 Kamu dapat: `{seller_gets:,}` koin (setelah fee {MARKET_FEE_PERCENT}%)\n"
                f"👤 Pembeli: {buyer_tag}\n"
                f"🆔 ID Pembeli: `{callback.from_user.id}`",
                parse_mode="Markdown"
            )
        except Exception:
            pass
    else:
        await callback.answer(msg, show_alert=True)


# ══════════════════════════════════════════════════════════════
# JUAL ORE
# ══════════════════════════════════════════════════════════════
@router.callback_query(F.data == "market_sell")
async def cb_market_sell(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.answer("Ketik /start!")
        return
    ore_inv = user.get("ore_inventory", {})
    ore_inv = {k: v for k, v in ore_inv.items() if v > 0}

    if not ore_inv:
        await callback.message.edit_text(
            "📦 *Inventory Ore Kosong!*\n\nMulai mining untuk mendapatkan ore.",
            reply_markup=back_main_kb(),
            parse_mode="Markdown"
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        "💰 *Jual Ore ke Market*\n\n"
        "Pilih ore yang ingin dijual:",
        reply_markup=ore_inventory_kb(ore_inv),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("sell_ore_"))
async def cb_sell_ore_select(callback: CallbackQuery, state: FSMContext):
    ore_id = callback.data.replace("sell_ore_", "")
    ore = ORES.get(ore_id)
    user = await get_user(callback.from_user.id)
    if not ore or not user:
        await callback.answer("❌ Ore tidak ditemukan!")
        return

    qty_have = user.get("ore_inventory", {}).get(ore_id, 0)
    await state.set_state(SellOreState.waiting_qty)
    await state.update_data(ore_id=ore_id, ore_name=ore["name"],
                             ore_emoji=ore["emoji"], qty_have=qty_have)

    await callback.message.edit_text(
        f"💰 *Jual {ore['emoji']} {ore['name']}*\n\n"
        f"📦 Kamu punya: `{qty_have}` buah\n"
        f"💡 Nilai dasar: `{ore['value']:,}` koin/buah\n\n"
        f"Ketik jumlah yang ingin dijual (1 - {qty_have}):",
        reply_markup=back_main_kb(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.message(SellOreState.waiting_qty)
async def process_sell_qty(message: Message, state: FSMContext):
    try:
        qty = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Masukkan angka yang valid!")
        return

    data = await state.get_data()
    if qty <= 0 or qty > data["qty_have"]:
        await message.answer(f"❌ Jumlah harus antara 1 dan {data['qty_have']}!")
        return

    await state.update_data(qty=qty)
    await state.set_state(SellOreState.waiting_price)

    ore = ORES.get(data["ore_id"], {})
    # Harga berdasarkan KG
    kg_min = ore.get("kg_min", 0.5)
    kg_max = ore.get("kg_max", 2.0)
    kg_avg = (kg_min + kg_max) / 2
    suggest_per = calculate_sell_price(data["ore_id"], kg_avg)
    suggest = suggest_per * qty
    await message.answer(
        f"💰 Jual *{qty}x {data['ore_emoji']} {data['ore_name']}*\n\n"
        f"⚖️ Berat rata-rata: `{format_kg(kg_avg)}` /buah\n"
        f"💡 Harga per buah (est.): `{suggest_per:,}` koin\n"
        f"💡 Harga total disarankan: `{suggest:,}` koin\n\n"
        f"Ketik *total harga jual* dalam koin:",
        parse_mode="Markdown"
    )


@router.message(SellOreState.waiting_price)
async def process_sell_price(message: Message, state: FSMContext):
    try:
        price_total = int(message.text.strip().replace(".", "").replace(",", ""))
    except ValueError:
        await message.answer("❌ Masukkan angka yang valid!")
        return

    if price_total <= 0:
        await message.answer("❌ Harga harus lebih dari 0!")
        return

    data = await state.get_data()
    qty = data["qty"]
    price_each = price_total // qty
    fee = int(price_total * MARKET_FEE_PERCENT / 100)
    seller_gets = price_total - fee

    # Kurangi ore dari inventory
    removed = await remove_ore_from_inventory(message.from_user.id, data["ore_id"], qty)
    if not removed:
        await message.answer("❌ Ore tidak cukup di inventory!")
        await state.clear()
        return

    # Buat listing
    user = await get_user(message.from_user.id)
    username = message.from_user.username or ""
    fname = message.from_user.first_name or "Miner"

    listing_id = await create_market_listing(
        seller_id=message.from_user.id,
        seller_username=username,
        seller_name=fname,
        ore_type=data["ore_id"],
        ore_name=data["ore_name"],
        ore_emoji=data["ore_emoji"],
        quantity=qty,
        price_each=price_each
    )

    await state.clear()

    # Achievement first market
    from game import _grant_if_new
    await _grant_if_new(message.from_user.id, "market_first")

    await message.answer(
        f"✅ *Listing Berhasil Dibuat!*\n\n"
        f"{data['ore_emoji']} *{data['ore_name']}* x{qty}\n"
        f"💰 Harga/buah : `{price_each:,}` koin\n"
        f"💰 Total      : `{price_total:,}` koin\n"
        f"🏷️ Fee ({MARKET_FEE_PERCENT}%)  : `{fee:,}` koin\n"
        f"💵 Kamu dapat : `{seller_gets:,}` koin (setelah terjual)\n\n"
        f"🆔 Listing ID : `#{listing_id}`\n"
        f"🆔 ID Kamu    : `{message.from_user.id}`\n\n"
        f"Listing aktif di market!",
        reply_markup=market_main_kb(),
        parse_mode="Markdown"
    )


# ══════════════════════════════════════════════════════════════
# LISTING SAYA
# ══════════════════════════════════════════════════════════════
@router.callback_query(F.data == "market_my_listings")
async def cb_my_listings(callback: CallbackQuery):
    listings = await get_user_market_listings(callback.from_user.id)
    text = (
        f"📦 *Listing Aktif Kamu ({len(listings)})*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Klik untuk membatalkan:"
    )
    await callback.message.edit_text(
        text,
        reply_markup=market_my_listings_kb(listings),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("market_cancel_"))
async def cb_market_cancel(callback: CallbackQuery):
    listing_id = int(callback.data.replace("market_cancel_", ""))
    ok, msg = await cancel_market_listing(listing_id, callback.from_user.id)
    await callback.answer(msg[:200], show_alert=True)
    if ok:
        listings = await get_user_market_listings(callback.from_user.id)
        await callback.message.edit_text(
            f"📦 *Listing Aktif Kamu ({len(listings)})*",
            reply_markup=market_my_listings_kb(listings),
            parse_mode="Markdown"
        )
