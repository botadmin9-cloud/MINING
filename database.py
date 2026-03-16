import aiosqlite
import json
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

DB_PATH = "mining_bot.db"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript("""
        PRAGMA journal_mode=WAL;

        CREATE TABLE IF NOT EXISTS users (
            user_id         INTEGER PRIMARY KEY,
            username        TEXT    DEFAULT '',
            first_name      TEXT    DEFAULT '',
            balance         INTEGER DEFAULT 500,
            total_earned    INTEGER DEFAULT 0,
            total_mined     INTEGER DEFAULT 0,
            mine_count      INTEGER DEFAULT 0,
            energy          INTEGER DEFAULT 500,
            max_energy      INTEGER DEFAULT 500,
            bag_slots       INTEGER DEFAULT 50,
            level           INTEGER DEFAULT 1,
            xp              INTEGER DEFAULT 0,
            rebirth_count   INTEGER DEFAULT 0,
            perm_coin_mult  REAL    DEFAULT 1.0,
            current_tool    TEXT    DEFAULT 'stone_pick',
            current_zone    TEXT    DEFAULT 'surface',
            owned_tools     TEXT    DEFAULT '["stone_pick"]',
            unlocked_zones  TEXT    DEFAULT '["surface"]',
            inventory       TEXT    DEFAULT '{}',
            active_buffs    TEXT    DEFAULT '{}',
            achievements    TEXT    DEFAULT '[]',
            ore_inventory   TEXT    DEFAULT '{}',
            favorite_ores   TEXT    DEFAULT '[]',
            museum_ores     TEXT    DEFAULT '[]',
            daily_streak    INTEGER DEFAULT 0,
            last_daily      TEXT    DEFAULT NULL,
            last_energy_regen TEXT  DEFAULT NULL,
            last_mine_time  TEXT    DEFAULT NULL,
            last_auto_mine  TEXT    DEFAULT NULL,
            bag_kg_used     REAL    DEFAULT 0.0,
            bag_kg_max      REAL    DEFAULT 100.0,
            total_kg_mined  REAL    DEFAULT 0.0,
            perm_xp_mult    REAL    DEFAULT 1.0,
            ore_kg_data     TEXT    DEFAULT '{}',
            created_at      TEXT    DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS mining_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            tool_id     TEXT,
            tool_name   TEXT,
            zone        TEXT,
            ore_type    TEXT,
            ore_name    TEXT,
            coins       INTEGER,
            xp_gained   INTEGER,
            is_crit     INTEGER DEFAULT 0,
            is_lucky    INTEGER DEFAULT 0,
            special_hit TEXT    DEFAULT NULL,
            mined_at    TEXT    DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        );

        CREATE TABLE IF NOT EXISTS transactions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER,
            type        TEXT,
            amount      INTEGER,
            description TEXT,
            created_at  TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS market_listings (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            seller_id       INTEGER NOT NULL,
            seller_username TEXT    DEFAULT '',
            seller_name     TEXT    DEFAULT '',
            ore_type        TEXT    NOT NULL,
            ore_name        TEXT    NOT NULL,
            ore_emoji       TEXT    DEFAULT '',
            quantity        INTEGER NOT NULL,
            price_each      INTEGER NOT NULL,
            price_total     INTEGER NOT NULL,
            status          TEXT    DEFAULT 'active',
            buyer_id        INTEGER DEFAULT NULL,
            buyer_username  TEXT    DEFAULT '',
            listed_at       TEXT    DEFAULT CURRENT_TIMESTAMP,
            sold_at         TEXT    DEFAULT NULL
        );

        CREATE TABLE IF NOT EXISTS admin_photos (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_id    INTEGER NOT NULL,
            photo_id    TEXT    NOT NULL,
            caption     TEXT    DEFAULT '',
            uploaded_at TEXT    DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS ore_photos (
            ore_id      TEXT    PRIMARY KEY,
            photo_id    TEXT    NOT NULL,
            caption     TEXT    DEFAULT '',
            set_by      INTEGER NOT NULL,
            updated_at  TEXT    DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_mining_user   ON mining_log(user_id);
        CREATE INDEX IF NOT EXISTS idx_mining_ore    ON mining_log(ore_type);
        CREATE INDEX IF NOT EXISTS idx_users_total   ON users(total_mined);
        CREATE INDEX IF NOT EXISTS idx_market_status ON market_listings(status);
        CREATE INDEX IF NOT EXISTS idx_market_seller ON market_listings(seller_id);
        """)
        # Migration: tambah kolom baru jika belum ada
        for col_sql in [
            "ALTER TABLE users ADD COLUMN ore_inventory TEXT DEFAULT '{}'",
            "ALTER TABLE users ADD COLUMN last_mine_time TEXT DEFAULT NULL",
            "ALTER TABLE users ADD COLUMN bag_slots INTEGER DEFAULT 50",
            "ALTER TABLE users ADD COLUMN favorite_ores TEXT DEFAULT '[]'",
            "ALTER TABLE users ADD COLUMN museum_ores TEXT DEFAULT '[]'",
            "ALTER TABLE users ADD COLUMN bag_kg_used REAL DEFAULT 0.0",
            "ALTER TABLE users ADD COLUMN bag_kg_max REAL DEFAULT 100.0",
            "ALTER TABLE users ADD COLUMN total_kg_mined REAL DEFAULT 0.0",
            "ALTER TABLE users ADD COLUMN perm_xp_mult REAL DEFAULT 1.0",
            "ALTER TABLE users ADD COLUMN ore_kg_data TEXT DEFAULT '{}'",
        ]:
            try:
                await db.execute(col_sql)
            except Exception:
                pass
        await db.commit()
    logger.info("✅ DB initialized (v2)")


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────
def _loads(val, default):
    try:
        return json.loads(val) if val else default
    except Exception:
        return default


def _row_to_user(row) -> dict:
    d = dict(row)
    d["owned_tools"]    = _loads(d.get("owned_tools"),    ["stone_pick"])
    d["unlocked_zones"] = _loads(d.get("unlocked_zones"), ["surface"])
    d["inventory"]      = _loads(d.get("inventory"),      {})
    d["active_buffs"]   = _loads(d.get("active_buffs"),   {})
    d["achievements"]   = _loads(d.get("achievements"),   [])
    d["ore_inventory"]  = _loads(d.get("ore_inventory"),  {})
    d["favorite_ores"]  = _loads(d.get("favorite_ores"),  [])
    d["museum_ores"]    = _loads(d.get("museum_ores"),     [])
    d["ore_kg_data"]    = _loads(d.get("ore_kg_data"),     {})
    if "bag_slots" not in d or d["bag_slots"] is None:
        d["bag_slots"] = 50
    if "bag_kg_max" not in d or d["bag_kg_max"] is None:
        d["bag_kg_max"] = 100.0
    if "bag_kg_used" not in d or d["bag_kg_used"] is None:
        d["bag_kg_used"] = 0.0
    if "total_kg_mined" not in d or d["total_kg_mined"] is None:
        d["total_kg_mined"] = 0.0
    if "perm_xp_mult" not in d or d["perm_xp_mult"] is None:
        d["perm_xp_mult"] = 1.0
    return d


# ─────────────────────────────────────────────────────────────
# USER CRUD
# ─────────────────────────────────────────────────────────────
async def get_user(user_id: int) -> Optional[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE user_id=?", (user_id,)) as cur:
            row = await cur.fetchone()
            return _row_to_user(row) if row else None


async def create_user(user_id: int, username: str, first_name: str) -> dict:
    from config import STARTING_BALANCE
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT OR IGNORE INTO users
               (user_id, username, first_name, balance)
               VALUES (?,?,?,?)""",
            (user_id, username or "", first_name or "Miner", STARTING_BALANCE)
        )
        await db.commit()
    return await get_user(user_id)


async def update_user(user_id: int, **kwargs):
    if not kwargs:
        return
    for key in ("owned_tools", "unlocked_zones", "inventory",
                "active_buffs", "achievements", "ore_inventory",
                "favorite_ores", "museum_ores", "ore_kg_data"):
        if key in kwargs:
            kwargs[key] = json.dumps(kwargs[key], ensure_ascii=False)
    cols = ", ".join(f"{k}=?" for k in kwargs)
    vals = list(kwargs.values()) + [user_id]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE users SET {cols} WHERE user_id=?", vals)
        await db.commit()


async def add_balance(user_id: int, amount: int, desc: str = ""):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET balance=balance+?, total_earned=total_earned+? WHERE user_id=?",
            (amount, max(0, amount), user_id)
        )
        if desc:
            await db.execute(
                "INSERT INTO transactions(user_id,type,amount,description) VALUES(?,?,?,?)",
                (user_id, "credit" if amount >= 0 else "debit", amount, desc)
            )
        await db.commit()


async def add_ore_to_inventory(user_id: int, ore_id: str, qty: int = 1, kg: float = 0.0):
    """Tambah ore ke ore_inventory user. kg = berat ore yang ditambahkan."""
    user = await get_user(user_id)
    if not user:
        return
    ore_inv = user.get("ore_inventory", {})
    ore_inv[ore_id] = ore_inv.get(ore_id, 0) + qty
    # Simpan data KG per ore type (akumulatif total kg)
    ore_kg_data = user.get("ore_kg_data", {})
    if kg > 0:
        ore_kg_data[ore_id] = round(ore_kg_data.get(ore_id, 0.0) + kg, 2)
    await update_user(user_id, ore_inventory=ore_inv, ore_kg_data=ore_kg_data)


async def remove_ore_from_inventory(user_id: int, ore_id: str, qty: int) -> bool:
    """Hapus ore dari ore_inventory user. Return False jika tidak cukup."""
    user = await get_user(user_id)
    if not user:
        return False
    ore_inv = user.get("ore_inventory", {})
    if ore_inv.get(ore_id, 0) < qty:
        return False
    ore_inv[ore_id] -= qty
    if ore_inv[ore_id] <= 0:
        del ore_inv[ore_id]
    await update_user(user_id, ore_inventory=ore_inv)
    return True


# ─────────────────────────────────────────────────────────────
# MINING LOG
# ─────────────────────────────────────────────────────────────
async def log_mine(user_id: int, tool_id: str, tool_name: str, zone: str,
                   ore_type: str, ore_name: str, coins: int, xp: int,
                   is_crit: bool = False, is_lucky: bool = False,
                   special: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO mining_log
               (user_id,tool_id,tool_name,zone,ore_type,ore_name,coins,xp_gained,is_crit,is_lucky,special_hit)
               VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
            (user_id, tool_id, tool_name, zone, ore_type, ore_name,
             coins, xp, int(is_crit), int(is_lucky), special)
        )
        await db.execute(
            "UPDATE users SET total_mined=total_mined+?, mine_count=mine_count+1 WHERE user_id=?",
            (coins, user_id)
        )
        await db.commit()


# ─────────────────────────────────────────────────────────────
# MARKET
# ─────────────────────────────────────────────────────────────
async def create_market_listing(seller_id: int, seller_username: str, seller_name: str,
                                  ore_type: str, ore_name: str, ore_emoji: str,
                                  quantity: int, price_each: int) -> int:
    price_total = price_each * quantity
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            """INSERT INTO market_listings
               (seller_id, seller_username, seller_name, ore_type, ore_name, ore_emoji,
                quantity, price_each, price_total, status)
               VALUES (?,?,?,?,?,?,?,?,?,'active')""",
            (seller_id, seller_username, seller_name, ore_type, ore_name, ore_emoji,
             quantity, price_each, price_total)
        )
        await db.commit()
        return cur.lastrowid


async def get_market_listings(ore_type: str = None, limit: int = 20) -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if ore_type:
            async with db.execute(
                "SELECT * FROM market_listings WHERE status='active' AND ore_type=? ORDER BY price_each ASC LIMIT ?",
                (ore_type, limit)
            ) as cur:
                return [dict(r) for r in await cur.fetchall()]
        else:
            async with db.execute(
                "SELECT * FROM market_listings WHERE status='active' ORDER BY listed_at DESC LIMIT ?",
                (limit,)
            ) as cur:
                return [dict(r) for r in await cur.fetchall()]


async def get_listing_by_id(listing_id: int) -> Optional[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM market_listings WHERE id=?", (listing_id,)) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def buy_market_listing(listing_id: int, buyer_id: int, buyer_username: str) -> tuple:
    """Return (ok, msg, listing)"""
    listing = await get_listing_by_id(listing_id)
    if not listing:
        return False, "❌ Listing tidak ditemukan!", None
    if listing["status"] != "active":
        return False, "❌ Listing sudah tidak aktif!", None
    if listing["seller_id"] == buyer_id:
        return False, "❌ Kamu tidak bisa membeli barangmu sendiri!", None

    buyer = await get_user(buyer_id)
    if not buyer:
        return False, "❌ User tidak ditemukan!", None
    if buyer["balance"] < listing["price_total"]:
        return False, f"❌ Koin tidak cukup! Butuh `{listing['price_total']:,}` koin.", None

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE market_listings SET status='sold', buyer_id=?, buyer_username=?, sold_at=? WHERE id=?",
            (buyer_id, buyer_username, datetime.now().isoformat(), listing_id)
        )
        await db.commit()

    # Kurangi balance buyer
    await add_balance(buyer_id, -listing["price_total"], f"Beli ore dari market #{listing_id}")
    # Tambah ore ke buyer
    await add_ore_to_inventory(buyer_id, listing["ore_type"], listing["quantity"])
    # Tambah koin ke seller
    fee = int(listing["price_total"] * 0.05)
    seller_gets = listing["price_total"] - fee
    await add_balance(listing["seller_id"], seller_gets, f"Jual ore via market #{listing_id}")

    return True, f"✅ Berhasil membeli!", listing


async def cancel_market_listing(listing_id: int, user_id: int) -> tuple:
    """Cancel listing dan kembalikan ore ke seller."""
    listing = await get_listing_by_id(listing_id)
    if not listing:
        return False, "❌ Listing tidak ditemukan!"
    if listing["seller_id"] != user_id:
        return False, "❌ Bukan listing milikmu!"
    if listing["status"] != "active":
        return False, "❌ Listing sudah tidak aktif!"

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE market_listings SET status='cancelled' WHERE id=?",
            (listing_id,)
        )
        await db.commit()

    # Kembalikan ore
    await add_ore_to_inventory(user_id, listing["ore_type"], listing["quantity"])
    return True, f"✅ Listing dibatalkan, ore dikembalikan."


async def get_user_market_listings(user_id: int) -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM market_listings WHERE seller_id=? AND status='active' ORDER BY listed_at DESC",
            (user_id,)
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]


# ─────────────────────────────────────────────────────────────
# ADMIN PHOTOS
# ─────────────────────────────────────────────────────────────
async def save_admin_photo(admin_id: int, photo_id: str, caption: str = "") -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO admin_photos (admin_id, photo_id, caption) VALUES (?,?,?)",
            (admin_id, photo_id, caption)
        )
        await db.commit()
    return True


async def get_admin_photos(admin_id: int = None) -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if admin_id:
            async with db.execute(
                "SELECT * FROM admin_photos WHERE admin_id=? ORDER BY uploaded_at DESC",
                (admin_id,)
            ) as cur:
                return [dict(r) for r in await cur.fetchall()]
        else:
            async with db.execute(
                "SELECT * FROM admin_photos ORDER BY uploaded_at DESC"
            ) as cur:
                return [dict(r) for r in await cur.fetchall()]


async def delete_admin_photo(photo_db_id: int, admin_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "DELETE FROM admin_photos WHERE id=? AND admin_id=?",
            (photo_db_id, admin_id)
        )
        await db.commit()
    return True


# ─────────────────────────────────────────────────────────────
# LEADERBOARD & STATS
# ─────────────────────────────────────────────────────────────
async def get_leaderboard(limit: int = 10) -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT user_id,username,first_name,total_mined,level,rebirth_count "
            "FROM users ORDER BY total_mined DESC LIMIT ?", (limit,)
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]


async def get_user_rank(user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT COUNT(*) FROM users WHERE total_mined>"
            "(SELECT total_mined FROM users WHERE user_id=?)", (user_id,)
        ) as cur:
            row = await cur.fetchone()
            return (row[0] + 1) if row else 999


async def get_ore_stats(user_id: int) -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT ore_type,ore_name,COUNT(*) as cnt,SUM(coins) as total "
            "FROM mining_log WHERE user_id=? GROUP BY ore_type ORDER BY total DESC",
            (user_id,)
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]


async def get_all_users() -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT user_id,username,first_name,balance,level,total_mined FROM users") as cur:
            return [dict(r) for r in await cur.fetchall()]


async def get_total_users() -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cur:
            row = await cur.fetchone()
            return row[0] if row else 0


# ─────────────────────────────────────────────────────────────
# ORE PHOTOS (foto per jenis ore, dipasang admin)
# ─────────────────────────────────────────────────────────────
async def set_ore_photo(ore_id: str, photo_id: str, caption: str, admin_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO ore_photos (ore_id, photo_id, caption, set_by, updated_at)
               VALUES (?,?,?,?,?)
               ON CONFLICT(ore_id) DO UPDATE SET
                 photo_id=excluded.photo_id,
                 caption=excluded.caption,
                 set_by=excluded.set_by,
                 updated_at=excluded.updated_at""",
            (ore_id, photo_id, caption, admin_id, datetime.now().isoformat())
        )
        await db.commit()
    return True


async def get_ore_photo(ore_id: str) -> Optional[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM ore_photos WHERE ore_id=?", (ore_id,)) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def get_all_ore_photos() -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM ore_photos ORDER BY ore_id") as cur:
            return [dict(r) for r in await cur.fetchall()]


async def delete_ore_photo(ore_id: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM ore_photos WHERE ore_id=?", (ore_id,))
        await db.commit()
    return True
