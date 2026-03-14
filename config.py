"""
⚙️ CONFIG — Semua pengaturan game Mining Bot v2
   Edit file ini untuk kustomisasi game
"""
import os
from dotenv import load_dotenv
load_dotenv()

# ══════════════════════════════════════════════════════════════
# 🔑 CREDENTIALS
# ══════════════════════════════════════════════════════════════
BOT_TOKEN = os.getenv("BOT_TOKEN", "8423250634:AAFY0bMwALbw3N7s-vwD4WAYujruhMSA44w")

# ID Telegram admin (pisahkan dengan koma di env: "123,456")
_raw_admins = os.getenv("577381,7573097201")
ADMIN_IDS: list[int] = [int(x.strip()) for x in _raw_admins.split(",") if x.strip().isdigit()]

DATABASE_URL = os.getenv("DATABASE_URL", "mining_bot.db")

# ══════════════════════════════════════════════════════════════
# 💰 EKONOMI GAME
# ══════════════════════════════════════════════════════════════
STARTING_BALANCE   = 0          # Koin awal pemain baru
DAILY_BONUS_BASE   = 100        # Bonus harian dasar
DAILY_BONUS_LEVEL  = 10         # +X koin per level
ENERGY_REGEN_RATE  = 10         # Energy regen per 10 menit ( 50 energy per 1 menit)
ENERGY_COOLDOWN_MINUTES = 10    # Cooldown energy = 1 menit per 50 energy
MAX_ENERGY_BASE    = 500        # Max energy default (dimulai 500)

# ══════════════════════════════════════════════════════════════
# 🎒 BAG (Ore Inventory Slot)
# ══════════════════════════════════════════════════════════════
BAG_SLOT_DEFAULT   = 50          # Slot awal bag
BAG_SLOT_MAX       = 350         # Slot maksimal bag
BAG_SLOT_STEP      = 50          # Tambah slot per upgrade
BAG_SLOT_BASE_COST = 100000      # Harga upgrade slot pertama (naik setiap upgrade)

# ══════════════════════════════════════════════════════════════
# ⚡ ENERGY UPGRADE (via /buyenergy)
# ══════════════════════════════════════════════════════════════
ENERGY_UPGRADE_MAX      = 5000   # Max energy setelah upgrade
ENERGY_UPGRADE_STEP     = 100    # Tambah max energy per upgrade
ENERGY_UPGRADE_BASE_COST = 5000  # Harga upgrade energy pertama (naik bertahap)

# ══════════════════════════════════════════════════════════════
# ⛏️ PERALATAN MINING — Dari GRATIS hingga MYTHICAL
# Speed mining: murah = lama, mahal = cepat. Maks 4 detik (cooldown antar mine)
# speed_delay = detik tunggu antar mine (lebih kecil = lebih lama)
# ══════════════════════════════════════════════════════════════
TOOLS: dict = {

    # ╔══ TIER 1 — STARTER (Gratis) ═══════════════════════════╗
    "stone_pick": {
        "name":          "⛏️ Beliung Batu",
        "emoji":         "⛏️",
        "tier":          1,
        "tier_name":     "Starter",
        "price":         0,
        "power":         2,
        "energy_cost":   10,
        "speed_mult":    1.0,
        "speed_delay":   6,     # 6 detik per mine (paling lambat)
        "crit_bonus":    0.0,
        "luck_bonus":    0.0,
        "description":   "Beliung batu klasik. Gratis untuk semua pemain!",
        "flavor":        "Terbuat dari batu sungai yang dipahat kasar.",
        "level_req":     1,
        "special":       None,
        "ore_req":       {},     # tidak butuh ore
    },

    # ╔══ TIER 2 — BASIC ═══════════════════════════════════════╗
    "copper_pick": {
        "name":          "🔨 Beliung Tembaga",
        "emoji":         "🔨",
        "tier":          2,
        "tier_name":     "Basic",
        "price":         5000,
        "power":         5,
        "energy_cost":   9,
        "speed_mult":    1.1,
        "speed_delay":   6,
        "crit_bonus":    0.02,
        "luck_bonus":    0.0,
        "description":   "Beliung tembaga ringan. Power +5, sedikit lebih cepat.",
        "flavor":        "Dilebur dari bijih tembaga murni.",
        "level_req":     2,
        "special":       None,
        "ore_req":       {},
    },
    "iron_pick": {
        "name":          "⚒️ Beliung Besi",
        "emoji":         "⚒️",
        "tier":          2,
        "tier_name":     "Basic",
        "price":         15000,
        "power":         12,
        "energy_cost":   8,
        "speed_mult":    1.2,
        "speed_delay":   6,
        "crit_bonus":    0.03,
        "luck_bonus":    0.01,
        "description":   "Beliung besi kokoh. Power +12, efisiensi lebih baik.",
        "flavor":        "Tempa besi kualitas tinggi dari pandai besi.",
        "level_req":     4,
        "special":       None,
        "ore_req":       {},
    },
    "silver_pick": {
        "name":          "🥈 Beliung Perak",
        "emoji":         "🥈",
        "tier":          2,
        "tier_name":     "Basic",
        "price":         35000,
        "power":         20,
        "energy_cost":   8,
        "speed_mult":    1.3,
        "speed_delay":   6,
        "crit_bonus":    0.04,
        "luck_bonus":    0.02,
        "description":   "Beliung perak berkilau. Sedikit lebih beruntung.",
        "flavor":        "Dibuat dari perak murni yang dipoles halus.",
        "level_req":     6,
        "special":       "🍀 +2% luck bonus",
        "ore_req":       {},
    },

    # ╔══ TIER 3 — ADVANCED ════════════════════════════════════╗
    "steel_drill": {
        "name":          "🔩 Bor Baja",
        "emoji":         "🔩",
        "tier":          3,
        "tier_name":     "Advanced",
        "price":         80000,
        "power":         28,
        "energy_cost":   12,
        "speed_mult":    1.5,
        "speed_delay":   6,
        "crit_bonus":    0.05,
        "luck_bonus":    0.02,
        "description":   "Bor baja mekanik. Power +28, bisa menembus batuan keras.",
        "flavor":        "Mesin bor pertama yang menggunakan mekanisme gigi roda.",
        "level_req":     8,
        "special":       None,
        "ore_req":       {},
    },
    "electric_drill": {
        "name":          "⚡ Bor Listrik",
        "emoji":         "⚡",
        "tier":          3,
        "tier_name":     "Advanced",
        "price":         200000,
        "power":         55,
        "energy_cost":   14,
        "speed_mult":    1.8,
        "speed_delay":   6,
        "crit_bonus":    0.06,
        "luck_bonus":    0.03,
        "description":   "Bor bertenaga listrik. Power +55, kecepatan meningkat drastis!",
        "flavor":        "Motor 500W yang menghasilkan torsi luar biasa.",
        "level_req":     10,
        "special":       "⚡ Chance 8% untuk double ore!",
        "ore_req":       {},
    },
    "sonic_drill": {
        "name":          "🔊 Sonic Drill",
        "emoji":         "🔊",
        "tier":          3,
        "tier_name":     "Advanced",
        "price":         350000,
        "power":         80,
        "energy_cost":   13,
        "speed_mult":    2.0,
        "speed_delay":   6,
        "crit_bonus":    0.07,
        "luck_bonus":    0.04,
        "description":   "Bor sonik yang menggunakan gelombang suara. Sangat efisien!",
        "flavor":        "Frekuensi sonik 50kHz menghancurkan batuan tanpa gesekan.",
        "level_req":     14,
        "special":       "🔊 Sonic Boom: 5% chance +3x XP!",
        "ore_req":       {},
    },

    # ╔══ TIER 4 — EXPERT ══════════════════════════════════════╗
    "pneumatic_jack": {
        "name":          "🏗️ Pneumatic Jackhammer",
        "emoji":         "🏗️",
        "tier":          4,
        "tier_name":     "Expert",
        "price":         600000,
        "power":         120,
        "energy_cost":   18,
        "speed_mult":    2.2,
        "speed_delay":   6,
        "crit_bonus":    0.08,
        "luck_bonus":    0.05,
        "description":   "Jackhammer pneumatik industri. Power +120, mengguncang tanah!",
        "flavor":        "Ditenagai angin bertekanan tinggi 200 PSI.",
        "level_req":     16,
        "special":       "💥 Crit damage +15%",
        "ore_req":       {},
    },
    "diamond_drill": {
        "name":          "💠 Diamond Drill",
        "emoji":         "💠",
        "tier":          4,
        "tier_name":     "Expert",
        "price":         1500000,
        "power":         250,
        "energy_cost":   20,
        "speed_mult":    2.5,
        "speed_delay":   6,
        "crit_bonus":    0.10,
        "luck_bonus":    0.07,
        "description":   "Mata bor berlapis berlian asli. Power +250, menembus apapun!",
        "flavor":        "Lapisan berlian industri grade-A untuk ketahanan maksimal.",
        "level_req":     20,
        "special":       "🔮 +7% rare ore",
        "ore_req":       {},
    },
    "titanium_drill": {
        "name":          "🔷 Titanium Drill Pro",
        "emoji":         "🔷",
        "tier":          4,
        "tier_name":     "Expert",
        "price":         3000000,
        "power":         400,
        "energy_cost":   19,
        "speed_mult":    2.7,
        "speed_delay":   6,
        "crit_bonus":    0.11,
        "luck_bonus":    0.08,
        "description":   "Bor titanium aero-grade. Lebih kuat dari berlian!",
        "flavor":        "Titanium campuran aerospace, lebih ringan namun lebih keras.",
        "level_req":     25,
        "special":       "🔷 +10% crit rate",
        "ore_req":       {},
    },

    # ╔══ TIER 5 — MASTER ══════════════════════════════════════╗
    "laser_cutter": {
        "name":          "🔬 Laser Cutter Pro",
        "emoji":         "🔬",
        "tier":          5,
        "tier_name":     "Master",
        "price":         8000000,
        "power":         500,
        "energy_cost":   22,
        "speed_mult":    2.8,
        "speed_delay":   5,
        "crit_bonus":    0.12,
        "luck_bonus":    0.10,
        "description":   "Pemotong laser presisi tinggi. Power +500, akurasi sempurna.",
        "flavor":        "Laser CO₂ 1000W yang dapat memotong baja 50mm.",
        "level_req":     30,
        "special":       "✨ +10% bonus XP",
        "ore_req":       {},
    },
    "plasma_drill": {
        "name":          "🌟 Plasma Drill",
        "emoji":         "🌟",
        "tier":          5,
        "tier_name":     "Master",
        "price":         18000000,
        "power":         1000,
        "energy_cost":   26,
        "speed_mult":    3.2,
        "speed_delay":   5,
        "crit_bonus":    0.15,
        "luck_bonus":    0.12,
        "description":   "Bor plasma futuristik. Power +1000, mengionisasi batuan!",
        "flavor":        "Teknologi plasma yang diadaptasi dari reaktor fusi.",
        "level_req":     38,
        "special":       "🌟 Plasma Burst: 12% chance x3 coins",
        "ore_req":       {},
    },
    "photon_extractor": {
        "name":          "💡 Photon Extractor",
        "emoji":         "💡",
        "tier":          5,
        "tier_name":     "Master",
        "price":         30000000,
        "power":         1800,
        "energy_cost":   24,
        "speed_mult":    3.5,
        "speed_delay":   5,
        "crit_bonus":    0.16,
        "luck_bonus":    0.13,
        "description":   "Ekstraktor berbasis foton cahaya. Ultra-cepat!",
        "flavor":        "Menggunakan foton berenergi tinggi untuk memisahkan mineral dari batu.",
        "level_req":     45,
        "special":       "💡 Light Speed: 10% chance skip energy cost!",
        "ore_req":       {},
    },

    # ╔══ TIER 6 — LEGENDARY ═══════════════════════════════════╗
    "quantum_miner": {
        "name":          "💎 Quantum Miner X",
        "emoji":         "💎",
        "tier":          6,
        "tier_name":     "Legendary",
        "price":         80000000,
        "power":         2500,
        "energy_cost":   30,
        "speed_mult":    4.0,
        "speed_delay":   3,
        "crit_bonus":    0.18,
        "luck_bonus":    0.15,
        "description":   "Penambang kuantum ultra-canggih. Power +2500, manipulasi quantum!",
        "flavor":        "Menggunakan superposisi kuantum untuk menambang di multi-dimensi.",
        "level_req":     55,
        "special":       "🌀 Quantum Shift: 15% chance dapat 2 ore sekaligus!",
        "ore_req":       {"diamond": 50, "amethyst": 20},  # butuh 50 diamond + 20 amethyst
    },
    "void_extractor": {
        "name":          "🕳️ Void Extractor",
        "emoji":         "🕳️",
        "tier":          6,
        "tier_name":     "Legendary",
        "price":         200000000,
        "power":         5000,
        "energy_cost":   35,
        "speed_mult":    5.0,
        "speed_delay":   3,
        "crit_bonus":    0.20,
        "luck_bonus":    0.20,
        "description":   "Ekstraktor lubang hitam. Power +5000, menyedot materi dari dimensi lain!",
        "flavor":        "Teknologi yang ditemukan dari reruntuhan peradaban alien.",
        "level_req":     70,
        "special":       "🕳️ Void Pull: 20% chance mendapat double loot!",
        "ore_req":       {"mythril": 30, "diamond": 100, "dragonstone": 5},
    },
    "dark_matter_drill": {
        "name":          "🌌 Dark Matter Drill",
        "emoji":         "🌌",
        "tier":          6,
        "tier_name":     "Legendary",
        "price":         500000000,
        "power":         9000,
        "energy_cost":   38,
        "speed_mult":    5.5,
        "speed_delay":   3,    # 3 detik = speed maksimal
        "crit_bonus":    0.22,
        "luck_bonus":    0.22,
        "description":   "Bor materi gelap dari luar galaksi. Kekuatan tak terbatas!",
        "flavor":        "Menggunakan materi gelap yang belum dimengerti ilmu pengetahuan.",
        "level_req":     85,
        "special":       "🌌 Dark Energy: 18% chance triple coins + XP!",
        "ore_req":       {"void_shard": 10, "stardust": 20, "dragonstone": 10},
    },

    # ╔══ TIER 7 — MYTHICAL (Ultra Rare) ═══════════════════════╗
    "celestial_hammer": {
        "name":          "☄️ Celestial War Hammer",
        "emoji":         "☄️",
        "tier":          7,
        "tier_name":     "Mythical",
        "price":         1000000000,
        "power":         12000,
        "energy_cost":   40,
        "speed_mult":    6.0,
        "speed_delay":   2,    # 2 detik maksimal
        "crit_bonus":    0.25,
        "luck_bonus":    0.25,
        "description":   "Palu perang celestial dari surga. Power +12000, kekuatan dewa!",
        "flavor":        "Ditempa dari logam bintang neutron oleh para dewa tambang.",
        "level_req":     100,
        "special":       "☄️ Meteor Strike: 25% chance x5 coins! Juga +25% rare ore!",
        "ore_req":       {"void_shard": 50, "stardust": 30, "cosmic_dust": 20, "dragonstone": 20},
    },
    "god_hammer": {
        "name":          "⚡ God's Hammer",
        "emoji":         "⚡",
        "tier":          7,
        "tier_name":     "Mythical",
        "price":         5000000000,
        "power":         30000,
        "energy_cost":   50,
        "speed_mult":    8.0,
        "speed_delay":   2,
        "crit_bonus":    0.30,
        "luck_bonus":    0.30,
        "description":   "Palu milik para dewa. Kekuatan tanpa batas!",
        "flavor":        "Dicuri dari Olimpus oleh titan yang menjadi penambang.",
        "level_req":     200,
        "special":       "⚡ Divine Strike: 30% chance x10 coins!",
        "ore_req":       {"void_shard": 100, "cosmic_dust": 50, "nebula_ore": 20, "stardust": 50},
    },
}

# ══════════════════════════════════════════════════════════════
# 🪨 JENIS BIJIH — Dari umum hingga sangat langka
# ══════════════════════════════════════════════════════════════
ORES: dict = {
    "coal":          {"name": "🪨 Batu Bara",      "emoji": "🪨", "value": 1,        "rarity": 35.0,  "xp": 1,
                      "desc": "Batu bara hitam, bahan bakar dasar. Sangat umum ditemukan."},
    "stone":         {"name": "🗿 Batu Biasa",      "emoji": "🗿", "value": 2,        "rarity": 20.0,  "xp": 2,
                      "desc": "Batu biasa tanpa nilai khusus. Melimpah di permukaan."},
    "iron":          {"name": "⬛ Bijih Besi",      "emoji": "⬛", "value": 5,        "rarity": 18.0,  "xp": 4,
                      "desc": "Bijih besi abu-abu, bahan dasar industri. Cukup umum."},
    "copper":        {"name": "🟤 Bijih Tembaga",   "emoji": "🟤", "value": 8,        "rarity": 10.0,  "xp": 6,
                      "desc": "Tembaga kemerahan, konduktor listrik yang baik."},
    "silver":        {"name": "⬜ Perak",            "emoji": "⬜", "value": 20,       "rarity": 6.5,   "xp": 12,
                      "desc": "Perak berkilau, lebih berharga dari tembaga. Agak langka."},
    "tin":           {"name": "🔘 Timah",            "emoji": "🔘", "value": 15,       "rarity": 7.0,   "xp": 9,
                      "desc": "Timah abu-abu kebiruan, digunakan dalam paduan logam."},
    "gold":          {"name": "🟡 Emas Murni",       "emoji": "🟡", "value": 50,       "rarity": 4.0,   "xp": 25,
                      "desc": "Emas murni berkilau keemasan. Berharga dan cukup langka."},
    "quartz":        {"name": "🔳 Kuarsa",           "emoji": "🔳", "value": 35,       "rarity": 4.5,   "xp": 18,
                      "desc": "Kristal kuarsa transparan, digunakan di industri elektronik."},
    "sapphire":      {"name": "🔵 Safir",            "emoji": "🔵", "value": 150,      "rarity": 2.5,   "xp": 60,
                      "desc": "Batu mulia biru langit yang menawan. Cukup langka."},
    "emerald":       {"name": "💚 Zamrud",            "emoji": "💚", "value": 300,      "rarity": 1.5,   "xp": 100,
                      "desc": "Zamrud hijau zamrud yang memikat. Nilai tinggi!"},
    "ruby":          {"name": "❤️ Rubi",              "emoji": "❤️", "value": 600,      "rarity": 0.9,   "xp": 200,
                      "desc": "Rubi merah membara, salah satu batu mulia paling berharga."},
    "topaz":         {"name": "🔶 Topaz",             "emoji": "🔶", "value": 400,      "rarity": 1.2,   "xp": 150,
                      "desc": "Topaz kuning oranye yang indah. Sedikit lebih langka dari safir."},
    "diamond":       {"name": "💎 Berlian",           "emoji": "💎", "value": 1500,     "rarity": 0.5,   "xp": 500,
                      "desc": "Berlian murni, mineral terkeras di bumi. Sangat langka!"},
    "amethyst":      {"name": "💜 Ametis",            "emoji": "💜", "value": 3000,     "rarity": 0.25,  "xp": 800,
                      "desc": "Ametis ungu misterius, batu para penyihir. Sangat langka."},
    "opal":          {"name": "🌈 Opal Pelangi",      "emoji": "🌈", "value": 5000,     "rarity": 0.18,  "xp": 1200,
                      "desc": "Opal yang memantulkan semua warna pelangi. Eksotis!"},
    "mythril":       {"name": "🔮 Mithril",           "emoji": "🔮", "value": 8000,     "rarity": 0.10,  "xp": 2000,
                      "desc": "Logam mithril dari legenda kuno. Hampir tidak pernah ditemukan."},
    "dragonstone":   {"name": "🐉 Batu Naga",        "emoji": "🐉", "value": 20000,    "rarity": 0.04,  "xp": 5000,
                      "desc": "Batu yang katanya mengandung jiwa naga purba. Ultra langka!"},
    "stardust":      {"name": "✨ Debu Bintang",      "emoji": "✨", "value": 50000,    "rarity": 0.01,  "xp": 10000,
                      "desc": "Debu dari bintang jatuh. Bersinar di kegelapan. Sangat langka!"},
    "void_shard":    {"name": "🌑 Void Shard",       "emoji": "🌑", "value": 150000,   "rarity": 0.005, "xp": 30000,
                      "desc": "Pecahan dari dimensi kekosongan. Salah satu ore paling langka!"},
    "cosmic_dust":   {"name": "🌠 Debu Kosmik",      "emoji": "🌠", "value": 300000,   "rarity": 0.003, "xp": 60000,
                      "desc": "Debu dari tepi galaksi. Hampir mustahil ditemukan!"},
    "nebula_ore":    {"name": "🌌 Bijih Nebula",      "emoji": "🌌", "value": 800000,   "rarity": 0.001, "xp": 150000,
                      "desc": "Bijih dari awan nebula antarbintang. Sangat amat langka!"},
    "time_crystal":  {"name": "⏳ Kristal Waktu",    "emoji": "⏳", "value": 2000000,  "rarity": 0.0005,"xp": 500000,
                      "desc": "Kristal yang mengandung energi waktu. Nilai tak ternilai!"},
}

# ══════════════════════════════════════════════════════════════
# 🎒 ITEM / CONSUMABLE
# ══════════════════════════════════════════════════════════════
ITEMS: dict = {
    "energy_potion": {
        "name":        "⚡ Energy Potion",
        "emoji":       "⚡",
        "price":       500,
        "description": "Pulihkan 50 energy seketika.",
        "effect":      {"energy": 50},
        "stackable":   True,
    },
    "energy_potion_lg": {
        "name":        "⚡⚡ Energy Potion XL",
        "emoji":       "⚡",
        "price":       1200,
        "description": "Pulihkan energy PENUH seketika.",
        "effect":      {"energy": 999},
        "stackable":   True,
    },
    "luck_elixir": {
        "name":        "🍀 Luck Elixir",
        "emoji":       "🍀",
        "price":       3000,
        "description": "+20% peluang rare ore selama 30 menit.",
        "effect":      {"luck_buff": 0.20, "duration": 30},
        "stackable":   True,
    },
    "double_coin": {
        "name":        "💰 Double Coin Scroll",
        "emoji":       "💰",
        "price":       5000,
        "description": "2x koin selama 20 menit berikutnya.",
        "effect":      {"coin_mult": 2.0, "duration": 20},
        "stackable":   True,
    },
    "xp_boost": {
        "name":        "⭐ XP Booster",
        "emoji":       "⭐",
        "price":       4000,
        "description": "3x XP selama 20 menit.",
        "effect":      {"xp_mult": 3.0, "duration": 20},
        "stackable":   True,
    },
    "auto_miner_1h": {
        "name":        "🤖 Auto Miner (1 jam)",
        "emoji":       "🤖",
        "price":       8000,
        "description": "Mining otomatis setiap 10 menit selama 1 jam.",
        "effect":      {"auto_mine": True, "duration": 60},
        "stackable":   True,
    },
    "mystery_box": {
        "name":        "📦 Mystery Box",
        "emoji":       "📦",
        "price":       2000,
        "description": "Kotak misterius! Isi acak bisa koin, item, atau bahkan ore langka.",
        "effect":      {"mystery": True},
        "stackable":   True,
    },
    "rebirth_token": {
        "name":        "🔄 Rebirth Token",
        "emoji":       "🔄",
        "price":       500000,
        "description": "Reset level ke 1 dengan bonus permanen: +50% permanent coin boost! Max Rebirth saat Level 500.",
        "effect":      {"rebirth": True},
        "stackable":   False,
    },
    "speed_boost": {
        "name":        "🚀 Speed Boost",
        "emoji":       "🚀",
        "price":       6000,
        "description": "Kurangi cooldown mining 50% selama 15 menit.",
        "effect":      {"speed_boost": 0.5, "duration": 15},
        "stackable":   True,
    },
    "ore_magnet": {
        "name":        "🧲 Ore Magnet",
        "emoji":       "🧲",
        "price":       10000,
        "description": "+30% chance rare ore selama 45 menit.",
        "effect":      {"luck_buff": 0.30, "duration": 45},
        "stackable":   True,
    },
}

# ══════════════════════════════════════════════════════════════
# 🏅 PRESTASI / ACHIEVEMENTS
# ══════════════════════════════════════════════════════════════
ACHIEVEMENTS: dict = {
    "first_mine":      {"name": "🥇 Pertama Kali!",   "desc": "Lakukan mining pertama",          "reward": 500},
    "mine_10":         {"name": "⛏️ Penambang Pemula", "desc": "Mining 10 kali",                  "reward": 1000},
    "mine_100":        {"name": "💪 Penambang Sejati",  "desc": "Mining 100 kali",                 "reward": 5000},
    "mine_1000":       {"name": "🏆 Master Miner",     "desc": "Mining 1000 kali",                "reward": 50000},
    "mine_10000":      {"name": "👑 Legend Miner",     "desc": "Mining 10000 kali",               "reward": 500000},
    "first_rare":      {"name": "🔮 Rare Hunter",      "desc": "Dapatkan ore rare pertama",       "reward": 30000},
    "rich_100k":       {"name": "💰 Orang Kaya",       "desc": "Kumpulkan 100.000 koin",          "reward": 10000},
    "rich_1m":         {"name": "💎 Jutawan",           "desc": "Kumpulkan 1.000.000 koin",        "reward": 1000000},
    "rich_1b":         {"name": "🏦 Miliarder",        "desc": "Kumpulkan 1.000.000.000 koin",    "reward": 10000000},
    "lvl_10":          {"name": "⭐ Bintang 10",       "desc": "Capai Level 10",                  "reward": 5000},
    "lvl_50":          {"name": "🌟 Bintang 50",       "desc": "Capai Level 50",                  "reward": 50000},
    "lvl_100":         {"name": "💫 Century",           "desc": "Capai Level 100",                 "reward": 500000},
    "lvl_200":         {"name": "🌙 Level 200",        "desc": "Capai Level 200",                 "reward": 2000000},
    "lvl_500":         {"name": "☀️ Level 500",        "desc": "Capai Level 500 — Level Maks!",   "reward": 10000000},
    "void_shard":      {"name": "🌑 Void Seeker",      "desc": "Temukan Void Shard pertama",      "reward": 50000},
    "daily_streak_7":  {"name": "🔥 7-Day Streak",     "desc": "Daily bonus 7 hari berturut",     "reward": 200000},
    "daily_streak_30": {"name": "🌙 30-Day Streak",    "desc": "Daily bonus 30 hari berturut",    "reward": 2000000},
    "market_first":    {"name": "🏪 Pedagang Pertama", "desc": "Pertama kali jual ore di market", "reward": 100000},
    "rebirth_1":       {"name": "🔄 Reborn",           "desc": "Lakukan rebirth pertama",         "reward": 10000000},
    "cosmic_find":     {"name": "🌠 Cosmic Hunter",    "desc": "Temukan Debu Kosmik",             "reward": 100000000},
}

# ══════════════════════════════════════════════════════════════
# ⭐ LEVEL SYSTEM
# ══════════════════════════════════════════════════════════════
def xp_for_level(level: int) -> int:
    """XP yang dibutuhkan untuk naik dari level ini ke level berikutnya."""
    return int(150 * (level ** 1.6))

MAX_LEVEL = 500  # Level maksimal untuk rebirth adalah 500

# ══════════════════════════════════════════════════════════════
# 🌍 ZONA MINING (unlockable areas)
# ══════════════════════════════════════════════════════════════
ZONES: dict = {
    "surface": {
        "name": "🏔️ Permukaan",
        "desc": "Zona awal. Ore biasa seperti batu bara dan besi.",
        "level_req": 1,
        "ore_bonus": {},
        "unlock_cost": 0,
    },
    "cave": {
        "name": "🕯️ Gua Dalam",
        "desc": "Lebih banyak ore besi & perak. Gelap tapi kaya.",
        "level_req": 5,
        "ore_bonus": {"iron": 1.5, "silver": 1.3, "tin": 1.4},
        "unlock_cost": 30000,
    },
    "underground": {
        "name": "⛰️ Bawah Tanah",
        "desc": "Emas & safir lebih sering muncul. Ada quartz juga!",
        "level_req": 15,
        "ore_bonus": {"gold": 1.8, "sapphire": 1.5, "quartz": 1.6},
        "unlock_cost": 300000,
    },
    "lava_cave": {
        "name": "🌋 Gua Lava",
        "desc": "Rubi & berlian lebih melimpah! Berbahaya tapi menggiurkan.",
        "level_req": 25,
        "ore_bonus": {"ruby": 2.0, "diamond": 1.7, "topaz": 1.8},
        "unlock_cost": 1500000,
    },
    "crystal_cavern": {
        "name": "🔮 Cavern Kristal",
        "desc": "Ametis & mithril berlimpah! Opal langka juga ada.",
        "level_req": 40,
        "ore_bonus": {"amethyst": 2.5, "mythril": 2.0, "opal": 2.0},
        "unlock_cost": 3000000,
    },
    "void_realm": {
        "name": "🌑 Void Realm",
        "desc": "Dimensi lain. Dragonstone & Void Shard! Sangat berbahaya.",
        "level_req": 60,
        "ore_bonus": {"dragonstone": 3.0, "stardust": 2.0, "void_shard": 2.5},
        "unlock_cost": 5000000,
    },
    "ancient_ruins": {
        "name": "🏛️ Reruntuhan Kuno",
        "desc": "Reruntuhan peradaban kuno. Opal dan Mithril sangat banyak!",
        "level_req": 50,
        "ore_bonus": {"opal": 2.5, "mythril": 2.5, "amethyst": 2.0},
        "unlock_cost": 7000000,
    },
    "sky_island": {
        "name": "☁️ Pulau Langit",
        "desc": "Pulau melayang di atas awan. Stardust dan Cosmic Dust bersinar!",
        "level_req": 75,
        "ore_bonus": {"stardust": 3.0, "cosmic_dust": 2.5, "void_shard": 2.0},
        "unlock_cost": 10000000,
    },
    "deep_space": {
        "name": "🚀 Luar Angkasa",
        "desc": "Luar angkasa yang gelap. Nebula Ore dan Cosmic Dust melimpah!",
        "level_req": 100,
        "ore_bonus": {"cosmic_dust": 3.5, "nebula_ore": 3.0, "stardust": 2.5},
        "unlock_cost": 12000000,
    },
    "time_rift": {
        "name": "⏳ Retakan Waktu",
        "desc": "Zona di luar dimensi waktu. Kristal Waktu sangat langka di sini!",
        "level_req": 150,
        "ore_bonus": {"time_crystal": 3.0, "nebula_ore": 2.5, "cosmic_dust": 2.0},
        "unlock_cost": 15000000,
    },
}

# ══════════════════════════════════════════════════════════════
# PESAN SISTEM
# ══════════════════════════════════════════════════════════════
TIER_COLORS = {
    1: "⬜", 2: "🟩", 3: "🟦", 4: "🟧",
    5: "🟥", 6: "💜", 7: "⭐"
}

# ══════════════════════════════════════════════════════════════
# MARKET CONFIG
# ══════════════════════════════════════════════════════════════
MARKET_FEE_PERCENT = 5   # Biaya listing market 5% dari harga jual
