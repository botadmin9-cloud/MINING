# ⛏️ Mining Bot v2 — Telegram

Bot mining Telegram lengkap dengan sistem ore, market, level, zona, dan banyak fitur seru!

## 🚀 Cara Deploy ke Railway

### 1. Siapkan Bot Token
- Buka [@BotFather](https://t.me/BotFather) di Telegram
- Ketik `/newbot` dan ikuti instruksi
- Salin **BOT_TOKEN** yang diberikan

### 2. Dapatkan Telegram ID Admin
- Buka [@userinfobot](https://t.me/userinfobot)
- Kirim pesan apapun
- Salin **ID** yang diberikan

### 3. Deploy ke Railway
1. Push kode ini ke GitHub repository
2. Buka [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo**
3. Pilih repository ini
4. Di menu **Variables**, tambahkan:
   ```
   BOT_TOKEN = token_bot_kamu
   ADMIN_IDS = id_telegram_kamu
   ```
5. Railway akan otomatis build dan deploy!

### 4. Verifikasi
- Buka bot di Telegram
- Ketik `/start`
- Jika berhasil, bot akan menyapa kamu!

---

## ⚙️ Environment Variables

| Variable | Wajib | Keterangan |
|----------|-------|------------|
| `BOT_TOKEN` | ✅ | Token dari @BotFather |
| `ADMIN_IDS` | ✅ | ID Telegram admin, pisah koma jika lebih dari 1 |
| `DATABASE_URL` | ❌ | Path database (default: `mining_bot.db`) |

---

## 🎮 Fitur

### ⛏️ Mining
- Mine tunggal, x5, x10
- Cooldown mining berdasarkan alat (murah = lambat, mahal = cepat, min 5 detik)
- Keterangan ore yang ditemukan
- System energy dengan cooldown 10 menit/energy

### 🔧 Alat Mining (16 Alat, 7 Tier)
- **Tier 1 Starter**: Beliung Batu (Gratis)
- **Tier 2 Basic**: Beliung Tembaga, Besi, Perak
- **Tier 3 Advanced**: Bor Baja, Listrik, Sonic
- **Tier 4 Expert**: Pneumatic, Diamond, Titanium
- **Tier 5 Master**: Laser Cutter, Plasma Drill, Photon
- **Tier 6 Legendary**: Quantum Miner, Void Extractor, Dark Matter *(Butuh Ore!)*
- **Tier 7 Mythical**: Celestial Hammer, God's Hammer *(Butuh Ore!)*

### 🪨 Ore (22 Jenis)
Dari Batu Bara → Kristal Waktu, masing-masing dengan deskripsi unik!

### 🌍 Zona Mining (10 Zona)
Permukaan → Gua Dalam → Bawah Tanah → Gua Lava → Cavern Kristal → Reruntuhan Kuno → Void Realm → Pulau Langit → Luar Angkasa → Retakan Waktu

### 🛒 Market Ore
- Jual ore ke pemain lain dengan harga bebas
- Listing fee 5%
- Notifikasi ke penjual & pembeli beserta Telegram ID
- Batalkan listing kapan saja

### 👑 Admin Privileges
- Energy tidak berkurang
- Semua pembelian gratis (alat, item, zona)
- Speed mining 1 detik
- Tidak perlu ore untuk beli alat Legendary
- Upload foto admin via `/admin_setphoto`
- Perintah `/adminhelp` tersembunyi dari non-admin

### 🔄 Rebirth System
- Tersedia hanya di Level **500** (level maksimal)
- Reset level ke 1, dapat +50% permanent coin bonus
- Tidak ada batas jumlah rebirth

---

## 📋 Daftar Perintah

### Umum
| Perintah | Keterangan |
|----------|------------|
| `/start` | Mulai / menu utama |
| `/mine` | Panel mining |
| `/shop` | Toko |
| `/profile` | Profil kamu |
| `/inventory` | Inventaris item |
| `/market` | Pasar ore |
| `/daily` | Bonus harian |
| `/leaderboard` | Papan peringkat |
| `/help` | Bantuan |

### Admin (Tersembunyi dari non-admin)
| Perintah | Keterangan |
|----------|------------|
| `/adminhelp` | Daftar perintah admin |
| `/admin_setphoto` | Upload foto admin |
| `/admin_myphotos` | Lihat foto tersimpan |
| `/admin_deletephoto <id>` | Hapus foto |
| `/admin_info <uid>` | Info user |
| `/admin_addcoin <uid> <jumlah>` | Tambah koin |
| `/admin_setlevel <uid> <level>` | Set level |
| `/admin_setenergy <uid> <jumlah>` | Set energy |
| `/admin_givetool <uid> <tool_id>` | Beri alat |
| `/admin_giveitem <uid> <item_id> [qty]` | Beri item |
| `/admin_givezone <uid> <zone_id>` | Buka zona |
| `/admin_reset <uid>` | Reset user |
| `/admin_broadcast <pesan>` | Broadcast ke semua |
| `/admin_stats` | Statistik bot |
| `/admin_users` | Daftar user |
| `/admin_tools` | Daftar tool ID |
| `/admin_items` | Daftar item ID |
| `/admin_zones` | Daftar zone ID |
| `/admin_ores` | Daftar ore ID |

---

## 🗂️ Struktur File

```
miningbot_v2/
├── bot.py              # Entry point utama
├── config.py           # Konfigurasi game (alat, ore, zona, dll)
├── database.py         # Semua operasi database SQLite
├── game.py             # Engine game (mining, level, buff, dll)
├── keyboards.py        # Semua tombol inline & reply
├── middlewares.py      # Auto-register user
├── requirements.txt    # Dependencies Python
├── Procfile            # Untuk Railway/Heroku
├── railway.toml        # Konfigurasi Railway
├── nixpacks.toml       # Build config
├── .env.example        # Template environment variables
├── .gitignore
└── handlers/
    ├── start.py        # /start, menu utama
    ├── mining.py       # Mining, equip, zona
    ├── shop.py         # Toko alat, item, zona
    ├── profile.py      # Profil, statistik, ore inventory
    ├── inventory.py    # Inventaris item
    ├── equipment.py    # Equipment
    ├── daily.py        # Daily bonus
    ├── leaderboard.py  # Papan peringkat
    ├── help.py         # Bantuan
    ├── admin.py        # Panel admin
    └── market.py       # Market ore
```
