import os
import random
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "8423250634:AAFY0bMwALbw3N7s-vwD4WAYujruhMSA44w")
_raw_admins = os.getenv("ADMIN_IDS","577381","7573097201")
ADMIN_IDS: list[int] = [int(x.strip()) for x in _raw_admins.split(",") if x.strip().isdigit()]
DATABASE_URL = os.getenv("DATABASE_URL", "mining_bot.db")

STARTING_BALANCE        = 1000
DAILY_BONUS_BASE        = 500
DAILY_BONUS_LEVEL       = 25
ENERGY_REGEN_RATE       = 50       # energy per regen tick
ENERGY_COOLDOWN_MINUTES = 2        # ✅ Lebih cepat: 5 menit (dari 10)
MAX_ENERGY_BASE         = 500
XP_BASE_MULTIPLIER      = 1
KG_PRICE_MULTIPLIER     = 1

# ── Bag System ────────────────────────────────────────────────
BAG_SLOT_DEFAULT        = 50
BAG_SLOT_MAX            = 500
BAG_SLOT_STEP           = 10
BAG_SLOT_BASE_COST      = 50000
BAG_KG_DEFAULT          = 999999.0
BAG_KG_MAX              = 999999.0

# ── Energy Upgrade ────────────────────────────────────────────
ENERGY_UPGRADE_MAX       = 5000
ENERGY_UPGRADE_STEP      = 100
ENERGY_UPGRADE_BASE_COST = 150000
LUCKY_CHANCE             = 0.05
CRITICAL_CHANCE          = 0.10

# ── VIP System ───────────────────────────────────────────────
VIP_COOLDOWN_REDUCTION   = 0.85    # VIP: cooldown 15% lebih cepat
VIP_ENERGY_REGEN_BONUS   = 2       # VIP: +2 energy per regen
VIP_LUCK_BONUS           = 0.03    # VIP: +3% luck
VIP_CRIT_BONUS           = 0.02    # VIP: +2% crit
VIP_PRICES = {
    "1_month":  {"label": "1 Bulan",  "price": 40000,  "days": 30},
    "3_months": {"label": "3 Bulan",  "price": 110000,  "days": 90},
    "6_months": {"label": "6 Bulan",  "price": 200000, "days": 180},
    "lifetime": {"label": "Lifetime", "price": 350000, "days": 36500},
}
VIP_TRANSFER_INFO = os.getenv("VIP_TRANSFER_INFO", "Bank SEABANK: 901919719088 Erik Martin")
TOPUP_TRANSFER_INFO = os.getenv("TOPUP_TRANSFER_INFO", "Bank SEABANK: 901919719088 Erik Martin")
TOPUP_RATE = 1000  # 1 IDR = 1000 koin (contoh)

# ── TOOLS ─────────────────────────────────────────────────────
# CATATAN: level_req semua = 1 (tidak butuh level)
# xp_bonus semua = 1.0 (tidak ada multiplier XP dari alat)
# speed_delay: tier 1=6detik, makin tinggi tier makin cepat
TOOLS: dict = {
    # TIER 1 - STARTER (cooldown 6 detik)
    "stone_pick":      {"name":"⛏️ Beliung Batu",        "emoji":"⛏️", "tier":1,"tier_name":"Starter",  "price":0,            "power":1,    "energy_cost":10,"speed_mult":1.0,  "speed_delay":6, "crit_bonus":0.00,"luck_bonus":0.00,"xp_bonus":1.0,"kg_bonus":1.0,  "description":"Beliung batu klasik. Gratis!",               "flavor":"Terbuat dari batu sungai.",           "level_req":1,"special":None,"ore_req":{}},
    "wooden_pick":     {"name":"🪵 Beliung Kayu",         "emoji":"🪵", "tier":1,"tier_name":"Starter",  "price":500,          "power":2,    "energy_cost":10,"speed_mult":1.0,  "speed_delay":6, "crit_bonus":0.01,"luck_bonus":0.0, "xp_bonus":1.0,"kg_bonus":1.02, "description":"Sedikit lebih baik dari batu.",              "flavor":"Kayu oak keras dipahat.",             "level_req":1,"special":None,"ore_req":{}},
    "flint_pick":      {"name":"🪨 Beliung Batu Api",     "emoji":"🪨", "tier":1,"tier_name":"Starter",  "price":2000,         "power":3,    "energy_cost":9, "speed_mult":1.05, "speed_delay":6, "crit_bonus":0.01,"luck_bonus":0.01,"xp_bonus":1.0,"kg_bonus":1.04, "description":"+1% luck. Batu api yang keras.",            "flavor":"Batu api dari tepi sungai.",          "level_req":1,"special":"🔥 +1% luck","ore_req":{}},
    # TIER 2 - BASIC (cooldown 5 detik)
    "copper_pick":     {"name":"🔨 Beliung Tembaga",      "emoji":"🔨", "tier":2,"tier_name":"Basic",    "price":12000,        "power":4,    "energy_cost":9, "speed_mult":1.1,  "speed_delay":5, "crit_bonus":0.02,"luck_bonus":0.0, "xp_bonus":1.0,"kg_bonus":1.05, "description":"Sedikit lebih cepat.",                      "flavor":"Dilebur dari bijih tembaga.",         "level_req":1,"special":None,"ore_req":{}},
    "iron_pick":       {"name":"⚒️ Beliung Besi",         "emoji":"⚒️","tier":2,"tier_name":"Basic",    "price":35000,        "power":5,    "energy_cost":8, "speed_mult":1.2,  "speed_delay":5, "crit_bonus":0.03,"luck_bonus":0.01,"xp_bonus":1.0,"kg_bonus":1.1,  "description":"Ore lebih berat.",                          "flavor":"Tempa besi kualitas tinggi.",         "level_req":1,"special":None,"ore_req":{}},
    "bronze_pick":     {"name":"🟫 Beliung Perunggu",     "emoji":"🟫", "tier":2,"tier_name":"Basic",    "price":60000,        "power":7,    "energy_cost":8, "speed_mult":1.25, "speed_delay":5, "crit_bonus":0.03,"luck_bonus":0.01,"xp_bonus":1.0,"kg_bonus":1.12, "description":"Alloy tembaga-timah.",                      "flavor":"Perunggu dipakai sejak 3000 SM.",     "level_req":1,"special":None,"ore_req":{}},
    "silver_pick":     {"name":"🥈 Beliung Perak",        "emoji":"🥈", "tier":2,"tier_name":"Basic",    "price":90000,        "power":8,    "energy_cost":8, "speed_mult":1.3,  "speed_delay":5, "crit_bonus":0.04,"luck_bonus":0.02,"xp_bonus":1.0,"kg_bonus":1.15, "description":"+2% luck.",                                 "flavor":"Perak murni dipoles halus.",          "level_req":1,"special":"🍀 +2% luck","ore_req":{}},
    "gold_pick":       {"name":"🥇 Beliung Emas",         "emoji":"🥇", "tier":2,"tier_name":"Basic",    "price":180000,       "power":12,   "energy_cost":9, "speed_mult":1.4,  "speed_delay":5, "crit_bonus":0.05,"luck_bonus":0.03,"xp_bonus":1.0,"kg_bonus":1.2,  "description":"Crit +5%.",                                 "flavor":"Emas solid dengan gagang oak.",       "level_req":1,"special":"✨ +5% crit","ore_req":{}},
    "alloy_pick":      {"name":"🔩 Beliung Alloy",        "emoji":"🔩", "tier":2,"tier_name":"Basic",    "price":250000,       "power":14,   "energy_cost":8, "speed_mult":1.45, "speed_delay":5, "crit_bonus":0.05,"luck_bonus":0.03,"xp_bonus":1.0,"kg_bonus":1.22, "description":"Alloy logam campuran.",                     "flavor":"Nikel, kobalt, mangan campuran.",     "level_req":1,"special":None,"ore_req":{}},
    # TIER 3 - ADVANCED (cooldown 4 detik)
    "steel_drill":     {"name":"🔩 Bor Baja",             "emoji":"🔩", "tier":3,"tier_name":"Advanced", "price":350000,       "power":15,   "energy_cost":12,"speed_mult":1.5,  "speed_delay":4, "crit_bonus":0.05,"luck_bonus":0.02,"xp_bonus":1.0,"kg_bonus":1.25, "description":"Menembus batuan keras.",                    "flavor":"Mekanisme gigi roda pertama.",        "level_req":1,"special":None,"ore_req":{}},
    "electric_drill":  {"name":"⚡ Bor Listrik",           "emoji":"⚡", "tier":3,"tier_name":"Advanced", "price":700000,       "power":20,   "energy_cost":14,"speed_mult":1.8,  "speed_delay":4, "crit_bonus":0.06,"luck_bonus":0.03,"xp_bonus":1.0,"kg_bonus":1.3,  "description":"Kecepatan meningkat!",                      "flavor":"Motor 500W torsi luar biasa.",        "level_req":1,"special":"⚡ 8% Double KG!","ore_req":{}},
    "pneumatic_drill": {"name":"💨 Bor Pneumatik",         "emoji":"💨", "tier":3,"tier_name":"Advanced", "price":900000,       "power":24,   "energy_cost":13,"speed_mult":1.9,  "speed_delay":4, "crit_bonus":0.06,"luck_bonus":0.03,"xp_bonus":1.0,"kg_bonus":1.32, "description":"Tekanan angin tinggi.",                     "flavor":"Kompresor 150 PSI bertekanan.",       "level_req":1,"special":"💨 +8% rare ore","ore_req":{}},
    "sonic_drill":     {"name":"🔊 Sonic Drill",           "emoji":"🔊", "tier":3,"tier_name":"Advanced", "price":1200000,      "power":28,   "energy_cost":13,"speed_mult":2.0,  "speed_delay":4, "crit_bonus":0.07,"luck_bonus":0.04,"xp_bonus":1.0,"kg_bonus":1.35, "description":"Gelombang sonik!",                          "flavor":"Frekuensi 50kHz hancurkan batu.",     "level_req":1,"special":"🔊 Sonic Boom: 5% KG 3x!","ore_req":{}},
    "crystal_drill":   {"name":"🔷 Crystal Drill",         "emoji":"🔷", "tier":3,"tier_name":"Advanced", "price":2000000,      "power":35,   "energy_cost":14,"speed_mult":2.1,  "speed_delay":4, "crit_bonus":0.08,"luck_bonus":0.05,"xp_bonus":1.0,"kg_bonus":1.4,  "description":"Efisien untuk kristal.",                    "flavor":"Kuarsa dipotong presisi laser.",      "level_req":1,"special":"💎 +15% KG kristal","ore_req":{}},
    "magma_drill":     {"name":"🌋 Magma Drill",           "emoji":"🌋", "tier":3,"tier_name":"Advanced", "price":2500000,      "power":40,   "energy_cost":15,"speed_mult":2.15, "speed_delay":4, "crit_bonus":0.08,"luck_bonus":0.05,"xp_bonus":1.0,"kg_bonus":1.42, "description":"Tahan panas lava.",                         "flavor":"Alloy tungsten tahan 3000°C.",        "level_req":1,"special":"🌋 +20% bonus lava zone","ore_req":{}},
    # TIER 4 - EXPERT (cooldown 3 detik)
    "pneumatic_jack":  {"name":"🏗️ Pneumatic Jackhammer","emoji":"🏗️","tier":4,"tier_name":"Expert",   "price":3000000,      "power":45,   "energy_cost":18,"speed_mult":2.2,  "speed_delay":3, "crit_bonus":0.09,"luck_bonus":0.05,"xp_bonus":1.0,"kg_bonus":1.5,  "description":"Mengguncang tanah!",                        "flavor":"Angin bertekanan 200 PSI.",           "level_req":1,"special":"💥 Crit +15%","ore_req":{}},
    "diamond_drill":   {"name":"💠 Diamond Drill",         "emoji":"💠", "tier":4,"tier_name":"Expert",   "price":6000000,      "power":70,   "energy_cost":20,"speed_mult":2.5,  "speed_delay":3, "crit_bonus":0.10,"luck_bonus":0.07,"xp_bonus":1.0,"kg_bonus":1.6,  "description":"Menembus apapun!",                          "flavor":"Berlian industri grade-A.",           "level_req":1,"special":"🔮 +7% rare ore","ore_req":{}},
    "titanium_drill":  {"name":"🔷 Titanium Drill Pro",   "emoji":"🔷", "tier":4,"tier_name":"Expert",   "price":12000000,     "power":100,  "energy_cost":19,"speed_mult":2.7,  "speed_delay":3, "crit_bonus":0.11,"luck_bonus":0.08,"xp_bonus":1.0,"kg_bonus":1.7,  "description":"Lebih kuat dari berlian!",                  "flavor":"Titanium aerospace campuran.",        "level_req":1,"special":"🔷 +10% crit","ore_req":{}},
    "cobalt_drill":    {"name":"🔵 Cobalt Drill",          "emoji":"🔵", "tier":4,"tier_name":"Expert",   "price":18000000,     "power":115,  "energy_cost":20,"speed_mult":2.8,  "speed_delay":3, "crit_bonus":0.115,"luck_bonus":0.085,"xp_bonus":1.0,"kg_bonus":1.75,"description":"Kobalt super keras!",                       "flavor":"Kobalt grade militer.",               "level_req":1,"special":"🔵 +12% crit, KG +5%","ore_req":{}},
    "obsidian_breaker":{"name":"🌑 Obsidian Breaker",      "emoji":"🌑", "tier":4,"tier_name":"Expert",   "price":22000000,     "power":130,  "energy_cost":22,"speed_mult":2.9,  "speed_delay":3, "crit_bonus":0.12,"luck_bonus":0.09,"xp_bonus":1.0,"kg_bonus":1.8,  "description":"Ideal untuk zona lava!",                    "flavor":"Alloy karbida tahan 2000°C.",         "level_req":1,"special":"🌋 +20% KG lava","ore_req":{}},
    "meteor_hammer":   {"name":"☄️ Meteor Hammer",         "emoji":"☄️", "tier":4,"tier_name":"Expert",   "price":30000000,     "power":145,  "energy_cost":22,"speed_mult":3.0,  "speed_delay":3, "crit_bonus":0.12,"luck_bonus":0.09,"xp_bonus":1.0,"kg_bonus":1.85, "description":"Ditempa dari meteor!",                      "flavor":"Logam meteorit besi-nikel.",          "level_req":1,"special":"☄️ +12% crit, +9% luck","ore_req":{}},
    "void_hammer":     {"name":"🌌 Void Hammer",           "emoji":"🌌", "tier":4,"tier_name":"Expert",   "price":45000000,     "power":160,  "energy_cost":23,"speed_mult":3.1,  "speed_delay":3, "crit_bonus":0.13,"luck_bonus":0.10,"xp_bonus":1.0,"kg_bonus":1.9,  "description":"Diresapi energi void!",                     "flavor":"Logam void dari dimensi lain.",       "level_req":1,"special":"🌌 Void Touch: 10% KG 2x","ore_req":{}},
    "storm_pick":      {"name":"⛈️ Storm Pickaxe",         "emoji":"⛈️","tier":4,"tier_name":"Expert",   "price":55000000,     "power":175,  "energy_cost":23,"speed_mult":3.15, "speed_delay":3, "crit_bonus":0.13,"luck_bonus":0.10,"xp_bonus":1.0,"kg_bonus":1.92, "description":"Diperkuat petir badai!",                    "flavor":"Disambar petir 10.000 volt.",         "level_req":1,"special":"⛈️ +15% crit","ore_req":{}},
    # TIER 5 - MASTER (cooldown 2 detik)
    "laser_cutter":    {"name":"🔬 Laser Cutter Pro",     "emoji":"🔬", "tier":5,"tier_name":"Master",   "price":100000000,     "power":160,  "energy_cost":22,"speed_mult":2.8,  "speed_delay":2, "crit_bonus":0.12,"luck_bonus":0.10,"xp_bonus":1.0,"kg_bonus":2.0,  "description":"Akurasi sempurna.",                         "flavor":"Laser CO₂ 1000W.",                   "level_req":1,"special":"✨ +KG double","ore_req":{}},
    "plasma_drill":    {"name":"🌟 Plasma Drill",          "emoji":"🌟", "tier":5,"tier_name":"Master",   "price":150000000,    "power":250,  "energy_cost":26,"speed_mult":3.2,  "speed_delay":2, "crit_bonus":0.15,"luck_bonus":0.12,"xp_bonus":1.0,"kg_bonus":2.2,  "description":"Mengionisasi batuan!",                      "flavor":"Plasma dari reaktor fusi.",           "level_req":1,"special":"🌟 Plasma Burst: 12% KG 3x","ore_req":{}},
    "neutron_drill":   {"name":"⚛️ Neutron Drill",        "emoji":"⚛️","tier":5,"tier_name":"Master",   "price":200000000,    "power":320,  "energy_cost":27,"speed_mult":3.3,  "speed_delay":2, "crit_bonus":0.15,"luck_bonus":0.12,"xp_bonus":1.0,"kg_bonus":2.35, "description":"Partikel neutron!",                         "flavor":"Reaktor nuklir mini terkontrol.",     "level_req":1,"special":"⚛️ 10% KG 3.5x","ore_req":{}},
    "photon_extractor":{"name":"💡 Photon Extractor",     "emoji":"💡", "tier":5,"tier_name":"Master",   "price":250000000,    "power":400,  "energy_cost":24,"speed_mult":3.5,  "speed_delay":2, "crit_bonus":0.16,"luck_bonus":0.13,"xp_bonus":1.0,"kg_bonus":2.5,  "description":"Ultra-cepat!",                              "flavor":"Foton berenergi tinggi.",             "level_req":1,"special":"💡 Light Speed: 10% skip energy!","ore_req":{}},
    "tachyon_drill":   {"name":"🌀 Tachyon Drill",         "emoji":"🌀", "tier":5,"tier_name":"Master",   "price":300000000,    "power":480,  "energy_cost":25,"speed_mult":3.7,  "speed_delay":2, "crit_bonus":0.16,"luck_bonus":0.135,"xp_bonus":1.0,"kg_bonus":2.65,"description":"Menembus dimensi!",                         "flavor":"Teknologi FTL dari masa depan.",      "level_req":1,"special":"🌀 Tachyon: 12% KG 2x","ore_req":{}},
    "nano_extractor":  {"name":"🧬 Nano Extractor",        "emoji":"🧬", "tier":5,"tier_name":"Master",   "price":350000000,    "power":500,  "energy_cost":25,"speed_mult":3.8,  "speed_delay":2, "crit_bonus":0.17,"luck_bonus":0.14,"xp_bonus":1.0,"kg_bonus":2.8,  "description":"Presisi tingkat atom!",                     "flavor":"Robot nano 10nm menggali.",           "level_req":1,"special":"🧬 Nano Swarm: 15% KG 4x!","ore_req":{}},
    "psionic_drill":   {"name":"🧠 Psionic Drill",         "emoji":"🧠", "tier":5,"tier_name":"Master",   "price":400000000,    "power":580,  "energy_cost":26,"speed_mult":3.9,  "speed_delay":2, "crit_bonus":0.17,"luck_bonus":0.14,"xp_bonus":1.0,"kg_bonus":2.9,  "description":"Dikendalikan pikiran!",                     "flavor":"Antarmuka neural militer.",           "level_req":1,"special":"🧠 Psionic: 12% KG 3x & luck","ore_req":{}},
    "dark_wave_drill": {"name":"🌊 Dark Wave Drill",       "emoji":"🌊", "tier":5,"tier_name":"Master",   "price":450000000,    "power":620,  "energy_cost":27,"speed_mult":4.0,  "speed_delay":2, "crit_bonus":0.175,"luck_bonus":0.145,"xp_bonus":1.0,"kg_bonus":3.0,"description":"Gelombang energi gelap!",                   "flavor":"Energi dari materi anti.",            "level_req":1,"special":"🌊 Dark Wave: 15% rare+KG","ore_req":{}},
    # TIER 6 - LEGENDARY (cooldown 2 detik, butuh sedikit ore)
    "quantum_miner":   {"name":"💎 Quantum Miner X",       "emoji":"💎", "tier":6,"tier_name":"Legendary","price":500000000,    "power":700,  "energy_cost":30,"speed_mult":4.0,  "speed_delay":2, "crit_bonus":0.18,"luck_bonus":0.15,"xp_bonus":1.0,"kg_bonus":3.0,  "description":"Manipulasi quantum!",                       "flavor":"Superposisi kuantum multi-dim.",      "level_req":1,"special":"🌀 Quantum Shift: 15% 2 ore!","ore_req":{"diamond":5,"amethyst":3}},
    "void_extractor":  {"name":"🕳️ Void Extractor",       "emoji":"🕳️","tier":6,"tier_name":"Legendary","price":600000000,   "power":1200, "energy_cost":35,"speed_mult":5.0,  "speed_delay":2, "crit_bonus":0.20,"luck_bonus":0.20,"xp_bonus":1.0,"kg_bonus":3.5,  "description":"Materi dari dimensi lain!",                 "flavor":"Teknologi reruntuhan alien.",         "level_req":1,"special":"🕳️ Void Pull: 20% double loot!","ore_req":{"mythril":5,"diamond":10,"dragonstone":1}},
    "entropy_drill":   {"name":"🌪️ Entropy Drill",        "emoji":"🌪️","tier":6,"tier_name":"Legendary","price":700000000,   "power":1500, "energy_cost":36,"speed_mult":5.2,  "speed_delay":2, "crit_bonus":0.21,"luck_bonus":0.21,"xp_bonus":1.0,"kg_bonus":3.7,  "description":"Menggunakan entropi semesta!",               "flavor":"Prinsip termodinamika dibalik.",      "level_req":1,"special":"🌪️ Entropy: 18% KG 2x","ore_req":{"void_shard":1,"dragonstone":2}},
    "dark_matter_drill":{"name":"🌌 Dark Matter Drill",    "emoji":"🌌", "tier":6,"tier_name":"Legendary","price":800000000,   "power":2000, "energy_cost":38,"speed_mult":5.5,  "speed_delay":2, "crit_bonus":0.22,"luck_bonus":0.22,"xp_bonus":1.0,"kg_bonus":4.0,  "description":"Kekuatan tak terbatas!",                    "flavor":"Materi gelap belum dimengerti.",      "level_req":1,"special":"🌌 Dark Energy: 18% triple KG!","ore_req":{"void_shard":2,"stardust":5,"dragonstone":3}},
    "antimatter_borer":{"name":"💥 Antimatter Borer",      "emoji":"💥", "tier":6,"tier_name":"Legendary","price":900000000,   "power":2500, "energy_cost":40,"speed_mult":5.8,  "speed_delay":2, "crit_bonus":0.23,"luck_bonus":0.23,"xp_bonus":1.0,"kg_bonus":4.5,  "description":"Anihilasi batuan instan!",                  "flavor":"1mg antimateri=energi bom nuklir.",   "level_req":1,"special":"💥 Annihilation: 20% quad KG!","ore_req":{"void_shard":3,"nebula_ore":1,"dragonstone":5}},
    "wormhole_drill":  {"name":"🌐 Wormhole Drill",         "emoji":"🌐", "tier":6,"tier_name":"Legendary","price":1000000000,  "power":3000, "energy_cost":42,"speed_mult":6.0,  "speed_delay":2, "crit_bonus":0.24,"luck_bonus":0.24,"xp_bonus":1.0,"kg_bonus":4.8,  "description":"Membuka lubang cacing!",                    "flavor":"Singularitas mini terkontrol.",       "level_req":1,"special":"🌐 Wormhole: 20% ore bonus","ore_req":{"cosmic_dust":2,"nebula_ore":3,"void_shard":5}},
    "star_ripper":     {"name":"⭐ Star Ripper",            "emoji":"⭐", "tier":6,"tier_name":"Legendary","price":1500000000,  "power":3500, "energy_cost":43,"speed_mult":6.2,  "speed_delay":2, "crit_bonus":0.245,"luck_bonus":0.245,"xp_bonus":1.0,"kg_bonus":5.0,"description":"Merobek bintang!",                          "flavor":"Dibuat dari material supernova.",     "level_req":1,"special":"⭐ Star Tear: 22% KG 3x!","ore_req":{"stardust":5,"cosmic_dust":3,"void_shard":8}},
    # TIER 7 - MYTHICAL (cooldown 1 detik)
    "celestial_hammer":{"name":"☄️ Celestial War Hammer",  "emoji":"☄️", "tier":7,"tier_name":"Mythical", "price":2000000000,  "power":3500, "energy_cost":40,"speed_mult":6.0,  "speed_delay":1, "crit_bonus":0.25,"luck_bonus":0.25,"xp_bonus":1.0,"kg_bonus":5.0,  "description":"Kekuatan dewa!",                            "flavor":"Logam bintang neutron, dewa tempa.",  "level_req":1,"special":"☄️ Meteor Strike: 25% KG 5x!","ore_req":{"void_shard":10,"stardust":10,"cosmic_dust":5,"dragonstone":5}},
    "star_forge":      {"name":"⭐ Star Forge",              "emoji":"⭐", "tier":7,"tier_name":"Mythical", "price":2500000000,  "power":5000, "energy_cost":45,"speed_mult":7.0,  "speed_delay":1, "crit_bonus":0.27,"luck_bonus":0.27,"xp_bonus":1.0,"kg_bonus":5.5,  "description":"Ditempa dari inti bintang!",                "flavor":"Suhu inti bintang 15 juta derajat.",  "level_req":1,"special":"⭐ Star Forge: 25% KG 6x","ore_req":{"stardust":15,"cosmic_dust":8,"nebula_ore":5}},
    "god_hammer":      {"name":"⚡ God's Hammer",            "emoji":"⚡", "tier":7,"tier_name":"Mythical", "price":3000000000,  "power":7000, "energy_cost":50,"speed_mult":8.0,  "speed_delay":1, "crit_bonus":0.30,"luck_bonus":0.30,"xp_bonus":1.0,"kg_bonus":6.0,  "description":"Kekuatan tanpa batas!",                     "flavor":"Dicuri dari Olimpus oleh titan.",     "level_req":1,"special":"⚡ Divine Strike: 30% KG 10x!","ore_req":{"void_shard":20,"cosmic_dust":15,"nebula_ore":8,"stardust":20}},
    "eternal_pick":    {"name":"♾️ Eternal Pickaxe",         "emoji":"♾️","tier":7,"tier_name":"Mythical", "price":3500000000,  "power":9000, "energy_cost":48,"speed_mult":9.0,  "speed_delay":1, "crit_bonus":0.32,"luck_bonus":0.32,"xp_bonus":1.0,"kg_bonus":6.5,  "description":"Ada sebelum waktu!",                        "flavor":"Tidak diketahui pembuatnya.",         "level_req":1,"special":"♾️ Eternal: 30% KG 8x","ore_req":{"time_crystal":1,"soul_fragment":1,"void_shard":30,"cosmic_dust":20}},
    "galaxy_crusher":  {"name":"🌠 Galaxy Crusher",          "emoji":"🌠", "tier":7,"tier_name":"Mythical", "price":4000000000, "power":11000,"energy_cost":52,"speed_mult":9.5,  "speed_delay":1, "crit_bonus":0.33,"luck_bonus":0.33,"xp_bonus":1.0,"kg_bonus":7.0,  "description":"Menghancurkan galaksi!",                    "flavor":"Material dari inti galaksi.",         "level_req":1,"special":"🌠 Galaxy: 35% KG 10x!","ore_req":{"time_crystal":2,"soul_fragment":2,"nebula_ore":10,"void_shard":50}},
    # TIER 8 - DIVINE (cooldown 1 detik)
    "genesis_pick":    {"name":"🌅 Genesis Pickaxe",         "emoji":"🌅", "tier":8,"tier_name":"Divine",   "price":4500000000, "power":12000,"energy_cost":55,"speed_mult":10.0, "speed_delay":1, "crit_bonus":0.35,"luck_bonus":0.35,"xp_bonus":1.0,"kg_bonus":7.0,  "description":"Dari awal penciptaan!",                     "flavor":"Materi Big Bang yang tertinggal.",    "level_req":1,"special":"🌅 Genesis Burst: 35% KG 15x!","ore_req":{"time_crystal":3,"nebula_ore":15,"cosmic_dust":20,"void_shard":60}},
    "omega_drill":     {"name":"🔱 Omega Drill",              "emoji":"🔱", "tier":8,"tier_name":"Divine",   "price":5000000000, "power":18000,"energy_cost":57,"speed_mult":11.0, "speed_delay":1, "crit_bonus":0.37,"luck_bonus":0.37,"xp_bonus":1.0,"kg_bonus":7.5,  "description":"Senjata terakhir penambang!",               "flavor":"Diberkati para dewa tambang.",        "level_req":1,"special":"🔱 Omega: 38% KG 10x","ore_req":{"time_crystal":5,"soul_fragment":3,"eternity_stone":1,"void_shard":80}},
    "singularity_drill":{"name":"🌀 Singularity Drill",      "emoji":"🌀", "tier":8,"tier_name":"Divine",   "price":5500000000, "power":25000,"energy_cost":60,"speed_mult":12.0, "speed_delay":1, "crit_bonus":0.40,"luck_bonus":0.40,"xp_bonus":1.0,"kg_bonus":8.0,  "description":"Merobek ruang-waktu!",                      "flavor":"Bintang neutron terkompresi.",        "level_req":1,"special":"🌀 Singularity: 40% semua bonus!","ore_req":{"time_crystal":8,"soul_fragment":5,"nebula_ore":20,"void_shard":100}},
    "cosmos_hammer":   {"name":"🌌 Cosmos Hammer",            "emoji":"🌌", "tier":8,"tier_name":"Divine",   "price":6000000000,"power":40000,"energy_cost":65,"speed_mult":15.0, "speed_delay":1, "crit_bonus":0.45,"luck_bonus":0.45,"xp_bonus":1.0,"kg_bonus":10.0, "description":"Menghancurkan realitas!",                   "flavor":"Palu berisi energi seluruh galaksi.", "level_req":1,"special":"🌌 Cosmos: 45% KG 15x","ore_req":{"universe_core":1,"eternity_stone":5,"soul_fragment":8,"time_crystal":15}},
    "infinity_borer":  {"name":"♾️ Infinity Borer",           "emoji":"♾️","tier":8,"tier_name":"Divine",   "price":6500000000,"power":60000,"energy_cost":70,"speed_mult":18.0, "speed_delay":1, "crit_bonus":0.50,"luck_bonus":0.50,"xp_bonus":1.0,"kg_bonus":12.0, "description":"Penambang akhir segala zaman!",             "flavor":"Dibuat dari sisa Big Bang.",          "level_req":1,"special":"♾️ Infinity: 50% semua bonus!","ore_req":{"universe_core":2,"eternity_stone":10,"soul_fragment":15,"time_crystal":20}},
}

ORES: dict = {
    # COMMON
    "pebble":           {"name":"🪨 Kerikil",            "emoji":"🪨","value":5,           "rarity":40.0,     "xp":3,         "kg_min":0.1,    "kg_max":500.0,    "desc":"Kerikil kecil. Ringan sekali.",                                  "tier":"common"},
    "coal":             {"name":"⬛ Batu Bara",            "emoji":"⬛","value":10,          "rarity":30.0,     "xp":5,         "kg_min":0.5,    "kg_max":2000.0,   "desc":"Batu bara hitam, bahan bakar dasar.",                            "tier":"common"},
    "stone":            {"name":"🗿 Batu Biasa",           "emoji":"🗿","value":15,          "rarity":20.0,     "xp":6,         "kg_min":1.0,    "kg_max":4000.0,   "desc":"Batu biasa. Melimpah di permukaan.",                             "tier":"common"},
    "sandstone":        {"name":"🟫 Batu Pasir",           "emoji":"🟫","value":12,          "rarity":18.0,     "xp":5,         "kg_min":0.8,    "kg_max":3000.0,   "desc":"Batu pasir berpori, ringan.",                                    "tier":"common"},
    "clay":             {"name":"🟤 Tanah Liat",           "emoji":"🟤","value":18,          "rarity":16.0,     "xp":7,         "kg_min":1.5,    "kg_max":5000.0,   "desc":"Tanah liat plastis, berguna untuk keramik.",                     "tier":"common"},
    "gravel":           {"name":"⬜ Kerikil Kasar",         "emoji":"⬜","value":8,           "rarity":22.0,     "xp":4,         "kg_min":0.3,    "kg_max":1500.0,   "desc":"Kerikil besar-kasar.",                                           "tier":"common"},
    "chalk":            {"name":"🤍 Kapur",                 "emoji":"🤍","value":12,          "rarity":15.0,     "xp":5,         "kg_min":0.5,    "kg_max":2500.0,   "desc":"Kapur lunak putih.",                                             "tier":"common"},
    "mudstone":         {"name":"🟫 Batulumpur",            "emoji":"🟫","value":10,          "rarity":14.0,     "xp":4,         "kg_min":0.8,    "kg_max":3500.0,   "desc":"Batuan sedimen dari lumpur kuno.",                               "tier":"common"},
    "basalt":           {"name":"⬛ Basal",                  "emoji":"⬛","value":20,          "rarity":12.0,     "xp":8,         "kg_min":2.0,    "kg_max":8000.0,   "desc":"Batu vulkanik padat dari lava kuno.",                            "tier":"common"},
    "limestone":        {"name":"🟩 Batu Kapur",            "emoji":"🟩","value":15,          "rarity":13.0,     "xp":6,         "kg_min":1.5,    "kg_max":6000.0,   "desc":"Batu kapur dari dasar laut purba.",                              "tier":"common"},
    "granite":          {"name":"🪨 Granit",                "emoji":"🪨","value":22,          "rarity":11.0,     "xp":8,         "kg_min":2.0,    "kg_max":10000.0,  "desc":"Batuan beku bertekstur kasar.",                                  "tier":"common"},
    "obsidian_raw":     {"name":"🌑 Obsidian Kasar",        "emoji":"🌑","value":30,          "rarity":9.0,      "xp":10,        "kg_min":3.0,    "kg_max":12000.0,  "desc":"Kaca vulkanik dari lava yang mendingin.",                        "tier":"common"},
    "flint":            {"name":"🔥 Batu Api",               "emoji":"🔥","value":25,          "rarity":10.0,     "xp":9,         "kg_min":1.0,    "kg_max":5000.0,   "desc":"Batu api keras, dapat mengeluarkan percikan.",                   "tier":"common"},
    "pumice":           {"name":"🫧 Batu Apung",             "emoji":"🫧","value":18,          "rarity":11.5,     "xp":7,         "kg_min":0.2,    "kg_max":2000.0,   "desc":"Batu apung ringan dari letusan gunung berapi.",                  "tier":"common"},
    "shale":            {"name":"🟤 Serpih",                 "emoji":"🟤","value":14,          "rarity":12.5,     "xp":5,         "kg_min":1.0,    "kg_max":4000.0,   "desc":"Batuan sedimen berlapis tipis.",                                 "tier":"common"},
    # UNCOMMON
    "iron":             {"name":"⚙️ Bijih Besi",           "emoji":"⚙️","value":50,          "rarity":12.0,     "xp":15,        "kg_min":2.0,    "kg_max":6000.0,   "desc":"Bijih besi abu-abu, bahan dasar industri.",                     "tier":"uncommon"},
    "copper":           {"name":"🟠 Bijih Tembaga",         "emoji":"🟠","value":80,          "rarity":10.0,     "xp":20,        "kg_min":2.5,    "kg_max":7000.0,   "desc":"Tembaga kemerahan, konduktor listrik.",                          "tier":"uncommon"},
    "tin":              {"name":"🔘 Timah",                  "emoji":"🔘","value":60,          "rarity":9.0,      "xp":18,        "kg_min":2.0,    "kg_max":6500.0,   "desc":"Timah abu-abu kebiruan untuk paduan.",                           "tier":"uncommon"},
    "lead":             {"name":"🔲 Timbal",                 "emoji":"🔲","value":55,          "rarity":8.5,      "xp":16,        "kg_min":3.0,    "kg_max":8000.0,   "desc":"Timbal sangat berat dan padat.",                                 "tier":"uncommon"},
    "zinc":             {"name":"🔳 Seng",                   "emoji":"🔳","value":65,          "rarity":8.0,      "xp":19,        "kg_min":2.5,    "kg_max":7000.0,   "desc":"Seng putih kebiruan untuk galvanisasi.",                         "tier":"uncommon"},
    "nickel":           {"name":"🔶 Nikel",                  "emoji":"🔶","value":90,          "rarity":7.5,      "xp":22,        "kg_min":2.5,    "kg_max":7500.0,   "desc":"Nikel silver-putih, tahan korosi.",                              "tier":"uncommon"},
    "manganese":        {"name":"🟪 Mangan",                 "emoji":"🟪","value":100,         "rarity":7.0,      "xp":24,        "kg_min":3.0,    "kg_max":8000.0,   "desc":"Mangan keras, komponen baja kekuatan tinggi.",                   "tier":"uncommon"},
    "chromite":         {"name":"⚫ Kromit",                  "emoji":"⚫","value":120,         "rarity":6.5,      "xp":27,        "kg_min":3.0,    "kg_max":9000.0,   "desc":"Bijih krom hitam, untuk baja tahan karat.",                     "tier":"uncommon"},
    "sulfur":           {"name":"🟡 Belerang",               "emoji":"🟡","value":40,          "rarity":9.5,      "xp":13,        "kg_min":1.0,    "kg_max":4000.0,   "desc":"Belerang kuning dengan bau khas.",                               "tier":"uncommon"},
    "bauxite":          {"name":"🔴 Bauksit",                "emoji":"🔴","value":60,          "rarity":8.0,      "xp":17,        "kg_min":2.0,    "kg_max":7000.0,   "desc":"Bijih aluminium utama di dunia.",                                "tier":"uncommon"},
    "pyrite":           {"name":"✨ Pirit",                  "emoji":"✨","value":75,          "rarity":7.0,      "xp":21,        "kg_min":2.0,    "kg_max":6000.0,   "desc":"Pirit emas palsu, berkilau seperti emas.",                       "tier":"uncommon"},
    "magnetite":        {"name":"🔮 Magnetit",               "emoji":"🔮","value":85,          "rarity":6.8,      "xp":23,        "kg_min":2.5,    "kg_max":7500.0,   "desc":"Bijih besi magnetik, menarik logam.",                            "tier":"uncommon"},
    "galena":           {"name":"🩶 Galena",                 "emoji":"🩶","value":70,          "rarity":7.2,      "xp":20,        "kg_min":3.0,    "kg_max":8000.0,   "desc":"Bijih timbal utama dengan kilau logam.",                         "tier":"uncommon"},
    "sphalerite":       {"name":"🟫 Sphalerit",              "emoji":"🟫","value":80,          "rarity":6.5,      "xp":22,        "kg_min":2.5,    "kg_max":7000.0,   "desc":"Bijih seng utama, hitam mengkilap.",                             "tier":"uncommon"},
    "cinnabar":         {"name":"🔴 Sinnabari",              "emoji":"🔴","value":110,         "rarity":6.0,      "xp":26,        "kg_min":2.0,    "kg_max":6000.0,   "desc":"Bijih merkuri merah mencolok.",                                  "tier":"uncommon"},
    # RARE
    "silver":           {"name":"⬜ Perak",                  "emoji":"⬜","value":300,         "rarity":6.0,      "xp":50,        "kg_min":3.0,    "kg_max":9000.0,   "desc":"Perak berkilau, lebih berharga dari tembaga.",                   "tier":"rare"},
    "quartz":           {"name":"🔷 Kuarsa",                 "emoji":"🔷","value":250,         "rarity":5.0,      "xp":45,        "kg_min":2.0,    "kg_max":7000.0,   "desc":"Kristal kuarsa transparan.",                                     "tier":"rare"},
    "gold":             {"name":"🟡 Emas Murni",             "emoji":"🟡","value":800,         "rarity":4.0,      "xp":100,       "kg_min":4.0,    "kg_max":12000.0,  "desc":"Emas murni berkilau.",                                           "tier":"rare"},
    "platinum":         {"name":"🤍 Platinum",               "emoji":"🤍","value":1500,        "rarity":2.5,      "xp":160,       "kg_min":5.0,    "kg_max":15000.0,  "desc":"Platinum putih mewah, lebih langka dari emas.",                  "tier":"rare"},
    "palladium":        {"name":"🩶 Palladium",              "emoji":"🩶","value":1200,        "rarity":3.0,      "xp":140,       "kg_min":4.5,    "kg_max":13000.0,  "desc":"Logam transisi langka, digunakan dalam katalis.",                "tier":"rare"},
    "titanium_ore":     {"name":"🔵 Bijih Titanium",         "emoji":"🔵","value":1000,        "rarity":3.2,      "xp":130,       "kg_min":4.0,    "kg_max":12000.0,  "desc":"Titanium ringan namun sekuat baja.",                             "tier":"rare"},
    "cobalt_ore":       {"name":"🫐 Bijih Kobalt",           "emoji":"🫐","value":1200,        "rarity":2.8,      "xp":145,       "kg_min":4.5,    "kg_max":13000.0,  "desc":"Kobalt biru tua, digunakan dalam baterai.",                      "tier":"rare"},
    "tungsten":         {"name":"🩷 Tungsten",               "emoji":"🩷","value":1800,        "rarity":2.2,      "xp":180,       "kg_min":6.0,    "kg_max":18000.0,  "desc":"Tungsten titik lebur tertinggi dari semua logam.",               "tier":"rare"},
    "malachite":        {"name":"💚 Malakit",                "emoji":"💚","value":600,         "rarity":4.5,      "xp":75,        "kg_min":2.5,    "kg_max":8000.0,   "desc":"Tembaga karbonat hijau zamrud yang indah.",                      "tier":"rare"},
    "hematite":         {"name":"🩸 Hematit",                "emoji":"🩸","value":500,         "rarity":5.0,      "xp":60,        "kg_min":3.5,    "kg_max":10000.0,  "desc":"Bijih besi merah, digunakan sejak zaman batu.",                  "tier":"rare"},
    "rhodium":          {"name":"🔘 Rhodium",                "emoji":"🔘","value":2000,        "rarity":2.0,      "xp":200,       "kg_min":5.0,    "kg_max":15000.0,  "desc":"Logam paling mahal di dunia per gramnya.",                       "tier":"rare"},
    "iridium":          {"name":"⚫ Iridium",                 "emoji":"⚫","value":1700,        "rarity":2.3,      "xp":170,       "kg_min":5.0,    "kg_max":14000.0,  "desc":"Logam terkeras dari platinum group.",                            "tier":"rare"},
    "osmium":           {"name":"🔵 Osmium",                  "emoji":"🔵","value":1600,        "rarity":2.4,      "xp":160,       "kg_min":6.0,    "kg_max":16000.0,  "desc":"Logam paling padat yang ada di bumi.",                           "tier":"rare"},
    "ruthenium":        {"name":"🩶 Ruthenium",              "emoji":"🩶","value":1400,        "rarity":2.6,      "xp":150,       "kg_min":4.0,    "kg_max":12000.0,  "desc":"Logam keras dari platinum group.",                               "tier":"rare"},
    "rhenium":          {"name":"🔷 Rhenium",                "emoji":"🔷","value":1900,        "rarity":1.8,      "xp":190,       "kg_min":5.0,    "kg_max":15000.0,  "desc":"Logam langka dengan titik lebur sangat tinggi.",                 "tier":"rare"},
    # EPIC
    "sapphire":         {"name":"🔵 Safir",                  "emoji":"🔵","value":3000,        "rarity":2.0,      "xp":300,       "kg_min":1.0,    "kg_max":5000.0,   "desc":"Batu mulia biru langit yang menawan.",                           "tier":"epic"},
    "emerald":          {"name":"💚 Zamrud",                  "emoji":"💚","value":5000,        "rarity":1.5,      "xp":500,       "kg_min":1.5,    "kg_max":6000.0,   "desc":"Zamrud hijau yang memikat. Nilai tinggi!",                       "tier":"epic"},
    "ruby":             {"name":"❤️ Rubi",                    "emoji":"❤️","value":10000,       "rarity":1.0,      "xp":800,       "kg_min":2.0,    "kg_max":7000.0,   "desc":"Rubi merah membara, batu mulia paling berharga.",                "tier":"epic"},
    "topaz":            {"name":"🔶 Topaz",                  "emoji":"🔶","value":7500,        "rarity":1.2,      "xp":600,       "kg_min":1.5,    "kg_max":5500.0,   "desc":"Topaz kuning oranye yang indah.",                                "tier":"epic"},
    "tanzanite":        {"name":"💙 Tanzanit",               "emoji":"💙","value":12000,       "rarity":0.8,      "xp":1000,      "kg_min":2.0,    "kg_max":8000.0,   "desc":"Batu biru-ungu langka dari Afrika Timur.",                       "tier":"epic"},
    "garnet":           {"name":"🟥 Garnet",                 "emoji":"🟥","value":9000,        "rarity":1.1,      "xp":700,       "kg_min":1.8,    "kg_max":6500.0,   "desc":"Garnet merah tua berkilau indah.",                               "tier":"epic"},
    "aquamarine":       {"name":"🩵 Aquamarin",              "emoji":"🩵","value":11000,       "rarity":0.9,      "xp":900,       "kg_min":1.5,    "kg_max":6000.0,   "desc":"Batu laut biru kehijauan kristal bening.",                       "tier":"epic"},
    "tourmaline":       {"name":"🌈 Turmalin",               "emoji":"🌈","value":14000,       "rarity":0.75,     "xp":1100,      "kg_min":2.0,    "kg_max":7500.0,   "desc":"Turmalin multi-warna, batu paling berwarna-warni.",              "tier":"epic"},
    "spinel":           {"name":"🟣 Spinel",                 "emoji":"🟣","value":16000,       "rarity":0.65,     "xp":1300,      "kg_min":1.5,    "kg_max":6500.0,   "desc":"Spinel merah-ungu, sering salah disebut rubi.",                  "tier":"epic"},
    "zircon":           {"name":"🔸 Zirkon",                 "emoji":"🔸","value":10000,       "rarity":0.95,     "xp":800,       "kg_min":1.5,    "kg_max":5500.0,   "desc":"Zirkon berkilau amat terang seperti berlian.",                   "tier":"epic"},
    "peridot":          {"name":"🍏 Peridot",                "emoji":"🍏","value":8000,        "rarity":1.15,     "xp":650,       "kg_min":1.3,    "kg_max":5000.0,   "desc":"Peridot hijau-kuning dari mantel bumi.",                         "tier":"epic"},
    "iolite":           {"name":"💜 Iolit",                  "emoji":"💜","value":13000,       "rarity":0.85,     "xp":950,       "kg_min":1.8,    "kg_max":7000.0,   "desc":"Batu biru-ungu, kompas Viking kuno.",                            "tier":"epic"},
    "alexandrite_jr":   {"name":"🟣 Mini Alexandrit",        "emoji":"🟣","value":15000,       "rarity":0.70,     "xp":1200,      "kg_min":1.0,    "kg_max":5000.0,   "desc":"Versi kecil alexandrit, masih berubah warna.",                   "tier":"epic"},
    "chrysoberyl":      {"name":"🟡 Krisoberil",             "emoji":"🟡","value":11500,       "rarity":0.88,     "xp":870,       "kg_min":1.5,    "kg_max":6000.0,   "desc":"Kuning kehijauan, cat's eye effect.",                            "tier":"epic"},
    "sunstone":         {"name":"🌟 Batu Matahari",          "emoji":"🌟","value":9500,        "rarity":1.05,     "xp":750,       "kg_min":1.5,    "kg_max":5500.0,   "desc":"Batu yang berkilau seperti matahari.",                           "tier":"epic"},
    # LEGENDARY
    "diamond":          {"name":"💎 Berlian",                "emoji":"💎","value":25000,       "rarity":0.5,      "xp":2000,      "kg_min":0.5,    "kg_max":3000.0,   "desc":"Berlian murni, mineral terkeras di bumi!",                       "tier":"legendary"},
    "amethyst":         {"name":"💜 Ametis",                 "emoji":"💜","value":40000,       "rarity":0.3,      "xp":3000,      "kg_min":1.0,    "kg_max":4000.0,   "desc":"Ametis ungu misterius, batu para penyihir.",                     "tier":"legendary"},
    "opal":             {"name":"🌈 Opal Pelangi",           "emoji":"🌈","value":75000,       "rarity":0.18,     "xp":5000,      "kg_min":0.8,    "kg_max":3500.0,   "desc":"Opal memantulkan semua warna pelangi. Eksotis!",                 "tier":"legendary"},
    "mythril":          {"name":"🔮 Mithril",                "emoji":"🔮","value":125000,      "rarity":0.10,     "xp":8000,      "kg_min":3.0,    "kg_max":10000.0,  "desc":"Logam mithril dari legenda kuno.",                               "tier":"legendary"},
    "alexandrite":      {"name":"🟢 Alexandrit",             "emoji":"🟢","value":150000,      "rarity":0.08,     "xp":9000,      "kg_min":0.5,    "kg_max":2500.0,   "desc":"Batu ajaib berubah warna di cahaya berbeda.",                    "tier":"legendary"},
    "painite":          {"name":"🔴 Painit",                 "emoji":"🔴","value":200000,      "rarity":0.06,     "xp":12000,     "kg_min":0.3,    "kg_max":2000.0,   "desc":"Salah satu mineral paling langka di bumi.",                      "tier":"legendary"},
    "benitoite":        {"name":"💠 Benitoit",               "emoji":"💠","value":225000,      "rarity":0.05,     "xp":14000,     "kg_min":0.2,    "kg_max":1500.0,   "desc":"Safir biru fluoresen langka dari California.",                   "tier":"legendary"},
    "jadeite":          {"name":"🟩 Jadeite",                "emoji":"🟩","value":175000,      "rarity":0.07,     "xp":11000,     "kg_min":1.0,    "kg_max":5000.0,   "desc":"Giok kualitas tertinggi, lebih berharga dari emas.",             "tier":"legendary"},
    "larimar":          {"name":"🩵 Larimar",                "emoji":"🩵","value":140000,      "rarity":0.09,     "xp":8500,      "kg_min":0.5,    "kg_max":3000.0,   "desc":"Batu laut biru-putih langka dari Dominika.",                     "tier":"legendary"},
    "musgravite":       {"name":"🟤 Musgravit",              "emoji":"🟤","value":275000,      "rarity":0.04,     "xp":16000,     "kg_min":0.1,    "kg_max":1000.0,   "desc":"Batu mulia sangat langka dari Australia.",                       "tier":"legendary"},
    "red_beryl":        {"name":"🔴 Beril Merah",            "emoji":"🔴","value":185000,      "rarity":0.065,    "xp":11500,     "kg_min":0.3,    "kg_max":2000.0,   "desc":"Beril merah rubi, lebih langka dari berlian.",                   "tier":"legendary"},
    "grandidierite":    {"name":"🟦 Grandidierit",           "emoji":"🟦","value":195000,      "rarity":0.062,    "xp":12500,     "kg_min":0.5,    "kg_max":2500.0,   "desc":"Batu biru-hijau langka dari Madagascar.",                        "tier":"legendary"},
    "serendibite":      {"name":"🟫 Serendibit",             "emoji":"🟫","value":210000,      "rarity":0.055,    "xp":13000,     "kg_min":0.2,    "kg_max":1500.0,   "desc":"Mineral langka mengandung boron.",                                "tier":"legendary"},
    "poudretteite":     {"name":"🩷 Poudrétteite",           "emoji":"🩷","value":240000,      "rarity":0.045,    "xp":15000,     "kg_min":0.1,    "kg_max":1000.0,   "desc":"Mineral kristal merah muda ultra langka.",                       "tier":"legendary"},
    # MYTHICAL
    "dragonstone":      {"name":"🐉 Batu Naga",              "emoji":"🐉","value":400000,      "rarity":0.04,     "xp":20000,     "kg_min":5.0,    "kg_max":50000.0,  "desc":"Batu mengandung jiwa naga purba. Ultra langka!",                 "tier":"mythical"},
    "stardust":         {"name":"✨ Debu Bintang",            "emoji":"✨","value":900000,      "rarity":0.012,    "xp":40000,     "kg_min":0.1,    "kg_max":1000.0,   "desc":"Debu dari bintang jatuh. Bersinar di kegelapan.",                "tier":"mythical"},
    "phoenix_ash":      {"name":"🔥 Abu Phoenix",            "emoji":"🔥","value":1250000,     "rarity":0.009,    "xp":55000,     "kg_min":0.2,    "kg_max":2000.0,   "desc":"Abu phoenix yang terlahir kembali.",                             "tier":"mythical"},
    "lunar_crystal":    {"name":"🌙 Kristal Bulan",          "emoji":"🌙","value":1750000,     "rarity":0.007,    "xp":70000,     "kg_min":1.0,    "kg_max":5000.0,   "desc":"Kristal cahaya bulan purnama 1000 tahun.",                       "tier":"mythical"},
    "void_shard":       {"name":"🌑 Void Shard",             "emoji":"🌑","value":2500000,     "rarity":0.005,    "xp":100000,    "kg_min":0.5,    "kg_max":4000.0,   "desc":"Pecahan dari dimensi kekosongan.",                               "tier":"mythical"},
    "dragon_heart":     {"name":"💗 Jantung Naga",           "emoji":"💗","value":3500000,     "rarity":0.004,    "xp":140000,    "kg_min":2.0,    "kg_max":10000.0,  "desc":"Jantung naga purba masih berdenyut.",                            "tier":"mythical"},
    "leviathan_scale":  {"name":"🐍 Sisik Leviathan",        "emoji":"🐍","value":4500000,     "rarity":0.003,    "xp":180000,    "kg_min":3.0,    "kg_max":15000.0,  "desc":"Sisik makhluk laut raksasa dari zaman prasejarah.",              "tier":"mythical"},
    "thunder_stone":    {"name":"⚡ Batu Petir",              "emoji":"⚡","value":3000000,     "rarity":0.0045,   "xp":120000,    "kg_min":1.0,    "kg_max":6000.0,   "desc":"Batu yang terbentuk dari sambaran petir jutaan tahun.",          "tier":"mythical"},
    "glacial_shard":    {"name":"🧊 Serpihan Glacial",       "emoji":"🧊","value":2250000,     "rarity":0.006,    "xp":90000,     "kg_min":0.5,    "kg_max":5000.0,   "desc":"Kristal es dari zaman es 100.000 tahun lalu.",                   "tier":"mythical"},
    "cursed_gem":       {"name":"👁️ Batu Terkutuk",          "emoji":"👁️","value":6000000,    "rarity":0.002,    "xp":250000,    "kg_min":0.5,    "kg_max":3000.0,   "desc":"Batu berisi kutukan kuno.",                                      "tier":"mythical"},
    "phoenix_feather":  {"name":"🦅 Bulu Phoenix",           "emoji":"🦅","value":5000000,     "rarity":0.0025,   "xp":200000,    "kg_min":0.1,    "kg_max":1000.0,   "desc":"Bulu phoenix legendaris yang tidak terbakar.",                   "tier":"mythical"},
    "unicorn_horn":     {"name":"🦄 Tanduk Unicorn",         "emoji":"🦄","value":5500000,     "rarity":0.002,    "xp":220000,    "kg_min":0.5,    "kg_max":3000.0,   "desc":"Tanduk unicorn murni, penuh keajaiban.",                         "tier":"mythical"},
    "kraken_tentacle":  {"name":"🐙 Tentakel Kraken",        "emoji":"🐙","value":4000000,     "rarity":0.003,    "xp":160000,    "kg_min":5.0,    "kg_max":20000.0,  "desc":"Tentakel kraken raksasa, masih bergerak.",                       "tier":"mythical"},
    "basilisk_eye":     {"name":"🐍 Mata Basilisk",          "emoji":"🐍","value":7000000,     "rarity":0.0015,   "xp":280000,    "kg_min":0.3,    "kg_max":2000.0,   "desc":"Mata basilisk yang dapat mematikan.",                            "tier":"mythical"},
    "ancient_fossil":   {"name":"🦕 Fosil Kuno",             "emoji":"🦕","value":3200000,     "rarity":0.0038,   "xp":130000,    "kg_min":10.0,   "kg_max":50000.0,  "desc":"Fosil makhluk prasejarah jutaan tahun.",                         "tier":"mythical"},
    # COSMIC
    "cosmic_dust":      {"name":"🌠 Debu Kosmik",            "emoji":"🌠","value":5000000,     "rarity":0.003,    "xp":200000,    "kg_min":0.05,   "kg_max":500.0,    "desc":"Debu dari tepi galaksi. Hampir mustahil ditemukan!",             "tier":"cosmic"},
    "nebula_ore":       {"name":"🌌 Bijih Nebula",            "emoji":"🌌","value":12500000,    "rarity":0.001,    "xp":400000,    "kg_min":2.0,    "kg_max":8000.0,   "desc":"Bijih dari awan nebula antarbintang.",                           "tier":"cosmic"},
    "time_crystal":     {"name":"⏳ Kristal Waktu",           "emoji":"⏳","value":30000000,    "rarity":0.0005,   "xp":1000000,   "kg_min":0.3,    "kg_max":2000.0,   "desc":"Kristal mengandung energi waktu.",                               "tier":"cosmic"},
    "dark_energy_ore":  {"name":"🫥 Materi Gelap",           "emoji":"🫥","value":40000000,    "rarity":0.0003,   "xp":1500000,   "kg_min":0.1,    "kg_max":1500.0,   "desc":"Materi gelap yang nyaris tidak terdeteksi.",                     "tier":"cosmic"},
    "pulsar_fragment":  {"name":"💫 Serpihan Pulsar",         "emoji":"💫","value":20000000,    "rarity":0.0008,   "xp":700000,    "kg_min":0.5,    "kg_max":3000.0,   "desc":"Serpihan bintang pulsar yang berputar 700x/detik.",              "tier":"cosmic"},
    "quasar_crystal":   {"name":"🔆 Kristal Quasar",         "emoji":"🔆","value":25000000,    "rarity":0.0006,   "xp":900000,    "kg_min":0.2,    "kg_max":2500.0,   "desc":"Kristal dari pusat quasar paling terang.",                       "tier":"cosmic"},
    "antimatter_shard": {"name":"💥 Serpihan Antimateri",    "emoji":"💥","value":50000000,    "rarity":0.0002,   "xp":2000000,   "kg_min":0.01,   "kg_max":500.0,    "desc":"Secuil antimateri — kontak dengan materi = ledakan.",            "tier":"cosmic"},
    "neutron_core":     {"name":"⚪ Inti Neutron",            "emoji":"⚪","value":60000000,    "rarity":0.00015,  "xp":2500000,   "kg_min":5.0,    "kg_max":50000.0,  "desc":"Inti bintang neutron — lebih padat dari timbal.",                "tier":"cosmic"},
    "singularity_ore":  {"name":"🌀 Bijih Singularitas",     "emoji":"🌀","value":100000000,   "rarity":0.0001,   "xp":4000000,   "kg_min":0.001,  "kg_max":100.0,    "desc":"Ore dari dalam lubang hitam.",                                   "tier":"cosmic"},
    "gamma_crystal":    {"name":"☢️ Kristal Gamma",           "emoji":"☢️","value":35000000,   "rarity":0.0004,   "xp":1200000,   "kg_min":0.1,    "kg_max":1000.0,   "desc":"Kristal teriradiasi sinar gamma dari magnetar.",                 "tier":"cosmic"},
    "supernova_ash":    {"name":"💥 Abu Supernova",           "emoji":"💥","value":45000000,    "rarity":0.00025,  "xp":1800000,   "kg_min":0.05,   "kg_max":800.0,    "desc":"Abu dari ledakan supernova bintang raksasa.",                    "tier":"cosmic"},
    "black_hole_dust":  {"name":"⚫ Debu Lubang Hitam",       "emoji":"⚫","value":80000000,    "rarity":0.00012,  "xp":3000000,   "kg_min":0.001,  "kg_max":200.0,    "desc":"Debu dari tepi horizon peristiwa lubang hitam.",                 "tier":"cosmic"},
    "magnetar_shard":   {"name":"🧲 Serpihan Magnetar",      "emoji":"🧲","value":55000000,    "rarity":0.00018,  "xp":2200000,   "kg_min":1.0,    "kg_max":5000.0,   "desc":"Serpihan bintang dengan medan magnet terkuat.",                  "tier":"cosmic"},
    "warp_crystal":     {"name":"🌀 Kristal Warp",           "emoji":"🌀","value":70000000,    "rarity":0.00013,  "xp":2800000,   "kg_min":0.1,    "kg_max":1000.0,   "desc":"Kristal yang melengkungkan ruang di sekitarnya.",                "tier":"cosmic"},
    # DIVINE
    "soul_fragment":    {"name":"👻 Pecahan Jiwa",            "emoji":"👻","value":75000000,    "rarity":0.0001,   "xp":3000000,   "kg_min":0.01,   "kg_max":300.0,    "desc":"Pecahan jiwa makhluk purba. Menyentuh keabadian.",               "tier":"divine"},
    "eternity_stone":   {"name":"♾️ Batu Keabadian",          "emoji":"♾️","value":250000000,  "rarity":0.00005,  "xp":10000000,  "kg_min":1.0,    "kg_max":5000.0,   "desc":"Ada sejak sebelum alam semesta terbentuk.",                      "tier":"divine"},
    "universe_core":    {"name":"🌐 Inti Semesta",            "emoji":"🌐","value":500000000,  "rarity":0.00001,  "xp":20000000,  "kg_min":10.0,   "kg_max":100000.0, "desc":"Inti dari alam semesta. Tidak ada yang lebih langka.",           "tier":"divine"},
    "god_tear":         {"name":"💧 Air Mata Dewa",           "emoji":"💧","value":1000000000, "rarity":0.000005, "xp":50000000,  "kg_min":0.001,  "kg_max":100.0,    "desc":"Tetes air mata dewa yang jatuh dari langit ke-7.",               "tier":"divine"},
    "creation_spark":   {"name":"✴️ Percikan Penciptaan",     "emoji":"✴️","value":2500000000,"rarity":0.000001, "xp":100000000, "kg_min":0.0001, "kg_max":10.0,     "desc":"Percikan energi dari momen penciptaan alam semesta.",            "tier":"divine"},
    "omega_shard":      {"name":"🔱 Serpihan Omega",          "emoji":"🔱","value":1500000000,"rarity":0.000003, "xp":70000000,  "kg_min":0.1,    "kg_max":1000.0,   "desc":"Pecahan dari kekuatan Omega — akhir dari segalanya.",            "tier":"divine"},
    "infinity_gem":     {"name":"♾️ Permata Tak Terbatas",    "emoji":"♾️","value":5000000000,"rarity":0.0000005,"xp":200000000, "kg_min":1.0,    "kg_max":100000.0, "desc":"Permata yang mengandung kekuatan tak terbatas.",                 "tier":"divine"},
    "genesis_core":     {"name":"🌅 Inti Genesis",            "emoji":"🌅","value":3000000000,"rarity":0.0000008,"xp":120000000, "kg_min":5.0,    "kg_max":50000.0,  "desc":"Inti dari momen kelahiran semesta.",                             "tier":"divine"},
    "divine_essence":   {"name":"✨ Esensi Ilahi",            "emoji":"✨","value":800000000, "rarity":0.000007, "xp":35000000,  "kg_min":0.01,   "kg_max":500.0,    "desc":"Esensi murni dari para dewa.",                                   "tier":"divine"},
    "chaos_fragment":   {"name":"🌪️ Serpihan Chaos",         "emoji":"🌪️","value":2000000000,"rarity":0.000002, "xp":90000000,  "kg_min":0.5,    "kg_max":5000.0,   "desc":"Serpihan dari kekuatan chaos primordial.",                       "tier":"divine"},
}

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
    """Format berat ke string yang mudah dibaca — mendukung mg hingga ribuan ton."""
    if kg < 0.001:
        return f"{kg*1000000:.2f}mg"
    elif kg < 1.0:
        return f"{kg*1000:.1f}g"
    elif kg < 1000.0:
        return f"{kg:.2f} kg"
    elif kg < 1000000.0:
        return f"{kg/1000:.3f} ton"
    else:
        return f"{kg/1000:.1f} ton"

ITEMS: dict = {
    "energy_drink":       {"name":"🥤 Energy Drink",              "emoji":"🥤","price":2000,       "description":"Pulihkan 50 energy.",                                                 "effect":{"energy":50},                                   "stackable":True},
    "energy_potion":      {"name":"⚡ Energy Potion",              "emoji":"⚡","price":25000,       "description":"Pulihkan 100 energy seketika.",                                        "effect":{"energy":100},                                  "stackable":True},
    "mana_crystal":       {"name":"💠 Kristal Mana",               "emoji":"💠","price":50000,      "description":"Pulihkan 200 energy seketika.",                                        "effect":{"energy":200},                                  "stackable":True},
    "titan_energy":       {"name":"⚡🔥 Titan Energy",             "emoji":"⚡","price":200000,      "description":"Pulihkan PENUH energy + buff energy.",                                  "effect":{"energy":9999},                                 "stackable":True},
    "rainbow_gem":        {"name":"🌈 Rainbow Gem",                 "emoji":"🌈","price":150000,     "description":"+70% luck selama 30 menit!",                                           "effect":{"luck_buff":0.70,"duration":30},                 "stackable":True},
    "divine_luck_orb":    {"name":"🔮 Divine Luck Orb",             "emoji":"🔮","price":250000,     "description":"+100% luck selama 20 menit!",                                          "effect":{"luck_buff":1.0,"duration":20},                  "stackable":True},
    "xp_mega_boost":      {"name":"🌠 XP Mega Boost",               "emoji":"🌠","price":100000,      "description":"5x XP selama 20 menit!",                                               "effect":{"xp_mult":5.0,"duration":20},                    "stackable":True},
    "xp_nova":            {"name":"💥 XP Nova",                     "emoji":"💥","price":250000,     "description":"10x XP selama 10 menit!",                                              "effect":{"xp_mult":10.0,"duration":10},                   "stackable":True},
    "speed_boost":        {"name":"🚀 Speed Boost",                  "emoji":"🚀","price":50000,      "description":"Cooldown mining -50% selama 20 menit.",                                "effect":{"speed_boost":0.5,"duration":20},                "stackable":True},
    "turbo_boost":        {"name":"⚡ Turbo Boost",                  "emoji":"⚡","price":150000,      "description":"Cooldown mining -75% selama 15 menit!",                                "effect":{"speed_boost":0.25,"duration":15},               "stackable":True},
    "hunters_kit":        {"name":"🎯 Hunter's Kit",                "emoji":"🎯","price":85000,      "description":"2x XP + 20% luck selama 30 menit!",                                    "effect":{"xp_mult":2.0,"luck_buff":0.20,"duration":30},   "stackable":True},
    "mystery_box":        {"name":"📦 Mystery Box",                  "emoji":"📦","price":50000,      "description":"Kotak misterius! Isi acak bisa XP, item, atau ore.",                    "effect":{"mystery":True},                                 "stackable":True},
    "premium_mystery_box":{"name":"🎁 Premium Mystery Box",          "emoji":"🎁","price":150000,     "description":"Kotak premium! Dijamin item/ore berharga.",                              "effect":{"mystery_premium":True},                         "stackable":True},
    "divine_box":         {"name":"✨ Divine Mystery Box",            "emoji":"✨","price":500000,     "description":"Kotak surgawi! Kemungkinan ore mythical-divine!",                        "effect":{"mystery_divine":True},                          "stackable":True},
    "rebirth_token":      {"name":"🔄 Rebirth Token",                "emoji":"🔄","price":2500000,    "description":"Reset level ke 1. Bonus permanen: +50% XP selamanya!",                  "effect":{"rebirth":True},                                 "stackable":False},
}

ACHIEVEMENTS: dict = {
    "first_mine":        {"name":"🥇 Pertama Kali!",        "desc":"Lakukan mining pertama",               "reward":5000},
    "mine_10":           {"name":"⛏️ Penambang Pemula",     "desc":"Mining 10 kali",                       "reward":10000},
    "mine_100":          {"name":"💪 Penambang Sejati",      "desc":"Mining 100 kali",                      "reward":50000},
    "mine_1000":         {"name":"🏆 Master Miner",          "desc":"Mining 1.000 kali",                    "reward":500000},
    "mine_10000":        {"name":"👑 Legend Miner",          "desc":"Mining 10.000 kali",                   "reward":5000000},
    "mine_100000":       {"name":"🌟 God Miner",             "desc":"Mining 100.000 kali",                  "reward":50000000},
    "first_rare":        {"name":"🔮 Rare Hunter",           "desc":"Dapatkan ore rare pertama",            "reward":200000},
    "rich_100k":         {"name":"💰 Orang Kaya",            "desc":"Kumpulkan 100.000 koin",               "reward":10000},
    "rich_1m":           {"name":"💎 Jutawan",               "desc":"Kumpulkan 1.000.000 koin",             "reward":100000},
    "rich_1b":           {"name":"🏦 Miliarder",             "desc":"Kumpulkan 1 Miliar koin",              "reward":10000000},
    "rich_1t":           {"name":"👑 Triliunder",            "desc":"Kumpulkan 1 Triliun koin",             "reward":250000000},
    "lvl_10":            {"name":"⭐ Bintang 10",            "desc":"Capai Level 10",                       "reward":5000},
    "lvl_50":            {"name":"🌟 Bintang 50",            "desc":"Capai Level 50",                       "reward":50000},
    "lvl_100":           {"name":"💫 Century",               "desc":"Capai Level 100",                      "reward":500000},
    "lvl_200":           {"name":"🌙 Level 200",             "desc":"Capai Level 200",                      "reward":2500000},
    "lvl_500":           {"name":"☀️ Level 500",             "desc":"Capai Level 500",                      "reward":10000000},
    "void_shard":        {"name":"🌑 Void Seeker",           "desc":"Temukan Void Shard pertama",           "reward":500000},
    "daily_streak_7":    {"name":"🔥 7-Day Streak",          "desc":"Daily bonus 7 hari berturut",          "reward":250000},
    "daily_streak_30":   {"name":"🌙 30-Day Streak",         "desc":"Daily bonus 30 hari berturut",         "reward":2500000},
    "daily_streak_100":  {"name":"💯 100-Day Streak",        "desc":"Daily bonus 100 hari berturut!",       "reward":25000000},
    "market_first":      {"name":"🏪 Pedagang Pertama",      "desc":"Pertama kali jual di market",          "reward":10000},
    "rebirth_1":         {"name":"🔄 Reborn",                "desc":"Lakukan rebirth pertama",              "reward":1000000},
    "cosmic_find":       {"name":"🌠 Cosmic Hunter",         "desc":"Temukan Debu Kosmik",                  "reward":1000000},
    "divine_find":       {"name":"♾️ Divine Hunter",         "desc":"Temukan Batu Keabadian",               "reward":25000000},
    "heavy_miner":       {"name":"🏋️ Heavy Miner",          "desc":"Kumpulkan total 1.000 kg ore",         "reward":250000},
    "super_heavy":       {"name":"⚓ Super Heavy",           "desc":"Kumpulkan total 10.000 kg ore",        "reward":2500000},
    "kg_master":         {"name":"🌍 KG Master",             "desc":"Kumpulkan total 100.000 kg ore",       "reward":25000000},
    "ton_miner":         {"name":"🏗️ Ton Miner",            "desc":"Kumpulkan total 1.000 ton ore",        "reward":250000000},
    "mega_ton":          {"name":"⚓ Mega Ton Miner",        "desc":"Kumpulkan total 30.000 ton ore",       "reward":2500000000},
    "all_zones":         {"name":"🗺️ Penjelajah Dunia",      "desc":"Buka semua zona mining",               "reward":5000000},
    "first_mythical":    {"name":"🐉 Mythical Seeker",       "desc":"Temukan ore mythical pertama",         "reward":2500000},
    "first_cosmic":      {"name":"🌌 Cosmic Seeker",         "desc":"Temukan ore cosmic pertama",           "reward":10000000},
    "first_divine":      {"name":"🌈 Divine Seeker",         "desc":"Temukan ore divine pertama",           "reward":50000000},
    "collector_10":      {"name":"📦 Kolektor",               "desc":"Miliki 10 jenis ore berbeda",          "reward":500000},
    "collector_25":      {"name":"📦📦 Mega Kolektor",        "desc":"Miliki 25 jenis ore berbeda",          "reward":5000000},
    "tool_master":       {"name":"⚒️ Tool Master",           "desc":"Beli 10 alat berbeda",                 "reward":250000},
    "legendary_find":    {"name":"💎 Legend Hunter",         "desc":"Temukan ore legendary pertama",        "reward":500000},
    "neutron_miner":     {"name":"⚪ Neutron Miner",         "desc":"Temukan Inti Neutron",                 "reward":25000000},
    "infinity_hunter":   {"name":"♾️ Infinity Hunter",       "desc":"Temukan Permata Tak Terbatas",         "reward":250000000},
    "vip_member":        {"name":"👑 VIP Member",            "desc":"Aktifkan VIP pertama kali",            "reward":50000},
}

def xp_for_level(level: int) -> int:
    return int(200 * (level ** 1.65))

MAX_LEVEL = 500

ZONES: dict = {
    "surface":          {"name":"🏔️ Permukaan",         "desc":"Zona awal. Pebble, batu bara, dan besi.",                                "level_req":1,   "ore_bonus":{},                                                                      "unlock_cost":0,              "kg_bonus":1.0},
    "cave":             {"name":"🕯️ Gua Dalam",          "desc":"Lebih banyak besi, tembaga & perak.",                                    "level_req":5,   "ore_bonus":{"iron":1.5,"silver":1.3,"tin":1.4,"copper":1.4},                       "unlock_cost":5000,           "kg_bonus":1.1},
    "mine_shaft":       {"name":"⛏️ Sumur Tambang",      "desc":"Tambang dalam, nikel dan mangan melimpah!",                              "level_req":8,   "ore_bonus":{"nickel":1.6,"manganese":1.5,"zinc":1.4,"chromite":1.3},              "unlock_cost":20000,          "kg_bonus":1.15},
    "underground":      {"name":"⛰️ Bawah Tanah",        "desc":"Emas, safir & platinum lebih sering muncul!",                            "level_req":15,  "ore_bonus":{"gold":1.8,"sapphire":1.5,"quartz":1.6,"platinum":1.4},               "unlock_cost":50000,          "kg_bonus":1.2},
    "volcanic_field":   {"name":"🌋 Ladang Vulkanik",    "desc":"Tungsten, obsidian, dan basalt berlimpah!",                              "level_req":20,  "ore_bonus":{"tungsten":1.7,"basalt":2.0,"chromite":1.5,"sulfur":1.8},             "unlock_cost":100000,         "kg_bonus":1.25},
    "lava_cave":        {"name":"🌋 Gua Lava",            "desc":"Rubi, berlian & tanzanit lebih melimpah!",                               "level_req":25,  "ore_bonus":{"ruby":2.0,"diamond":1.7,"topaz":1.8,"tanzanite":1.9},               "unlock_cost":200000,         "kg_bonus":1.3},
    "deep_mine":        {"name":"⚫ Tambang Dalam",       "desc":"Garnet, spinel, dan turmalin berlimpah.",                                "level_req":32,  "ore_bonus":{"garnet":2.0,"spinel":1.8,"tourmaline":1.9,"zircon":1.7},             "unlock_cost":500000,         "kg_bonus":1.35},
    "crystal_cavern":   {"name":"🔮 Cavern Kristal",      "desc":"Ametis, mithril & alexandrit berlimpah!",                                "level_req":38,  "ore_bonus":{"amethyst":2.5,"mythril":2.0,"opal":2.0,"alexandrite":2.2},           "unlock_cost":800000,         "kg_bonus":1.4},
    "gem_paradise":     {"name":"💎 Surga Permata",       "desc":"Painit, benitoit, jadeite - permata super langka!",                      "level_req":44,  "ore_bonus":{"painite":2.5,"benitoite":2.3,"jadeite":2.0,"musgravite":2.5},       "unlock_cost":2000000,        "kg_bonus":1.45},
    "ancient_ruins":    {"name":"🏛️ Reruntuhan Kuno",   "desc":"Peradaban kuno. Opal dan Mithril sangat banyak!",                        "level_req":50,  "ore_bonus":{"opal":2.5,"mythril":2.5,"amethyst":2.0,"alexandrite":2.0},           "unlock_cost":3000000,        "kg_bonus":1.5},
    "dragon_lair":      {"name":"🐉 Sarang Naga",         "desc":"Dragonstone, Dragon Heart, dan Thunder Stone melimpah!",                 "level_req":58,  "ore_bonus":{"dragonstone":3.5,"dragon_heart":3.0,"thunder_stone":2.5,"ruby":2.0},"unlock_cost":10000000,       "kg_bonus":1.6},
    "void_realm":       {"name":"🌑 Void Realm",          "desc":"Dimensi lain. Void Shard, Phoenix Ash & Glacial!",                       "level_req":62,  "ore_bonus":{"dragonstone":3.0,"stardust":2.0,"void_shard":2.5,"phoenix_ash":2.0},"unlock_cost":8000000,        "kg_bonus":1.65},
    "sky_island":       {"name":"☁️ Pulau Langit",        "desc":"Stardust, Lunar Crystal & Cosmic Dust!",                                 "level_req":75,  "ore_bonus":{"stardust":3.0,"cosmic_dust":2.5,"void_shard":2.0,"lunar_crystal":2.5},"unlock_cost":30000000,      "kg_bonus":1.7},
    "frozen_core":      {"name":"🧊 Inti Beku",           "desc":"Inti bumi beku. Glacial Shard & Cursed Gem berlimpah!",                  "level_req":85,  "ore_bonus":{"glacial_shard":3.0,"cursed_gem":2.5,"lunar_crystal":2.0,"void_shard":2.0},"unlock_cost":60000000,  "kg_bonus":1.75},
    "deep_space":       {"name":"🚀 Luar Angkasa",        "desc":"Nebula Ore & Cosmic Dust melimpah!",                                     "level_req":100, "ore_bonus":{"cosmic_dust":3.5,"nebula_ore":3.0,"stardust":2.5,"dark_energy_ore":2.0},"unlock_cost":150000000,  "kg_bonus":1.8},
    "pulsar_belt":      {"name":"💫 Sabuk Pulsar",        "desc":"Pulsar Fragment & Quasar Crystal sangat tinggi!",                        "level_req":120, "ore_bonus":{"pulsar_fragment":4.0,"quasar_crystal":3.5,"gamma_crystal":3.0,"nebula_ore":2.5},"unlock_cost":400000000, "kg_bonus":1.9},
    "time_rift":        {"name":"⏳ Retakan Waktu",       "desc":"Zona di luar dimensi waktu. Kristal Waktu!",                             "level_req":150, "ore_bonus":{"time_crystal":3.0,"nebula_ore":2.5,"cosmic_dust":2.0,"dark_energy_ore":2.5},"unlock_cost":800000000, "kg_bonus":2.0},
    "antimatter_zone":  {"name":"💥 Zona Antimateri",     "desc":"Antimateri, Singularitas, Neutron Core! Ultra berbahaya!",               "level_req":180, "ore_bonus":{"antimatter_shard":4.0,"singularity_ore":3.5,"neutron_core":3.0},    "unlock_cost":3000000000,     "kg_bonus":2.2},
    "soul_realm":       {"name":"👻 Alam Jiwa",           "desc":"Alam roh kuno. Soul Fragment & Eternity Stone!",                         "level_req":200, "ore_bonus":{"soul_fragment":3.0,"eternity_stone":2.0,"void_shard":3.0,"time_crystal":2.5},"unlock_cost":5000000000, "kg_bonus":2.5},
    "genesis_realm":    {"name":"🌅 Alam Genesis",        "desc":"Tempat penciptaan. Universe Core, God Tear, Creation Spark!",            "level_req":350, "ore_bonus":{"universe_core":2.0,"eternity_stone":2.5,"god_tear":3.0,"creation_spark":3.5,"omega_shard":3.0,"infinity_gem":2.5},"unlock_cost":10000000000,"kg_bonus":3.0},
}

TIER_COLORS = {1:"⚪️",2:"🟢",3:"🔵",4:"🟠",5:"🔴",6:"💜",7:"🌟",8:"🌈"}
ORE_TIER_COLORS = {"common":"⚪️","uncommon":"🟢","rare":"🔵","epic":"🟠","legendary":"🔴","mythical":"💜","cosmic":"🌟","divine":"🌈"}

MARKET_FEE_PERCENT = 5
