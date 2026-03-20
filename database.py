import aiosqlite
import json
import logging
from datetime import datetime, timedelta
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
            display_name    TEXT    DEFAULT '',
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
            bag_kg_max      REAL    DEFAULT 999999.0,
            total_kg_mined  REAL    DEFAULT 0.0,
            perm_xp_mult    REAL    DEFAULT 1.0,
            ore_kg_data     TEXT    DEFAULT '{}',
            created_at      TEXT    DEFAULT CURRENT_TIMESTAMP,
            vip_expires_at  TEXT    DEFAULT NULL,
            vip_type        TEXT    DEFAULT NULL,
            transfer_send_count INTEGER DEFAULT 0,
            transfer_receive_count INTEGER DEFAULT 0,
            transfer_week_start TEXT DEFAULT NULL,
            last_name_change TEXT DEFAULT NULL,
            is_mining_multi INTEGER DEFAULT 0,
            mining_multi_type TEXT DEFAULT NULL,
            mining_multi_started TEXT DEFAULT NULL
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

        CREATE TABLE IF NOT EXISTS market_daily_count (
            user_id     INTEGER NOT NULL,
            list_date   TEXT    NOT NULL,
            count       INTEGER DEFAULT 0,
            PRIMARY KEY(user_id, list_date)
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

        CREATE TABLE IF NOT EXISTS tool_photos (
            tool_id     TEXT    PRIMARY KEY,
            photo_id    TEXT    NOT NULL,
            caption     TEXT    DEFAULT '',
            set_by      INTEGER NOT NULL,
            updated_at  TEXT    DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS zone_photos (
            zone_id     TEXT    PRIMARY KEY,
            photo_id    TEXT    NOT NULL,
            caption     TEXT    DEFAULT '',
            set_by      INTEGER NOT NULL,
            updated_at  TEXT    DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS leaderboard_weekly (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            display_name TEXT   DEFAULT '',
            balance     INTEGER DEFAULT 0,
            mine_count  INTEGER DEFAULT 0,
            total_kg    REAL    DEFAULT 0.0,
            ore_count   INTEGER DEFAULT 0,
            week_start  TEXT    NOT NULL,
            week_end    TEXT    DEFAULT NULL,
            rank_balance INTEGER DEFAULT 0,
            rank_mine   INTEGER DEFAULT 0,
            rank_kg     INTEGER DEFAULT 0,
            rank_ore    INTEGER DEFAULT 0,
            rewarded    INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS leaderboard_monthly (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            display_name TEXT   DEFAULT '',
            balance     INTEGER DEFAULT 0,
            mine_count  INTEGER DEFAULT 0,
            total_kg    REAL    DEFAULT 0.0,
            ore_count   INTEGER DEFAULT 0,
            month_start TEXT    NOT NULL,
            month_end   TEXT    DEFAULT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_mining_user   ON mining_log(user_id);
        CREATE INDEX IF NOT EXISTS idx_mining_ore    ON mining_log(ore_type);
        CREATE INDEX IF NOT EXISTS idx_users_total   ON users(total_mined);
        CREATE INDEX IF NOT EXISTS idx_market_status ON market_listings(status);
        CREATE INDEX IF NOT EXISTS idx_market_seller ON market_listings(seller_id);
        """)
        # Safe migration
        migrations = [
            "ALTER TABLE users ADD COLUMN ore_inventory TEXT DEFAULT '{}'",
            "ALTER TABLE users ADD COLUMN last_mine_time TEXT DEFAULT NULL",
            "ALTER TABLE users ADD COLUMN bag_slots INTEGER DEFAULT 50",
            "ALTER TABLE users ADD COLUMN favorite_ores TEXT DEFAULT '[]'",
            "ALTER TABLE users ADD COLUMN museum_ores TEXT DEFAULT '[]'",
            "ALTER TABLE users ADD COLUMN bag_kg_used REAL DEFAULT 0.0",
            "ALTER TABLE users ADD COLUMN bag_kg_max REAL DEFAULT 999999.0",
            "ALTER TABLE users ADD COLUMN total_kg_mined REAL DEFAULT 0.0",
            "ALTER TABLE users ADD COLUMN perm_xp_mult REAL DEFAULT 1.0",
            "ALTER TABLE users ADD COLUMN ore_kg_data TEXT DEFAULT '{}'",
            "ALTER TABLE users ADD COLUMN display_name TEXT DEFAULT ''",
            "ALTER TABLE users ADD COLUMN transfer_send_count INTEGER DEFAULT 0",
            "ALTER TABLE users ADD COLUMN transfer_receive_count INTEGER DEFAULT 0",
            "ALTER TABLE users ADD COLUMN transfer_week_start TEXT DEFAULT NULL",
            "ALTER TABLE users ADD COLUMN last_name_change TEXT DEFAULT NULL",
            "ALTER TABLE users ADD COLUMN is_mining_multi INTEGER DEFAULT 0",
            "ALTER TABLE users ADD COLUMN mining_multi_type TEXT DEFAULT NULL",
            "ALTER TABLE users ADD COLUMN mining_multi_started TEXT DEFAULT NULL",
        ]
        for col_sql in migrations:
            try:
                await db.execute(col_sql)
            except Exception:
                pass
        await db.execute("UPDATE users SET bag_kg_max=999999.0 WHERE bag_kg_max < 999999.0")
        await db.commit()
    logger.info("✅ DB initialized (v6)")


def _loads(val, default):
    try:
        return json.loads(val) if val else default
    except Exception:
        return default


def _row_to_user(row) -> dict:
    keys = [
        "user_id","username","first_name","display_name","balance",
        "total_earned","total_mined","mine_count","energy","max_energy",
        "bag_slots","level","xp","rebirth_count","perm_coin_mult",
        "current_tool","current_zone","owned_tools","unlocked_zones",
        "inventory","active_buffs","achievements","ore_inventory",
        "favorite_ores","museum_ores","daily_streak","last_daily",
        "last_energy_regen","last_mine_time","last_auto_mine",
        "bag_kg_used","bag_kg_max","total_kg_mined","perm_xp_mult",
        "ore_kg_data","created_at","vip_expires_at","vip_type",
        "transfer_send_count","transfer_receive_count","transfer_week_start",
        "last_name_change","is_mining_multi","mining_multi_type","mining_multi_started",
    ]
    d = dict(zip(keys, row))
    d["owned_tools"]    = _loads(d.get("owned_tools"),   ["stone_pick"])
    d["unlocked_zones"] = _loads(d.get("unlocked_zones"), ["surface"])
    d["inventory"]      = _loads(d.get("inventory"),      {})
    d["active_buffs"]   = _loads(d.get("active_buffs"),   {})
    d["achievements"]   = _loads(d.get("achievements"),   [])
    d["ore_inventory"]  = _loads(d.get("ore_inventory"),  {})
    d["favorite_ores"]  = _loads(d.get("favorite_ores"),  [])
    d["museum_ores"]    = _loads(d.get("museum_ores"),    [])
    d["ore_kg_data"]    = _loads(d.get("ore_kg_data"),    {})
    d["is_mining_multi"] = bool(d.get("is_mining_multi", 0))
    return d


async def get_user(user_id: int) -> Optional[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT * FROM users WHERE user_id=?", (user_id,)) as cur:
            row = await cur.fetchone()
            return _row_to_user(row) if row else None


async def create_user(user_id: int, username: str, first_name: str,
                      display_name: str = "") -> dict:
    from config import STARTING_BALANCE
    display_name = display_name or first_name
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT OR IGNORE INTO users
               (user_id, username, first_name, display_name, balance)
               VALUES (?,?,?,?,?)""",
            (user_id, username, first_name, display_name, STARTING_BALANCE)
        )
        await db.commit()
    return await get_user(user_id)


async def update_user(user_id: int, **kwargs):
    if not kwargs:
        return
    json_fields = {"owned_tools","unlocked_zones","inventory","active_buffs",
                   "achievements","ore_inventory","favorite_ores","museum_ores","ore_kg_data"}
    sets, vals = [], []
    for k, v in kwargs.items():
        sets.append(f"{k}=?")
        vals.append(json.dumps(v) if k in json_fields else v)
    vals.append(user_id)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE users SET {','.join(sets)} WHERE user_id=?", vals)
        await db.commit()


async def add_balance(user_id: int, amount: int, desc: str = ""):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET balance=balance+? WHERE user_id=?", (amount, user_id))
        if amount > 0:
            await db.execute(
                "UPDATE users SET total_earned=total_earned+? WHERE user_id=?",
                (amount, user_id)
            )
        await db.execute(
            "INSERT INTO transactions(user_id,type,amount,description) VALUES(?,?,?,?)",
            (user_id, "credit" if amount >= 0 else "debit", abs(amount), desc)
        )
        await db.commit()


async def add_ore_to_inventory(user_id: int, ore_id: str, qty: int = 1, kg: float = 0.0):
    user = await get_user(user_id)
    if not user:
        return
    inv = user.get("ore_inventory", {})
    inv[ore_id] = inv.get(ore_id, 0) + qty
    kg_data = user.get("ore_kg_data", {})
    kg_data[ore_id] = kg_data.get(ore_id, 0.0) + kg
    bag_kg_used = user.get("bag_kg_used", 0.0) + kg
    mine_count = user.get("mine_count", 0) + 1
    total_mined = user.get("total_mined", 0) + 1
    await update_user(user_id, ore_inventory=inv, ore_kg_data=kg_data,
                      bag_kg_used=bag_kg_used, mine_count=mine_count, total_mined=total_mined)


async def remove_ore_from_inventory(user_id: int, ore_id: str, qty: int) -> bool:
    user = await get_user(user_id)
    if not user:
        return False
    inv = user.get("ore_inventory", {})
    if inv.get(ore_id, 0) < qty:
        return False
    inv[ore_id] -= qty
    if inv[ore_id] <= 0:
        del inv[ore_id]
    kg_data = user.get("ore_kg_data", {})
    if ore_id in kg_data and inv.get(ore_id, 0) == 0:
        removed_kg = kg_data.pop(ore_id, 0.0)
    elif ore_id in kg_data:
        old_qty = inv.get(ore_id, 0) + qty
        if old_qty > 0:
            per_kg = kg_data[ore_id] / old_qty
            kg_data[ore_id] = per_kg * inv.get(ore_id, 0)
            removed_kg = per_kg * qty
        else:
            removed_kg = 0.0
    else:
        removed_kg = 0.0
    bag_kg_used = max(0.0, user.get("bag_kg_used", 0.0) - removed_kg)
    await update_user(user_id, ore_inventory=inv, ore_kg_data=kg_data, bag_kg_used=bag_kg_used)
    return True


async def log_mine(user_id: int, tool_id: str, tool_name: str, zone: str,
                   ore_type: str, ore_name: str, coins: int, xp_gained: int,
                   is_crit: bool = False, is_lucky: bool = False, special_hit: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO mining_log
               (user_id,tool_id,tool_name,zone,ore_type,ore_name,coins,xp_gained,is_crit,is_lucky,special_hit)
               VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
            (user_id, tool_id, tool_name, zone, ore_type, ore_name,
             coins, xp_gained, int(is_crit), int(is_lucky), special_hit)
        )
        await db.commit()


async def create_market_listing(seller_id: int, seller_username: str, seller_name: str,
                                 ore_type: str, ore_name: str, ore_emoji: str,
                                 quantity: int, price_each: int) -> Optional[int]:
    price_total = price_each * quantity
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            """INSERT INTO market_listings
               (seller_id,seller_username,seller_name,ore_type,ore_name,ore_emoji,quantity,price_each,price_total)
               VALUES(?,?,?,?,?,?,?,?,?)""",
            (seller_id, seller_username, seller_name, ore_type, ore_name,
             ore_emoji, quantity, price_each, price_total)
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
    listing = await get_listing_by_id(listing_id)
    if not listing:
        return False, "❌ Listing tidak ditemukan."
    if listing["status"] != "active":
        return False, "❌ Listing sudah tidak tersedia."
    if listing["seller_id"] == buyer_id:
        return False, "❌ Tidak bisa membeli listing sendiri."
    buyer = await get_user(buyer_id)
    if not buyer:
        return False, "❌ User tidak ditemukan."
    if buyer["balance"] < listing["price_total"]:
        return False, f"❌ Saldo tidak cukup. Butuh `{listing['price_total']:,}` koin."

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE market_listings SET status='sold', buyer_id=?, buyer_username=?, sold_at=? WHERE id=?",
            (buyer_id, buyer_username, datetime.now().isoformat(), listing_id)
        )
        await db.commit()

    # Transfer coin & ore
    await add_balance(buyer_id, -listing["price_total"], f"Beli {listing['ore_name']} dari market")
    seller_earn = int(listing["price_total"] * 0.95)
    await add_balance(listing["seller_id"], seller_earn, f"Jual {listing['ore_name']} di market")
    from config import ORES
    ore_data = ORES.get(listing["ore_type"], {})
    avg_kg = (ore_data.get("kg_min", 0.5) + ore_data.get("kg_max", 2.0)) / 2
    total_kg = avg_kg * listing["quantity"]
    await add_ore_to_inventory(buyer_id, listing["ore_type"], listing["quantity"], total_kg)
    return True, seller_earn


async def cancel_market_listing(listing_id: int, user_id: int) -> tuple:
    listing = await get_listing_by_id(listing_id)
    if not listing:
        return False, "❌ Listing tidak ditemukan."
    if listing["seller_id"] != user_id:
        return False, "❌ Ini bukan listing kamu."
    if listing["status"] != "active":
        return False, "❌ Listing sudah tidak aktif."
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE market_listings SET status='cancelled' WHERE id=?", (listing_id,))
        await db.commit()
    # Kembalikan ore ke seller
    from config import ORES
    ore_data = ORES.get(listing["ore_type"], {})
    avg_kg = (ore_data.get("kg_min", 0.5) + ore_data.get("kg_max", 2.0)) / 2
    total_kg = avg_kg * listing["quantity"]
    await add_ore_to_inventory(user_id, listing["ore_type"], listing["quantity"], total_kg)
    return True, "✅ Listing berhasil dibatalkan. Ore dikembalikan."


async def get_user_market_listings(user_id: int) -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM market_listings WHERE seller_id=? AND status='active' ORDER BY listed_at DESC",
            (user_id,)
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]


async def get_market_daily_count(user_id: int) -> int:
    today = datetime.now().strftime("%Y-%m-%d")
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT count FROM market_daily_count WHERE user_id=? AND list_date=?",
            (user_id, today)
        ) as cur:
            row = await cur.fetchone()
            return row[0] if row else 0


async def increment_market_daily_count(user_id: int):
    today = datetime.now().strftime("%Y-%m-%d")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO market_daily_count(user_id, list_date, count) VALUES(?,?,1) "
            "ON CONFLICT(user_id, list_date) DO UPDATE SET count=count+1",
            (user_id, today)
        )
        await db.commit()


async def save_admin_photo(admin_id: int, photo_id: str, caption: str = "") -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO admin_photos(admin_id,photo_id,caption) VALUES(?,?,?)",
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
            async with db.execute("SELECT * FROM admin_photos ORDER BY uploaded_at DESC") as cur:
                return [dict(r) for r in await cur.fetchall()]


async def delete_admin_photo(photo_db_id: int, admin_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "DELETE FROM admin_photos WHERE id=? AND admin_id=?", (photo_db_id, admin_id)
        )
        await db.commit()
        return cur.rowcount > 0


async def get_leaderboard(limit: int = 10, exclude_admins: bool = True) -> list:
    from config import ADMIN_IDS
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if exclude_admins and ADMIN_IDS:
            placeholders = ",".join("?" * len(ADMIN_IDS))
            sql = (f"SELECT * FROM users WHERE user_id NOT IN ({placeholders}) "
                   f"ORDER BY total_earned DESC LIMIT ?")
            params = ADMIN_IDS + [limit]
        else:
            sql = "SELECT * FROM users ORDER BY total_earned DESC LIMIT ?"
            params = [limit]
        async with db.execute(sql, params) as cur:
            rows = await cur.fetchall()
            return [_row_to_user(r) for r in rows]


async def get_leaderboard_by(field: str, limit: int = 10, exclude_admins: bool = True) -> list:
    from config import ADMIN_IDS
    allowed = {"total_earned", "mine_count", "total_kg_mined", "total_mined"}
    if field not in allowed:
        field = "total_earned"
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if exclude_admins and ADMIN_IDS:
            placeholders = ",".join("?" * len(ADMIN_IDS))
            sql = (f"SELECT * FROM users WHERE user_id NOT IN ({placeholders}) "
                   f"ORDER BY {field} DESC LIMIT ?")
            params = ADMIN_IDS + [limit]
        else:
            sql = f"SELECT * FROM users ORDER BY {field} DESC LIMIT ?"
            params = [limit]
        async with db.execute(sql, params) as cur:
            rows = await cur.fetchall()
            return [_row_to_user(r) for r in rows]


async def get_user_rank(user_id: int) -> int:
    from config import ADMIN_IDS
    async with aiosqlite.connect(DB_PATH) as db:
        if ADMIN_IDS:
            placeholders = ",".join("?" * len(ADMIN_IDS))
            sql = (f"SELECT COUNT(*)+1 FROM users "
                   f"WHERE total_earned > (SELECT total_earned FROM users WHERE user_id=?) "
                   f"AND user_id NOT IN ({placeholders})")
            params = [user_id] + ADMIN_IDS
        else:
            sql = ("SELECT COUNT(*)+1 FROM users "
                   "WHERE total_earned > (SELECT total_earned FROM users WHERE user_id=?)")
            params = [user_id]
        async with db.execute(sql, params) as cur:
            row = await cur.fetchone()
            return row[0] if row else 999


async def get_ore_stats(user_id: int) -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT ore_type, ore_name, COUNT(*) cnt FROM mining_log "
            "WHERE user_id=? GROUP BY ore_type ORDER BY cnt DESC LIMIT 20",
            (user_id,)
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]


async def get_all_users() -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users ORDER BY created_at DESC") as cur:
            rows = await cur.fetchall()
            return [_row_to_user(r) for r in rows]


async def get_total_users() -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cur:
            row = await cur.fetchone()
            return row[0] if row else 0


async def set_ore_photo(ore_id: str, photo_id: str, caption: str, admin_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO ore_photos(ore_id,photo_id,caption,set_by,updated_at) VALUES(?,?,?,?,?)",
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
        async with db.execute("SELECT * FROM ore_photos ORDER BY updated_at DESC") as cur:
            return [dict(r) for r in await cur.fetchall()]


async def delete_ore_photo(ore_id: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("DELETE FROM ore_photos WHERE ore_id=?", (ore_id,))
        await db.commit()
        return cur.rowcount > 0


async def set_tool_photo(tool_id: str, photo_id: str, caption: str, admin_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO tool_photos(tool_id,photo_id,caption,set_by,updated_at) VALUES(?,?,?,?,?)",
            (tool_id, photo_id, caption, admin_id, datetime.now().isoformat())
        )
        await db.commit()
    return True


async def get_tool_photo(tool_id: str) -> Optional[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM tool_photos WHERE tool_id=?", (tool_id,)) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def get_all_tool_photos() -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM tool_photos ORDER BY updated_at DESC") as cur:
            return [dict(r) for r in await cur.fetchall()]


async def delete_tool_photo(tool_id: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("DELETE FROM tool_photos WHERE tool_id=?", (tool_id,))
        await db.commit()
        return cur.rowcount > 0


async def set_zone_photo(zone_id: str, photo_id: str, caption: str, admin_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO zone_photos(zone_id,photo_id,caption,set_by,updated_at) VALUES(?,?,?,?,?)",
            (zone_id, photo_id, caption, admin_id, datetime.now().isoformat())
        )
        await db.commit()
    return True


async def get_zone_photo(zone_id: str) -> Optional[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM zone_photos WHERE zone_id=?", (zone_id,)) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def get_all_zone_photos() -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM zone_photos ORDER BY updated_at DESC") as cur:
            return [dict(r) for r in await cur.fetchall()]


async def delete_zone_photo(zone_id: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("DELETE FROM zone_photos WHERE zone_id=?", (zone_id,))
        await db.commit()
        return cur.rowcount > 0


async def get_transfer_week_counts(user_id: int) -> dict:
    user = await get_user(user_id)
    if not user:
        return {"send": 0, "receive": 0}
    week_start = user.get("transfer_week_start")
    now = datetime.now()
    if not week_start:
        return {"send": 0, "receive": 0}
    try:
        ws_dt = datetime.fromisoformat(week_start)
        if (now - ws_dt).days >= 7:
            await update_user(user_id,
                transfer_send_count=0,
                transfer_receive_count=0,
                transfer_week_start=now.isoformat()
            )
            return {"send": 0, "receive": 0}
    except Exception:
        pass
    return {
        "send": user.get("transfer_send_count", 0),
        "receive": user.get("transfer_receive_count", 0)
    }


async def increment_transfer_send(user_id: int):
    user = await get_user(user_id)
    if not user:
        return
    week_start = user.get("transfer_week_start")
    now = datetime.now()
    reset = False
    if not week_start:
        reset = True
    else:
        try:
            ws_dt = datetime.fromisoformat(week_start)
            if (now - ws_dt).days >= 7:
                reset = True
        except Exception:
            reset = True
    if reset:
        await update_user(user_id,
            transfer_send_count=1,
            transfer_week_start=now.isoformat()
        )
    else:
        new_count = user.get("transfer_send_count", 0) + 1
        await update_user(user_id, transfer_send_count=new_count)


async def increment_transfer_receive(user_id: int):
    user = await get_user(user_id)
    if not user:
        return
    new_count = user.get("transfer_receive_count", 0) + 1
    await update_user(user_id, transfer_receive_count=new_count)


async def set_mining_multi_status(user_id: int, active: bool, multi_type: str = None):
    now = datetime.now().isoformat() if active else None
    await update_user(user_id,
        is_mining_multi=1 if active else 0,
        mining_multi_type=multi_type if active else None,
        mining_multi_started=now
    )


# ─── Weekly Leaderboard ────────────────────────────────────────────────────────
async def get_weekly_leaderboard(field: str = "balance", limit: int = 10) -> list:
    from config import ADMIN_IDS
    allowed = {"balance", "mine_count", "total_kg", "ore_count"}
    if field not in allowed:
        field = "balance"
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if ADMIN_IDS:
            placeholders = ",".join("?" * len(ADMIN_IDS))
            sql = (f"SELECT * FROM users WHERE user_id NOT IN ({placeholders}) "
                   f"ORDER BY {field if field not in ('balance','mine_count') else ('total_earned' if field=='balance' else 'mine_count')} DESC LIMIT ?")
            # Map field correctly
            real_field = {
                "balance": "total_earned",
                "mine_count": "mine_count",
                "total_kg": "total_kg_mined",
                "ore_count": "total_mined"
            }.get(field, "total_earned")
            sql = (f"SELECT * FROM users WHERE user_id NOT IN ({placeholders}) "
                   f"ORDER BY {real_field} DESC LIMIT ?")
            params = ADMIN_IDS + [limit]
        else:
            real_field = {
                "balance": "total_earned",
                "mine_count": "mine_count",
                "total_kg": "total_kg_mined",
                "ore_count": "total_mined"
            }.get(field, "total_earned")
            sql = f"SELECT * FROM users ORDER BY {real_field} DESC LIMIT ?"
            params = [limit]
        async with db.execute(sql, params) as cur:
            rows = await cur.fetchall()
            return [_row_to_user(r) for r in rows]


# ══════════════════════════════════════════════════════════════
# DYNAMIC ADMIN MANAGEMENT
# ══════════════════════════════════════════════════════════════

async def init_admin_table():
    """Buat tabel dynamic_admins jika belum ada."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS dynamic_admins (
                user_id     INTEGER PRIMARY KEY,
                added_by    INTEGER NOT NULL,
                added_at    TEXT    DEFAULT CURRENT_TIMESTAMP,
                note        TEXT    DEFAULT ''
            )
        """)
        await db.commit()


async def add_dynamic_admin(user_id: int, added_by: int, note: str = "") -> bool:
    await init_admin_table()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO dynamic_admins(user_id, added_by, note) VALUES(?,?,?)",
            (user_id, added_by, note)
        )
        await db.commit()
    return True


async def remove_dynamic_admin(user_id: int) -> bool:
    await init_admin_table()
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "DELETE FROM dynamic_admins WHERE user_id=?", (user_id,)
        )
        await db.commit()
        return cur.rowcount > 0


async def get_dynamic_admins() -> list:
    await init_admin_table()
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM dynamic_admins ORDER BY added_at DESC"
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]


async def is_dynamic_admin(user_id: int) -> bool:
    await init_admin_table()
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT 1 FROM dynamic_admins WHERE user_id=?", (user_id,)
        ) as cur:
            return (await cur.fetchone()) is not None


async def reset_all_users() -> int:
    """Reset semua data pemain ke nilai awal. Mengembalikan jumlah user yang direset."""
    async with aiosqlite.connect(DB_PATH) as db:
        import json as _json
        cur = await db.execute("""
            UPDATE users SET
                balance               = 1000,
                total_earned          = 0,
                total_mined           = 0,
                mine_count            = 0,
                energy                = 500,
                max_energy            = 500,
                bag_slots             = 50,
                level                 = 1,
                xp                    = 0,
                rebirth_count         = 0,
                perm_coin_mult        = 1.0,
                perm_xp_mult          = 1.0,
                current_tool          = 'stone_pick',
                current_zone          = 'surface',
                owned_tools           = '["stone_pick"]',
                unlocked_zones        = '["surface"]',
                inventory             = '{}',
                active_buffs          = '{}',
                achievements          = '[]',
                ore_inventory         = '{}',
                favorite_ores         = '[]',
                museum_ores           = '[]',
                ore_kg_data           = '{}',
                bag_kg_used           = 0.0,
                bag_kg_max            = 999999.0,
                total_kg_mined        = 0.0,
                daily_streak          = 0,
                last_daily            = NULL,
                last_energy_regen     = NULL,
                last_mine_time        = NULL,
                last_auto_mine        = NULL,
                vip_expires_at        = NULL,
                vip_type              = NULL,
                transfer_send_count   = 0,
                transfer_receive_count= 0,
                transfer_week_start   = NULL,
                is_mining_multi       = 0,
                mining_multi_type     = NULL,
                mining_multi_started  = NULL
        """)
        # Juga bersihkan mining_log, transactions, market
        await db.execute("DELETE FROM mining_log")
        await db.execute("DELETE FROM transactions")
        await db.execute("DELETE FROM market_listings")
        await db.execute("DELETE FROM market_daily_count")
        await db.commit()
        return cur.rowcount
