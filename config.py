"""
⚙️ CONFIG — MiningBot v4 ULTIMATE EDITION
   ✅ Sistem KG pada setiap ore (kg_min, kg_max)
   ✅ Harga jual ore berbasis berat KG
   ✅ Mining memberikan XP lebih banyak (bukan saldo langsung)
   ✅ Lebih banyak Ore, Alat, Item, Zona baru
"""
import os
import random
from dotenv import load_dotenv
load_dotenv()

# ── CREDENTIALS ──────────────────────────────────────────────
BOT_TOKEN = os.getenv("BOT_TOKEN", "8423250634:AAFY0bMwALbw3N7s-vwD4WAYujruhMSA44w")
_raw_admins = os.getenv("577381,7573097201")
ADMIN_IDS: list[int] = [int(x.strip()) for x in _raw_admins.split(",") if x.strip().isdigit()]
DATABASE_URL = os.getenv("DATABASE_URL", "mining_bot.db")

# ── EKONOMI ───────────────────────────────────────────────────
STARTING_BALANCE        = 1000
DAILY_BONUS_BASE        = 500
DAILY_BONUS_LEVEL       = 25
ENERGY_REGEN_RATE       = 10
ENERGY_COOLDOWN_MINUTES = 10
MAX_ENERGY_BASE         = 500
XP_BASE_MULTIPLIER      = 3.0
KG_PRICE_MULTIPLIER     = 1.5   # harga jual = value_dasar * kg * 1.5

# ── BAG ───────────────────────────────────────────────────────
BAG_SLOT_DEFAULT        = 50
BAG_SLOT_MAX            = 500
BAG_SLOT_STEP           = 10
BAG_SLOT_BASE_COST      = 1000
BAG_KG_DEFAULT          = 100.0
BAG_KG_MAX              = 10000.0
BAG_KG_UPGRADE_STEP     = 50.0
BAG_KG_UPGRADE_COST     = 2000

# ── ENERGY ────────────────────────────────────────────────────
ENERGY_UPGRADE_MAX       = 5000
ENERGY_UPGRADE_STEP      = 100
ENERGY_UPGRADE_BASE_COST = 5000
LUCKY_CHANCE             = 0.05
CRITICAL_CHANCE          = 0.10

# ══════════════════════════════════════════════════════════════
# ⛏️ TOOLS v4
# ══════════════════════════════════════════════════════════════
TOOLS: dict = {
    # TIER 1 STARTER
    "stone_pick": {"name":"⛏️ Beliung Batu","emoji":"⛏️","tier":1,"tier_name":"Starter","price":0,"power":1,"energy_cost":10,"speed_mult":1.0,"speed_delay":60,"crit_bonus":0.0,"luck_bonus":0.0,"xp_bonus":1.0,"kg_bonus":1.0,"description":"Beliung batu klasik. Gratis!","flavor":"Terbuat dari batu sungai.","level_req":1,"special":None,"ore_req":{}},
    # TIER 2 BASIC
    "copper_pick": {"name":"🔨 Beliung Tembaga","emoji":"🔨","tier":2,"tier_name":"Basic","price":5000,"power":3,"energy_cost":9,"speed_mult":1.1,"speed_delay":50,"crit_bonus":0.02,"luck_bonus":0.0,"xp_bonus":1.1,"kg_bonus":1.05,"description":"XP +10%, sedikit lebih cepat.","flavor":"Dilebur dari bijih tembaga murni.","level_req":2,"special":None,"ore_req":{}},
    "iron_pick": {"name":"⚒️ Beliung Besi","emoji":"⚒️","tier":2,"tier_name":"Basic","price":15000,"power":5,"energy_cost":8,"speed_mult":1.2,"speed_delay":45,"crit_bonus":0.03,"luck_bonus":0.01,"xp_bonus":1.2,"kg_bonus":1.1,"description":"XP +20%, ore lebih berat.","flavor":"Tempa besi kualitas tinggi.","level_req":4,"special":None,"ore_req":{}},
    "silver_pick": {"name":"🥈 Beliung Perak","emoji":"🥈","tier":2,"tier_name":"Basic","price":35000,"power":8,"energy_cost":8,"speed_mult":1.3,"speed_delay":40,"crit_bonus":0.04,"luck_bonus":0.02,"xp_bonus":1.3,"kg_bonus":1.15,"description":"+2% luck, XP +30%.","flavor":"Perak murni dipoles halus.","level_req":6,"special":"🍀 +2% luck bonus","ore_req":{}},
    "gold_pick": {"name":"🥇 Beliung Emas","emoji":"🥇","tier":2,"tier_name":"Basic","price":70000,"power":12,"energy_cost":9,"speed_mult":1.4,"speed_delay":38,"crit_bonus":0.05,"luck_bonus":0.03,"xp_bonus":1.4,"kg_bonus":1.2,"description":"XP +40%, crit +5%.","flavor":"Emas solid dengan gagang oak.","level_req":8,"special":"✨ +5% crit bonus","ore_req":{}},
    # TIER 3 ADVANCED
    "steel_drill": {"name":"🔩 Bor Baja","emoji":"🔩","tier":3,"tier_name":"Advanced","price":120000,"power":15,"energy_cost":12,"speed_mult":1.5,"speed_delay":35,"crit_bonus":0.05,"luck_bonus":0.02,"xp_bonus":1.5,"kg_bonus":1.25,"description":"XP +50%, menembus batuan keras.","flavor":"Mekanisme gigi roda pertama.","level_req":10,"special":None,"ore_req":{}},
    "electric_drill": {"name":"⚡ Bor Listrik","emoji":"⚡","tier":3,"tier_name":"Advanced","price":250000,"power":20,"energy_cost":14,"speed_mult":1.8,"speed_delay":30,"crit_bonus":0.06,"luck_bonus":0.03,"xp_bonus":1.7,"kg_bonus":1.3,"description":"XP +70%, kecepatan meningkat!","flavor":"Motor 500W torsi luar biasa.","level_req":12,"special":"⚡ 8% chance Double XP!","ore_req":{}},
    "sonic_drill": {"name":"🔊 Sonic Drill","emoji":"🔊","tier":3,"tier_name":"Advanced","price":400000,"power":28,"energy_cost":13,"speed_mult":2.0,"speed_delay":25,"crit_bonus":0.07,"luck_bonus":0.04,"xp_bonus":2.0,"kg_bonus":1.35,"description":"XP 2x, gelombang sonik!","flavor":"Frekuensi 50kHz menghancurkan batuan.","level_req":15,"special":"🔊 Sonic Boom: 5% +3x XP!","ore_req":{}},
    "crystal_drill": {"name":"🔷 Crystal Drill","emoji":"🔷","tier":3,"tier_name":"Advanced","price":600000,"power":35,"energy_cost":14,"speed_mult":2.1,"speed_delay":24,"crit_bonus":0.08,"luck_bonus":0.05,"xp_bonus":2.2,"kg_bonus":1.4,"description":"XP 2.2x, efisien untuk ore kristal.","flavor":"Kuarsa dipotong presisi laser.","level_req":17,"special":"💎 +15% XP dari ore kristal","ore_req":{}},
    # TIER 4 EXPERT
    "pneumatic_jack": {"name":"🏗️ Pneumatic Jackhammer","emoji":"🏗️","tier":4,"tier_name":"Expert","price":900000,"power":45,"energy_cost":18,"speed_mult":2.2,"speed_delay":22,"crit_bonus":0.09,"luck_bonus":0.05,"xp_bonus":2.5,"kg_bonus":1.5,"description":"XP 2.5x, mengguncang tanah!","flavor":"Angin bertekanan 200 PSI.","level_req":18,"special":"💥 Crit damage +15%","ore_req":{}},
    "diamond_drill": {"name":"💠 Diamond Drill","emoji":"💠","tier":4,"tier_name":"Expert","price":2000000,"power":70,"energy_cost":20,"speed_mult":2.5,"speed_delay":18,"crit_bonus":0.10,"luck_bonus":0.07,"xp_bonus":3.0,"kg_bonus":1.6,"description":"XP 3x, menembus apapun!","flavor":"Berlian industri grade-A.","level_req":22,"special":"🔮 +7% rare ore chance","ore_req":{}},
    "titanium_drill": {"name":"🔷 Titanium Drill Pro","emoji":"🔷","tier":4,"tier_name":"Expert","price":4000000,"power":100,"energy_cost":19,"speed_mult":2.7,"speed_delay":16,"crit_bonus":0.11,"luck_bonus":0.08,"xp_bonus":3.5,"kg_bonus":1.7,"description":"XP 3.5x, lebih kuat dari berlian!","flavor":"Titanium aerospace campuran.","level_req":27,"special":"🔷 +10% crit rate","ore_req":{}},
    "obsidian_breaker": {"name":"🌑 Obsidian Breaker","emoji":"🌑","tier":4,"tier_name":"Expert","price":6000000,"power":130,"energy_cost":22,"speed_mult":2.9,"speed_delay":15,"crit_bonus":0.12,"luck_bonus":0.09,"xp_bonus":4.0,"kg_bonus":1.8,"description":"XP 4x, ideal untuk zona lava!","flavor":"Alloy karbida tahan 2000°C.","level_req":30,"special":"🌋 +20% XP di Lava Zone","ore_req":{}},
    # TIER 5 MASTER
    "laser_cutter": {"name":"🔬 Laser Cutter Pro","emoji":"🔬","tier":5,"tier_name":"Master","price":12000000,"power":160,"energy_cost":22,"speed_mult":2.8,"speed_delay":14,"crit_bonus":0.12,"luck_bonus":0.10,"xp_bonus":4.5,"kg_bonus":2.0,"description":"XP 4.5x, akurasi sempurna.","flavor":"Laser CO₂ 1000W potong baja 50mm.","level_req":33,"special":"✨ +10% bonus XP","ore_req":{}},
    "plasma_drill": {"name":"🌟 Plasma Drill","emoji":"🌟","tier":5,"tier_name":"Master","price":25000000,"power":250,"energy_cost":26,"speed_mult":3.2,"speed_delay":12,"crit_bonus":0.15,"luck_bonus":0.12,"xp_bonus":5.0,"kg_bonus":2.2,"description":"XP 5x, mengionisasi batuan!","flavor":"Plasma dari reaktor fusi.","level_req":40,"special":"🌟 Plasma Burst: 12% +3x XP","ore_req":{}},
    "photon_extractor": {"name":"💡 Photon Extractor","emoji":"💡","tier":5,"tier_name":"Master","price":45000000,"power":400,"energy_cost":24,"speed_mult":3.5,"speed_delay":10,"crit_bonus":0.16,"luck_bonus":0.13,"xp_bonus":6.0,"kg_bonus":2.5,"description":"XP 6x, Ultra-cepat!","flavor":"Foton berenergi tinggi memisahkan mineral.","level_req":47,"special":"💡 Light Speed: 10% skip energy!","ore_req":{}},
    "nano_extractor": {"name":"🧬 Nano Extractor","emoji":"🧬","tier":5,"tier_name":"Master","price":60000000,"power":500,"energy_cost":25,"speed_mult":3.8,"speed_delay":9,"crit_bonus":0.17,"luck_bonus":0.14,"xp_bonus":7.0,"kg_bonus":2.8,"description":"XP 7x, presisi tingkat atom!","flavor":"Robot nano 10nm menggali bersama.","level_req":52,"special":"🧬 Nano Swarm: 15% +4x XP!","ore_req":{}},
    # TIER 6 LEGENDARY
    "quantum_miner": {"name":"💎 Quantum Miner X","emoji":"💎","tier":6,"tier_name":"Legendary","price":120000000,"power":700,"energy_cost":30,"speed_mult":4.0,"speed_delay":8,"crit_bonus":0.18,"luck_bonus":0.15,"xp_bonus":8.0,"kg_bonus":3.0,"description":"XP 8x, manipulasi quantum!","flavor":"Superposisi kuantum multi-dimensi.","level_req":58,"special":"🌀 Quantum Shift: 15% dapat 2 ore!","ore_req":{"diamond":50,"amethyst":20}},
    "void_extractor": {"name":"🕳️ Void Extractor","emoji":"🕳️","tier":6,"tier_name":"Legendary","price":300000000,"power":1200,"energy_cost":35,"speed_mult":5.0,"speed_delay":6,"crit_bonus":0.20,"luck_bonus":0.20,"xp_bonus":10.0,"kg_bonus":3.5,"description":"XP 10x, materi dari dimensi lain!","flavor":"Teknologi reruntuhan alien.","level_req":72,"special":"🕳️ Void Pull: 20% double loot!","ore_req":{"mythril":30,"diamond":100,"dragonstone":5}},
    "dark_matter_drill": {"name":"🌌 Dark Matter Drill","emoji":"🌌","tier":6,"tier_name":"Legendary","price":700000000,"power":2000,"energy_cost":38,"speed_mult":5.5,"speed_delay":5,"crit_bonus":0.22,"luck_bonus":0.22,"xp_bonus":12.0,"kg_bonus":4.0,"description":"XP 12x, kekuatan tak terbatas!","flavor":"Materi gelap belum dimengerti sains.","level_req":88,"special":"🌌 Dark Energy: 18% triple XP!","ore_req":{"void_shard":10,"stardust":20,"dragonstone":10}},
    "antimatter_borer": {"name":"💥 Antimatter Borer","emoji":"💥","tier":6,"tier_name":"Legendary","price":900000000,"power":2500,"energy_cost":40,"speed_mult":5.8,"speed_delay":5,"crit_bonus":0.23,"luck_bonus":0.23,"xp_bonus":14.0,"kg_bonus":4.5,"description":"XP 14x, anihilasi batuan instan!","flavor":"1mg antimateri = energi bom nuklir.","level_req":95,"special":"💥 Annihilation: 20% quadruple XP!","ore_req":{"void_shard":20,"nebula_ore":5,"dragonstone":15}},
    # TIER 7 MYTHICAL
    "celestial_hammer": {"name":"☄️ Celestial War Hammer","emoji":"☄️","tier":7,"tier_name":"Mythical","price":1500000000,"power":3500,"energy_cost":40,"speed_mult":6.0,"speed_delay":5,"crit_bonus":0.25,"luck_bonus":0.25,"xp_bonus":18.0,"kg_bonus":5.0,"description":"XP 18x, kekuatan dewa!","flavor":"Logam bintang neutron, ditempa dewa.","level_req":105,"special":"☄️ Meteor Strike: 25% +5x XP!","ore_req":{"void_shard":50,"stardust":30,"cosmic_dust":20,"dragonstone":20}},
    "god_hammer": {"name":"⚡ God's Hammer","emoji":"⚡","tier":7,"tier_name":"Mythical","price":5000000000,"power":7000,"energy_cost":50,"speed_mult":8.0,"speed_delay":5,"crit_bonus":0.30,"luck_bonus":0.30,"xp_bonus":25.0,"kg_bonus":6.0,"description":"XP 25x, kekuatan tanpa batas!","flavor":"Dicuri dari Olimpus oleh titan.","level_req":200,"special":"⚡ Divine Strike: 30% x10 XP!","ore_req":{"void_shard":100,"cosmic_dust":50,"nebula_ore":20,"stardust":50}},
    # TIER 8 DIVINE (BARU)
    "genesis_pick": {"name":"🌅 Genesis Pickaxe","emoji":"🌅","tier":8,"tier_name":"Divine","price":10000000000,"power":12000,"energy_cost":55,"speed_mult":10.0,"speed_delay":5,"crit_bonus":0.35,"luck_bonus":0.35,"xp_bonus":35.0,"kg_bonus":7.0,"description":"XP 35x, dari awal penciptaan!","flavor":"Materi Big Bang yang tertinggal.","level_req":300,"special":"🌅 Genesis Burst: 35% XP×15 & KG×2!","ore_req":{"time_crystal":10,"nebula_ore":50,"cosmic_dust":100,"void_shard":200}},
    "singularity_drill": {"name":"🌀 Singularity Drill","emoji":"🌀","tier":8,"tier_name":"Divine","price":50000000000,"power":25000,"energy_cost":60,"speed_mult":12.0,"speed_delay":5,"crit_bonus":0.40,"luck_bonus":0.40,"xp_bonus":50.0,"kg_bonus":8.0,"description":"XP 50x, merobek ruang-waktu!","flavor":"Bintang neutron terkompresi.","level_req":400,"special":"🌀 Singularity: 40% semua bonus ×10!","ore_req":{"time_crystal":50,"soul_fragment":20,"nebula_ore":100,"void_shard":500}},
}

# ══════════════════════════════════════════════════════════════
# 🪨 ORES v4 — Dengan sistem KG
# kg_min & kg_max = berat per 1 buah ore (kg)
# harga jual = value * kg_weight * KG_PRICE_MULTIPLIER
# ══════════════════════════════════════════════════════════════
ORES: dict = {
    # COMMON
    "pebble":          {"name":"🪨 Kerikil",        "emoji":"🪨","value":1,        "rarity":40.0, "xp":3,       "kg_min":0.1, "kg_max":0.5,   "desc":"Kerikil kecil tak berarti. Ringan sekali.",                              "tier":"common"},
    "coal":            {"name":"⬛ Batu Bara",       "emoji":"⬛","value":3,        "rarity":30.0, "xp":5,       "kg_min":0.5, "kg_max":2.0,   "desc":"Batu bara hitam, bahan bakar dasar.",                                    "tier":"common"},
    "stone":           {"name":"🗿 Batu Biasa",      "emoji":"🗿","value":5,        "rarity":20.0, "xp":6,       "kg_min":1.0, "kg_max":4.0,   "desc":"Batu biasa. Melimpah di permukaan.",                                     "tier":"common"},
    "sandstone":       {"name":"🟫 Batu Pasir",      "emoji":"🟫","value":4,        "rarity":18.0, "xp":5,       "kg_min":0.8, "kg_max":3.0,   "desc":"Batu pasir berpori, ringan.",                                            "tier":"common"},
    "clay":            {"name":"🟤 Tanah Liat",      "emoji":"🟤","value":6,        "rarity":16.0, "xp":7,       "kg_min":1.5, "kg_max":5.0,   "desc":"Tanah liat plastis, berguna untuk keramik.",                             "tier":"common"},
    # UNCOMMON
    "iron":            {"name":"⚙️ Bijih Besi",     "emoji":"⚙️","value":15,       "rarity":12.0, "xp":15,      "kg_min":2.0, "kg_max":6.0,   "desc":"Bijih besi abu-abu, bahan dasar industri.",                             "tier":"uncommon"},
    "copper":          {"name":"🟠 Bijih Tembaga",   "emoji":"🟠","value":25,       "rarity":10.0, "xp":20,      "kg_min":2.5, "kg_max":7.0,   "desc":"Tembaga kemerahan, konduktor listrik.",                                  "tier":"uncommon"},
    "tin":             {"name":"🔘 Timah",           "emoji":"🔘","value":20,       "rarity":9.0,  "xp":18,      "kg_min":2.0, "kg_max":6.5,   "desc":"Timah abu-abu kebiruan untuk paduan.",                                   "tier":"uncommon"},
    "lead":            {"name":"🔲 Timbal",          "emoji":"🔲","value":18,       "rarity":8.5,  "xp":16,      "kg_min":3.0, "kg_max":8.0,   "desc":"Timbal sangat berat dan padat.",                                         "tier":"uncommon"},
    "zinc":            {"name":"🔳 Seng",            "emoji":"🔳","value":22,       "rarity":8.0,  "xp":19,      "kg_min":2.5, "kg_max":7.0,   "desc":"Seng putih kebiruan untuk galvanisasi.",                                 "tier":"uncommon"},
    # RARE
    "silver":          {"name":"⬜ Perak",           "emoji":"⬜","value":80,       "rarity":6.0,  "xp":50,      "kg_min":3.0, "kg_max":9.0,   "desc":"Perak berkilau, lebih berharga dari tembaga.",                           "tier":"rare"},
    "quartz":          {"name":"🔷 Kuarsa",          "emoji":"🔷","value":70,       "rarity":5.0,  "xp":45,      "kg_min":2.0, "kg_max":7.0,   "desc":"Kristal kuarsa transparan, berguna di elektronik.",                      "tier":"rare"},
    "gold":            {"name":"🟡 Emas Murni",      "emoji":"🟡","value":200,      "rarity":4.0,  "xp":100,     "kg_min":4.0, "kg_max":12.0,  "desc":"Emas murni berkilau. Berharga dan cukup langka.",                        "tier":"rare"},
    "platinum":        {"name":"🤍 Platinum",        "emoji":"🤍","value":350,      "rarity":2.5,  "xp":160,     "kg_min":5.0, "kg_max":15.0,  "desc":"Platinum putih mewah, lebih langka dari emas.",                          "tier":"rare"},
    "palladium":       {"name":"🩶 Palladium",       "emoji":"🩶","value":300,      "rarity":3.0,  "xp":140,     "kg_min":4.5, "kg_max":13.0,  "desc":"Logam transisi langka, digunakan dalam katalis.",                        "tier":"rare"},
    # EPIC
    "sapphire":        {"name":"🔵 Safir",           "emoji":"🔵","value":600,      "rarity":2.0,  "xp":300,     "kg_min":1.0, "kg_max":5.0,   "desc":"Batu mulia biru langit yang menawan.",                                   "tier":"epic"},
    "emerald":         {"name":"💚 Zamrud",          "emoji":"💚","value":1000,     "rarity":1.5,  "xp":500,     "kg_min":1.5, "kg_max":6.0,   "desc":"Zamrud hijau yang memikat. Nilai tinggi!",                               "tier":"epic"},
    "ruby":            {"name":"❤️ Rubi",            "emoji":"❤️","value":2000,     "rarity":1.0,  "xp":800,     "kg_min":2.0, "kg_max":7.0,   "desc":"Rubi merah membara, batu mulia paling berharga.",                        "tier":"epic"},
    "topaz":           {"name":"🔶 Topaz",           "emoji":"🔶","value":1500,     "rarity":1.2,  "xp":600,     "kg_min":1.5, "kg_max":5.5,   "desc":"Topaz kuning oranye yang indah.",                                        "tier":"epic"},
    "tanzanite":       {"name":"💙 Tanzanit",        "emoji":"💙","value":2500,     "rarity":0.8,  "xp":1000,    "kg_min":2.0, "kg_max":8.0,   "desc":"Batu biru-ungu langka dari Afrika Timur.",                              "tier":"epic"},
    "garnet":          {"name":"🟥 Garnet",          "emoji":"🟥","value":1800,     "rarity":1.1,  "xp":700,     "kg_min":1.8, "kg_max":6.5,   "desc":"Garnet merah tua berkilau indah.",                                       "tier":"epic"},
    # LEGENDARY
    "diamond":         {"name":"💎 Berlian",         "emoji":"💎","value":5000,     "rarity":0.5,  "xp":2000,    "kg_min":0.5, "kg_max":3.0,   "desc":"Berlian murni, mineral terkeras di bumi!",                               "tier":"legendary"},
    "amethyst":        {"name":"💜 Ametis",          "emoji":"💜","value":8000,     "rarity":0.3,  "xp":3000,    "kg_min":1.0, "kg_max":4.0,   "desc":"Ametis ungu misterius, batu para penyihir.",                             "tier":"legendary"},
    "opal":            {"name":"🌈 Opal Pelangi",    "emoji":"🌈","value":15000,    "rarity":0.18, "xp":5000,    "kg_min":0.8, "kg_max":3.5,   "desc":"Opal memantulkan semua warna pelangi. Eksotis!",                         "tier":"legendary"},
    "mythril":         {"name":"🔮 Mithril",         "emoji":"🔮","value":25000,    "rarity":0.10, "xp":8000,    "kg_min":3.0, "kg_max":10.0,  "desc":"Logam mithril dari legenda kuno.",                                       "tier":"legendary"},
    "alexandrite":     {"name":"🟢 Alexandrit",      "emoji":"🟢","value":30000,    "rarity":0.08, "xp":9000,    "kg_min":0.5, "kg_max":2.5,   "desc":"Batu ajaib berubah warna di cahaya berbeda.",                            "tier":"legendary"},
    # MYTHICAL
    "dragonstone":     {"name":"🐉 Batu Naga",       "emoji":"🐉","value":80000,    "rarity":0.04, "xp":20000,   "kg_min":5.0, "kg_max":20.0,  "desc":"Batu mengandung jiwa naga purba. Ultra langka!",                         "tier":"mythical"},
    "stardust":        {"name":"✨ Debu Bintang",     "emoji":"✨","value":180000,   "rarity":0.012,"xp":40000,   "kg_min":0.1, "kg_max":1.0,   "desc":"Debu dari bintang jatuh. Bersinar di kegelapan.",                        "tier":"mythical"},
    "phoenix_ash":     {"name":"🔥 Abu Phoenix",     "emoji":"🔥","value":250000,   "rarity":0.009,"xp":55000,   "kg_min":0.2, "kg_max":2.0,   "desc":"Abu phoenix yang terlahir kembali. Energi api abadi.",                  "tier":"mythical"},
    "lunar_crystal":   {"name":"🌙 Kristal Bulan",   "emoji":"🌙","value":350000,   "rarity":0.007,"xp":70000,   "kg_min":1.0, "kg_max":5.0,   "desc":"Kristal cahaya bulan purnama 1000 tahun.",                               "tier":"mythical"},
    "void_shard":      {"name":"🌑 Void Shard",      "emoji":"🌑","value":500000,   "rarity":0.005,"xp":100000,  "kg_min":0.5, "kg_max":4.0,   "desc":"Pecahan dari dimensi kekosongan. Sangat langka!",                        "tier":"mythical"},
    # COSMIC
    "cosmic_dust":     {"name":"🌠 Debu Kosmik",     "emoji":"🌠","value":1000000,  "rarity":0.003,"xp":200000,  "kg_min":0.05,"kg_max":0.5,   "desc":"Debu dari tepi galaksi. Hampir mustahil ditemukan!",                     "tier":"cosmic"},
    "nebula_ore":      {"name":"🌌 Bijih Nebula",    "emoji":"🌌","value":2500000,  "rarity":0.001,"xp":400000,  "kg_min":2.0, "kg_max":8.0,   "desc":"Bijih dari awan nebula antarbintang.",                                   "tier":"cosmic"},
    "time_crystal":    {"name":"⏳ Kristal Waktu",   "emoji":"⏳","value":6000000,  "rarity":0.0005,"xp":1000000,"kg_min":0.3, "kg_max":2.0,   "desc":"Kristal mengandung energi waktu.",                                        "tier":"cosmic"},
    "dark_energy_ore": {"name":"🫥 Materi Gelap",    "emoji":"🫥","value":8000000,  "rarity":0.0003,"xp":1500000,"kg_min":0.1, "kg_max":1.5,   "desc":"Materi gelap yang nyaris tidak terdeteksi.",                             "tier":"cosmic"},
    # DIVINE (BARU)
    "soul_fragment":   {"name":"👻 Pecahan Jiwa",    "emoji":"👻","value":15000000, "rarity":0.0001,"xp":3000000,"kg_min":0.01,"kg_max":0.3,   "desc":"Pecahan jiwa makhluk purba. Menyentuh keabadian.",                       "tier":"divine"},
    "eternity_stone":  {"name":"♾️ Batu Keabadian",  "emoji":"♾️","value":50000000, "rarity":0.00005,"xp":10000000,"kg_min":1.0,"kg_max":5.0,  "desc":"Ada sejak sebelum alam semesta terbentuk.",                              "tier":"divine"},
    "universe_core":   {"name":"🌐 Inti Semesta",    "emoji":"🌐","value":100000000,"rarity":0.00001,"xp":20000000,"kg_min":10.0,"kg_max":50.0, "desc":"Inti dari alam semesta. Tidak ada yang lebih langka.",                   "tier":"divine"},
}

# ── KG Helpers ───────────────────────────────────────────────
KG_PRICE_MULTIPLIER = 1.5

def calculate_sell_price(ore_id: str, kg_weight: float) -> int:
    ore = ORES.get(ore_id, {})
    base_value = ore.get("value", 1)
    price = int(base_value * kg_weight * KG_PRICE_MULTIPLIER)
    return max(price, 1)

def get_random_kg(ore_id: str) -> float:
    ore = ORES.get(ore_id, {})
    kg_min = ore.get("kg_min", 0.5)
    kg_max = ore.get("kg_max", 2.0)
    return round(random.uniform(kg_min, kg_max), 2)

def format_kg(kg: float) -> str:
    """Format berat ke string yang mudah dibaca."""
    if kg < 1.0:
        return f"{kg*1000:.0f}g"
    elif kg < 100:
        return f"{kg:.2f} kg"
    else:
        return f"{kg:.1f} kg"

# ══════════════════════════════════════════════════════════════
# 🎒 ITEMS v4
# ══════════════════════════════════════════════════════════════
ITEMS: dict = {
    # Energy
    "energy_drink":      {"name":"🥤 Energy Drink",          "emoji":"🥤","price":500,      "description":"Pulihkan 50 energy.",                                "effect":{"energy":50},                         "stackable":True},
    "energy_potion":     {"name":"⚡ Energy Potion",          "emoji":"⚡","price":1000,     "description":"Pulihkan 100 energy seketika.",                      "effect":{"energy":100},                        "stackable":True},
    "energy_potion_lg":  {"name":"⚡⚡ Energy Potion XL",     "emoji":"⚡","price":2500,     "description":"Pulihkan energy PENUH seketika.",                    "effect":{"energy":9999},                       "stackable":True},
    # Luck
    "luck_elixir":       {"name":"🍀 Luck Elixir",            "emoji":"🍀","price":5000,     "description":"+25% peluang rare ore selama 30 menit.",             "effect":{"luck_buff":0.25,"duration":30},      "stackable":True},
    "mega_luck_potion":  {"name":"🌟 Mega Luck Potion",       "emoji":"🌟","price":15000,    "description":"+50% peluang rare ore selama 45 menit.",             "effect":{"luck_buff":0.50,"duration":45},      "stackable":True},
    "ore_magnet":        {"name":"🧲 Ore Magnet",             "emoji":"🧲","price":12000,    "description":"+35% chance rare ore selama 60 menit.",              "effect":{"luck_buff":0.35,"duration":60},      "stackable":True},
    # XP
    "xp_boost":          {"name":"⭐ XP Booster",             "emoji":"⭐","price":6000,     "description":"3x XP selama 30 menit.",                            "effect":{"xp_mult":3.0,"duration":30},         "stackable":True},
    "xp_mega_boost":     {"name":"🌠 XP Mega Boost",          "emoji":"🌠","price":20000,    "description":"5x XP selama 20 menit!",                            "effect":{"xp_mult":5.0,"duration":20},         "stackable":True},
    "scholar_scroll":    {"name":"📜 Gulungan Cendekiawan",   "emoji":"📜","price":10000,    "description":"2x XP selama 60 menit.",                            "effect":{"xp_mult":2.0,"duration":60},         "stackable":True},
    # Speed
    "speed_boost":       {"name":"🚀 Speed Boost",            "emoji":"🚀","price":8000,     "description":"Cooldown mining -50% selama 20 menit.",              "effect":{"speed_boost":0.5,"duration":20},     "stackable":True},
    "turbo_boost":       {"name":"⚡ Turbo Boost",            "emoji":"⚡","price":20000,    "description":"Cooldown mining -75% selama 15 menit!",             "effect":{"speed_boost":0.25,"duration":15},    "stackable":True},
    # KG Boost (BARU)
    "weight_enhancer":   {"name":"⚖️ Weight Enhancer",        "emoji":"⚖️","price":7000,    "description":"Ore 2x lebih berat selama 30 menit (harga jual 2x)!","effect":{"kg_boost":2.0,"duration":30},       "stackable":True},
    "heavy_ore_charm":   {"name":"🏋️ Heavy Ore Charm",       "emoji":"🏋️","price":18000,   "description":"Ore 3x lebih berat selama 20 menit!",                "effect":{"kg_boost":3.0,"duration":20},        "stackable":True},
    # Misc
    "mystery_box":       {"name":"📦 Mystery Box",            "emoji":"📦","price":3000,     "description":"Kotak misterius! Isi acak bisa XP, item, atau ore.", "effect":{"mystery":True},                      "stackable":True},
    "premium_mystery_box":{"name":"🎁 Premium Mystery Box",   "emoji":"🎁","price":25000,    "description":"Kotak premium! Dijamin item/ore berharga.",           "effect":{"mystery_premium":True},              "stackable":True},
    "bag_expander":      {"name":"🎒 Bag Expander",           "emoji":"🎒","price":5000,     "description":"+5 slot bag & +10 kg kapasitas instan.",             "effect":{"bag_expand":True},                   "stackable":True},
    "rebirth_token":     {"name":"🔄 Rebirth Token",          "emoji":"🔄","price":500000,   "description":"Reset level ke 1. Bonus permanen: +50% XP selamanya!","effect":{"rebirth":True},                    "stackable":False},
    # Coin buff tetap ada (dari jual ore)
    "double_coin":       {"name":"💰 Double Sell Scroll",     "emoji":"💰","price":8000,     "description":"2x harga jual ore di bag selama 20 menit.",          "effect":{"coin_mult":2.0,"duration":20},       "stackable":True},
}

# ══════════════════════════════════════════════════════════════
# 🏅 ACHIEVEMENTS v4
# ══════════════════════════════════════════════════════════════
ACHIEVEMENTS: dict = {
    "first_mine":       {"name":"🥇 Pertama Kali!",      "desc":"Lakukan mining pertama",            "reward":100},
    "mine_10":          {"name":"⛏️ Penambang Pemula",   "desc":"Mining 10 kali",                    "reward":200},
    "mine_100":         {"name":"💪 Penambang Sejati",    "desc":"Mining 100 kali",                   "reward":1000},
    "mine_1000":        {"name":"🏆 Master Miner",        "desc":"Mining 1.000 kali",                 "reward":10000},
    "mine_10000":       {"name":"👑 Legend Miner",        "desc":"Mining 10.000 kali",                "reward":100000},
    "mine_100000":      {"name":"🌟 God Miner",           "desc":"Mining 100.000 kali",               "reward":1000000},
    "first_rare":       {"name":"🔮 Rare Hunter",         "desc":"Dapatkan ore rare pertama",         "reward":500},
    "rich_100k":        {"name":"💰 Orang Kaya",          "desc":"Kumpulkan 100.000 koin",            "reward":2000},
    "rich_1m":          {"name":"💎 Jutawan",             "desc":"Kumpulkan 1.000.000 koin",          "reward":20000},
    "rich_1b":          {"name":"🏦 Miliarder",           "desc":"Kumpulkan 1 Miliar koin",           "reward":2000000},
    "rich_1t":          {"name":"👑 Triliunder",          "desc":"Kumpulkan 1 Triliun koin",          "reward":50000000},
    "lvl_10":           {"name":"⭐ Bintang 10",          "desc":"Capai Level 10",                    "reward":1000},
    "lvl_50":           {"name":"🌟 Bintang 50",          "desc":"Capai Level 50",                    "reward":10000},
    "lvl_100":          {"name":"💫 Century",             "desc":"Capai Level 100",                   "reward":100000},
    "lvl_200":          {"name":"🌙 Level 200",           "desc":"Capai Level 200",                   "reward":500000},
    "lvl_500":          {"name":"☀️ Level 500",           "desc":"Capai Level 500",                   "reward":2000000},
    "void_shard":       {"name":"🌑 Void Seeker",         "desc":"Temukan Void Shard pertama",        "reward":100000},
    "daily_streak_7":   {"name":"🔥 7-Day Streak",        "desc":"Daily bonus 7 hari berturut",       "reward":5000},
    "daily_streak_30":  {"name":"🌙 30-Day Streak",       "desc":"Daily bonus 30 hari berturut",      "reward":50000},
    "daily_streak_100": {"name":"💯 100-Day Streak",      "desc":"Daily bonus 100 hari berturut!",    "reward":500000},
    "market_first":     {"name":"🏪 Pedagang Pertama",    "desc":"Pertama kali jual di market",       "reward":2000},
    "rebirth_1":        {"name":"🔄 Reborn",              "desc":"Lakukan rebirth pertama",           "reward":20000},
    "cosmic_find":      {"name":"🌠 Cosmic Hunter",       "desc":"Temukan Debu Kosmik",               "reward":200000},
    "divine_find":      {"name":"♾️ Divine Hunter",       "desc":"Temukan Batu Keabadian",            "reward":5000000},
    "heavy_miner":      {"name":"🏋️ Heavy Miner",        "desc":"Kumpulkan total 1.000 kg ore",      "reward":50000},
    "super_heavy":      {"name":"⚓ Super Heavy",         "desc":"Kumpulkan total 10.000 kg ore",     "reward":500000},
    "kg_master":        {"name":"🌍 KG Master",           "desc":"Kumpulkan total 100.000 kg ore",    "reward":5000000},
}

# ══════════════════════════════════════════════════════════════
# ⭐ LEVEL SYSTEM
# ══════════════════════════════════════════════════════════════
def xp_for_level(level: int) -> int:
    return int(200 * (level ** 1.65))

MAX_LEVEL = 500

# ══════════════════════════════════════════════════════════════
# 🌍 ZONES v4
# ══════════════════════════════════════════════════════════════
ZONES: dict = {
    "surface":        {"name":"🏔️ Permukaan",      "desc":"Zona awal. Pebble, batu bara, dan besi.",                          "level_req":1,   "ore_bonus":{},                                                                    "unlock_cost":0,            "kg_bonus":1.0},
    "cave":           {"name":"🕯️ Gua Dalam",       "desc":"Lebih banyak besi, tembaga & perak.",                              "level_req":5,   "ore_bonus":{"iron":1.5,"silver":1.3,"tin":1.4,"copper":1.4},                     "unlock_cost":5000,         "kg_bonus":1.1},
    "underground":    {"name":"⛰️ Bawah Tanah",     "desc":"Emas, safir & platinum lebih sering muncul!",                      "level_req":15,  "ore_bonus":{"gold":1.8,"sapphire":1.5,"quartz":1.6,"platinum":1.4},              "unlock_cost":50000,        "kg_bonus":1.2},
    "lava_cave":      {"name":"🌋 Gua Lava",         "desc":"Rubi, berlian & tanzanit lebih melimpah! Berbahaya!",              "level_req":25,  "ore_bonus":{"ruby":2.0,"diamond":1.7,"topaz":1.8,"tanzanite":1.9},               "unlock_cost":200000,       "kg_bonus":1.3},
    "crystal_cavern": {"name":"🔮 Cavern Kristal",   "desc":"Ametis, mithril & alexandrit berlimpah!",                          "level_req":38,  "ore_bonus":{"amethyst":2.5,"mythril":2.0,"opal":2.0,"alexandrite":2.2},          "unlock_cost":800000,       "kg_bonus":1.4},
    "ancient_ruins":  {"name":"🏛️ Reruntuhan Kuno", "desc":"Peradaban kuno. Opal dan Mithril sangat banyak!",                  "level_req":50,  "ore_bonus":{"opal":2.5,"mythril":2.5,"amethyst":2.0,"alexandrite":2.0},          "unlock_cost":3000000,      "kg_bonus":1.5},
    "void_realm":     {"name":"🌑 Void Realm",       "desc":"Dimensi lain. Dragonstone, Void Shard & Phoenix Ash!",            "level_req":62,  "ore_bonus":{"dragonstone":3.0,"stardust":2.0,"void_shard":2.5,"phoenix_ash":2.0},"unlock_cost":8000000,      "kg_bonus":1.6},
    "sky_island":     {"name":"☁️ Pulau Langit",     "desc":"Pulau melayang. Stardust, Lunar Crystal & Cosmic Dust!",          "level_req":75,  "ore_bonus":{"stardust":3.0,"cosmic_dust":2.5,"void_shard":2.0,"lunar_crystal":2.5},"unlock_cost":30000000,    "kg_bonus":1.7},
    "deep_space":     {"name":"🚀 Luar Angkasa",     "desc":"Nebula Ore & Cosmic Dust melimpah!",                               "level_req":100, "ore_bonus":{"cosmic_dust":3.5,"nebula_ore":3.0,"stardust":2.5,"dark_energy_ore":2.0},"unlock_cost":150000000, "kg_bonus":1.8},
    "time_rift":      {"name":"⏳ Retakan Waktu",    "desc":"Zona di luar dimensi waktu. Kristal Waktu sangat langka!",        "level_req":150, "ore_bonus":{"time_crystal":3.0,"nebula_ore":2.5,"cosmic_dust":2.0,"dark_energy_ore":2.5},"unlock_cost":800000000,"kg_bonus":2.0},
    "soul_realm":     {"name":"👻 Alam Jiwa",        "desc":"Alam roh kuno. Soul Fragment & Eternity Stone tersembunyi!",      "level_req":200, "ore_bonus":{"soul_fragment":3.0,"eternity_stone":2.0,"void_shard":3.0,"time_crystal":2.5},"unlock_cost":5000000000,"kg_bonus":2.5},
    "genesis_realm":  {"name":"🌅 Alam Genesis",    "desc":"Tempat penciptaan alam semesta. Universe Core bisa ditemukan!",   "level_req":350, "ore_bonus":{"universe_core":2.0,"eternity_stone":2.5,"soul_fragment":3.5,"time_crystal":3.0},"unlock_cost":20000000000,"kg_bonus":3.0},
}

TIER_COLORS = {1:"⬜",2:"🟩",3:"🟦",4:"🟧",5:"🟥",6:"💜",7:"⭐",8:"🌈"}
ORE_TIER_COLORS = {"common":"⬜","uncommon":"🟩","rare":"🟦","epic":"🟧","legendary":"🟥","mythical":"💜","cosmic":"⭐","divine":"🌈"}

MARKET_FEE_PERCENT = 5
