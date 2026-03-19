# ⛏️ MiningBot

Bot mining Telegram berbasis Python dengan sistem RPG lengkap — tambang ore, upgrade alat, jual di market, dan raih status VIP!

---

## 📋 Daftar Isi

- [Fitur Utama](#-fitur-utama)
- [Statistik Game](#-statistik-game)
- [Instalasi](#-instalasi)
- [Konfigurasi](#-konfigurasi)
- [Deploy ke Railway](#-deploy-ke-railway)
- [Struktur File](#-struktur-file)
- [Sistem VIP](#-sistem-vip)
- [Sistem Top Up](#-sistem-top-up)
- [Perintah Admin](#-perintah-admin)
- [Perintah Pemain](#-perintah-pemain)
- [Sistem Game](#-sistem-game)
- [FAQ](#-faq)

---

## 🚀 Fitur Utama

| Fitur | Keterangan |
|-------|------------|
| ⛏️ **Mining System** | Tambang 113 jenis ore dari Kerikil hingga Permata Tak Terbatas |
| ⚖️ **KG System** | Setiap ore punya berat nyata hingga **100.000 KG** |
| 🔧 **48 Alat Mining** | Tier 1 Starter s/d Tier 8 Divine, cooldown 6s → 1s |
| ⚡ **Energy System** | Regen otomatis tiap 5 menit, upgradeable hingga 5.000 |
| 🌍 **20 Zona Mining** | Dari Permukaan hingga Alam Genesis |
| 🏪 **Market** | Jual beli ore antar pemain dengan fee 5% |
| 👑 **VIP System** | Cooldown lebih cepat, energy lebih cepat, luck & crit lebih tinggi |
| 💰 **Top Up Saldo** | Beli koin via transfer bank (6 paket) |
| 🎁 **Daily Bonus** | Bonus harian dengan streak multiplier |
| 🏆 **Leaderboard** | Papan peringkat top miner |
| 🏅 **40 Achievement** | Raih prestasi & reward koin |
| 🏛️ **Museum** | Pamerkan ore langka koleksimu |
| ⭐ **Favorit** | Tandai ore favoritmu |
| 📊 **Admin Panel** | Kelola user, beri VIP, broadcast, statistik |

---

## 📊 Statistik Game

### Alat Mining (48 total)

| Tier | Nama | Jumlah | Cooldown | Syarat |
|------|------|--------|----------|--------|
| 1 | Starter | 3 | 6 detik | Tidak ada |
| 2 | Basic | 6 | 5 detik | Tidak ada |
| 3 | Advanced | 6 | 4 detik | Tidak ada |
| 4 | Expert | 8 | 3 detik | Tidak ada |
| 5 | Master | 8 | 2 detik | Tidak ada |
| 6 | Legendary | 7 | 2 detik | Sedikit ore |
| 7 | Mythical | 5 | 1 detik | Sedikit ore |
| 8 | Divine | 5 | 1 detik | Sedikit ore |

> ✅ Semua alat **tidak membutuhkan level**. Beli kapan saja!
> Alat Tier 6+ hanya butuh **sedikit ore** (maks 20 ore).

### Ore (113 total)

| Tier | Jumlah | Contoh |
|------|--------|--------|
| Common | 15 | Kerikil, Batu Bara, Granit |
| Uncommon | 15 | Besi, Tembaga, Nikel |
| Rare | 15 | Emas, Platinum, Tungsten |
| Epic | 15 | Rubi, Berlian, Tanzanit |
| Legendary | 14 | Berlian, Ametis, Mithril |
| Mythical | 15 | Batu Naga, Void Shard, Jantung Naga |
| Cosmic | 14 | Debu Kosmik, Bijih Nebula, Kristal Waktu |
| Divine | 10 | Pecahan Jiwa, Batu Keabadian, Inti Semesta |

**KG Range:** 0.001 gram hingga **100.000 KG** per ore tergantung jenis.

### Zona Mining (20 total)

| Zona | Level | Biaya | Ore Unggulan |
|------|-------|-------|--------------|
| 🏔️ Permukaan | 1 | Gratis | Batu, Besi, Batu Bara |
| 🕯️ Gua Dalam | 5 | 5.000 | Besi, Perak, Tembaga |
| ⛏️ Sumur Tambang | 8 | 20.000 | Nikel, Mangan, Zinc |
| 🌋 Gua Lava | 25 | 200.000 | Rubi, Berlian, Tanzanit |
| 🐉 Sarang Naga | 58 | 10.000.000 | Batu Naga, Jantung Naga |
| 🌑 Void Realm | 62 | 8.000.000 | Void Shard, Phoenix Ash |
| 🚀 Luar Angkasa | 100 | 150.000.000 | Debu Kosmik, Bijih Nebula |
| ⏳ Retakan Waktu | 150 | 800.000.000 | Kristal Waktu |
| 👻 Alam Jiwa | 200 | 5.000.000.000 | Pecahan Jiwa, Batu Keabadian |
| 🌅 Alam Genesis | 350 | 20.000.000.000 | Inti Semesta, Air Mata Dewa |

---

## 🛠️ Instalasi

### Persyaratan

- Python **3.11+**
- pip
- Token bot Telegram (dari [@BotFather](https://t.me/BotFather))

### Langkah Instalasi

```bash
# 1. Clone atau ekstrak project
cd MiningBot_v6

# 2. Install dependensi
pip install -r requirements.txt

# 3. Buat file .env
cp .env.example .env

# 4. Edit .env (lihat bagian Konfigurasi)
nano .env

# 5. Jalankan bot
python bot.py
```

---

## ⚙️ Konfigurasi

Edit file `.env` sebelum menjalankan bot:

```env
# ── WAJIB ──────────────────────────────────────────────
# Token bot dari @BotFather
BOT_TOKEN=1234567890:ABCDEFGhijklmnopqrstuvwxyz

# ID Telegram admin (pisah koma jika lebih dari 1)
ADMIN_IDS=123456789,987654321

# ── OPSIONAL ───────────────────────────────────────────
# Path database SQLite
DATABASE_URL=mining_bot.db

# Info rekening untuk pembelian VIP
VIP_TRANSFER_INFO=Bank BCA: 1234567890 a/n Nama Anda

# Info rekening untuk top up saldo
TOPUP_TRANSFER_INFO=Bank BCA: 1234567890 a/n Nama Anda
```

### Cara Mendapatkan Admin ID

1. Kirim pesan ke [@userinfobot](https://t.me/userinfobot)
2. Salin angka `Id:` yang diberikan
3. Masukkan ke `ADMIN_IDS` di `.env`

---

## 🚂 Deploy ke Railway

Bot sudah siap deploy ke [Railway](https://railway.app):

1. Push project ke GitHub
2. Buat project baru di Railway → **Deploy from GitHub**
3. Tambahkan variabel environment di tab **Variables**:
   - `BOT_TOKEN`
   - `ADMIN_IDS`
   - `VIP_TRANSFER_INFO`
   - `TOPUP_TRANSFER_INFO`
4. Railway akan otomatis menjalankan `python bot.py`

> File `railway.toml` dan `nixpacks.toml` sudah dikonfigurasi — tidak perlu setting tambahan.

---

## 📁 Struktur File

```
MiningBot_v6/
├── bot.py                  # Entry point utama
├── config.py               # Konfigurasi game (alat, ore, VIP, zona)
├── database.py             # Manajemen database SQLite
├── game.py                 # Engine game (mining, XP, energy, buff)
├── keyboards.py            # Semua keyboard inline & reply
├── middlewares.py          # Middleware bot
├── requirements.txt        # Dependensi Python
├── .env.example            # Template environment variables
├── Procfile                # Untuk deployment
├── railway.toml            # Konfigurasi Railway
├── nixpacks.toml           # Build config
└── handlers/
    ├── __init__.py
    ├── admin.py            # Panel admin & perintah admin
    ├── bag.py              # Manajemen bag & penjualan ore
    ├── daily.py            # Bonus harian
    ├── equipment.py        # Manajemen alat mining
    ├── favorite_museum.py  # Ore favorit & museum
    ├── help.py             # Bantuan & panduan
    ├── inventory.py        # Inventaris & penggunaan item
    ├── leaderboard.py      # Papan peringkat
    ├── market.py           # Market jual beli ore
    ├── mining.py           # Handler mining utama
    ├── profile.py          # Profil pemain
    ├── shop.py             # Toko alat, item, zona
    ├── start.py            # Registrasi & menu utama
    └── vip.py              # Sistem VIP & top up saldo
```

---

## 👑 Sistem VIP

### Keuntungan VIP

| Bonus | Nilai |
|-------|-------|
| ⏱️ Cooldown mining | **15% lebih cepat** |
| ⚡ Energy regen | **+2 energy per tick** |
| 🍀 Luck bonus | **+3%** |
| 💥 Critical bonus | **+2%** |
| 👑 Badge VIP | Muncul di profil & panel mining |

### Paket VIP

| Paket | Harga | Durasi |
|-------|-------|--------|
| 1 Bulan | Rp 25.000 | 30 hari |
| 3 Bulan | Rp 65.000 | 90 hari |
| 6 Bulan | Rp 120.000 | 180 hari |
| Lifetime | Rp 200.000 | Selamanya |

### Alur Pembelian VIP

```
Pemain → Shop → 👑 VIP Member
       → Pilih Paket
       → Lihat info rekening transfer
       → Transfer sesuai nominal
       → Klik "Sudah Transfer" → Kirim foto bukti
       → Bot forward bukti ke admin
       → Admin verifikasi → /admin_givevip <id> <plan>
       → Pemain dapat notifikasi VIP aktif ✅
```

### Cara Admin Mengaktifkan VIP

```
/admin_givevip 123456789 1_month
/admin_givevip 123456789 3_months
/admin_givevip 123456789 6_months
/admin_givevip 123456789 lifetime
```

> VIP akan otomatis *extend* jika pemain sudah punya VIP aktif.

---

## 💰 Sistem Top Up Saldo

### Paket Top Up

| Paket | Harga | Koin |
|-------|-------|------|
| Paket Starter | Rp 10.000 | 10 Juta Koin |
| Paket Bronze | Rp 25.000 | 30 Juta Koin |
| Paket Silver | Rp 50.000 | 75 Juta Koin |
| Paket Gold | Rp 100.000 | 200 Juta Koin |
| Paket Platinum | Rp 200.000 | 500 Juta Koin |
| Paket Diamond 💎 | Rp 500.000 | 2 Milyar Koin |

### Alur Top Up

```
Pemain → Shop → 💰 Top Up Saldo
       → Pilih Paket
       → Transfer ke rekening
       → Kirim foto bukti transfer
       → Admin cek → /admin_addcoin <id> <jumlah>
       → Saldo pemain bertambah ✅
```

---

## 🔐 Perintah Admin

### Manajemen User

```
/adminhelp                          — Lihat semua perintah admin
/admin_info <user_id>               — Lihat info lengkap user
/admin_addcoin <user_id> <jumlah>  — Tambah koin ke user
/admin_setlevel <user_id> <level>  — Set level user
/admin_setenergy <user_id> <val>   — Set energy user
/admin_reset <user_id>             — Reset data user ke awal
```

### Pemberian Item & Alat

```
/admin_givetool <user_id> <tool_id>           — Beri alat mining
/admin_giveitem <user_id> <item_id> <qty>     — Beri item
/admin_giveore <user_id> <ore_id> <qty>       — Beri ore
/admin_givezone <user_id> <zone_id>           — Buka zona
```

### VIP Management

```
/admin_givevip <user_id> <plan_id>   — Aktifkan VIP
/admin_revokevip <user_id>           — Cabut VIP
```

**Plan ID:** `1_month` | `3_months` | `6_months` | `lifetime`

### Statistik & Broadcast

```
/admin_stats              — Statistik bot (total user, dll)
/admin_users              — Daftar semua user
/admin_broadcast <pesan>  — Kirim pesan ke semua user
```

### Foto & Media

```
/admin_setphoto           — Upload foto profil admin
/admin_myphotos           — Lihat foto admin
/admin_deletephoto <id>   — Hapus foto admin
/admin_setorephoto <ore_id>    — Pasang foto untuk ore tertentu
/admin_listorephoto            — Daftar ore yang punya foto
/admin_delorephoto <ore_id>    — Hapus foto ore
```

### Referensi ID

```
/admin_tools    — Daftar semua tool_id
/admin_items    — Daftar semua item_id
/admin_zones    — Daftar semua zone_id
/admin_ores     — Daftar semua ore_id
```

### Keistimewaan Admin

- ⚡ Energy tidak pernah berkurang
- 💰 Beli alat & item tanpa biaya
- 🌍 Buka zona tanpa biaya & level
- ⏱️ Cooldown mining hanya **1 detik**
- 🪨 Beli alat Legendary+ tanpa ore

---

## 🎮 Perintah Pemain

### Utama

```
/start          — Menu utama & registrasi
/mine           — Panel mining
/bag            — Lihat & jual ore di bag
/shop           — Toko alat, item, zona, VIP, top up
/profile        — Profil & statistik kamu
/inventory      — Pakai item consumable
/market         — Pasar jual beli ore antar pemain
/daily          — Klaim bonus harian
/leaderboard    — Papan peringkat
/vip            — Cek status VIP
/help           — Panduan lengkap
```

### Upgrade

```
/buyenergy    — Beli +100 max energy
/energyinfo   — Info harga upgrade energy
/buyslot      — Beli +10 slot bag
/slotinfo     — Info harga upgrade slot bag
```

### Koleksi

```
/favorite     — Lihat & kelola ore favorit
/museum       — Museum ore langka kamu
/equipment    — Lihat alat yang dimiliki
```

---

## 🎯 Sistem Game

### Mining

- Cooldown dasar **6 detik** (Tier 1), makin tinggi tier makin cepat hingga **1 detik**
- Tersedia **x1 / x5 / x10 / x25 / x50** untuk semua pemain
- Setiap mining menghasilkan **1 jenis ore** secara acak berdasarkan rarity
- Hasil mining langsung masuk ke **Bag**

### Cara Mendapat Koin

```
Mining ore → Masuk Bag → Jual di Bag atau Market → Dapat Koin
```

> Mining **tidak** langsung menghasilkan koin. XP didapat dari mining, koin didapat dari menjual ore.

### Critical & Lucky

| Event | Trigger | Efek |
|-------|---------|------|
| 💥 Critical | Base 10% + bonus alat + VIP | XP ×2, KG ×1.5 |
| 🍀 Lucky | Base 5% + bonus alat + VIP | XP ×1.5, KG ×1.2 |

### Sistem XP & Level

- XP didapat dari mining (berdasarkan nilai ore + berat KG)
- Level naik otomatis saat XP cukup
- Max level: **500**
- Formula: `XP_needed = 200 × level^1.65`
- Rebirth Token: reset ke level 1, tapi dapat **+50% XP permanent**

### Energy

- Berkurang setiap mining (berdasarkan alat)
- Regen otomatis **tiap 5 menit** (+10 energy, +12 untuk VIP)
- Max energy default: **500**, bisa diupgrade hingga **5.000**
- Daily bonus: langsung isi energy **penuh**

### Bag

- Kapasitas default: **50 slot**
- Max slot: **500** (upgrade via `/buyslot`)
- KG capacity: unlimited (sudah diset sangat tinggi)

### Market

- Fee penjualan: **5%**
- Semua pemain bisa listing dan beli ore dari pemain lain
- Harga ditentukan penjual

---

## ❓ FAQ

**Q: Bagaimana cara dapat koin?**
A: Mining ore → masuk bag → jual di Bag (`/bag`) atau Market (`/market`).

**Q: Apakah ada syarat level untuk beli alat?**
A: **Tidak ada!** Semua alat bisa dibeli kapan saja tanpa syarat level.

**Q: Apa yang dibutuhkan untuk beli alat Tier 6+?**
A: Hanya sedikit ore tertentu (maks 16 ore total), tidak butuh level.

**Q: Kenapa XP mining saya sama saja meski ganti alat?**
A: Sengaja! Alat tidak lagi memberikan bonus XP multiplier. XP murni dari jenis & berat ore yang ditambang. Upgrade alat untuk cooldown lebih cepat dan ore lebih berat.

**Q: Berapa lama VIP diaktifkan setelah transfer?**
A: Maksimal **1×24 jam** setelah bukti diterima admin.

**Q: Apakah VIP bisa di-extend?**
A: Ya! Jika kamu beli VIP saat masih aktif, durasi akan ditambahkan dari sisa waktu yang ada.

**Q: Bot tidak merespons, kenapa?**
A: Pastikan `BOT_TOKEN` benar di `.env`, dan bot tidak sedang berjalan di tempat lain.

**Q: Database disimpan di mana?**
A: File `mining_bot.db` di direktori yang sama dengan `bot.py`. Backup file ini secara rutin!

---

## 🛡️ Keamanan

- Semua command admin diproteksi dengan pengecekan `ADMIN_IDS`
- Database menggunakan WAL mode untuk performa & keamanan
- Bukti transfer dikirim langsung ke admin, tidak disimpan di database

---

## 📦 Dependensi

```
aiogram==3.7.0       # Framework bot Telegram async
aiosqlite==0.20.0    # Database SQLite async
python-dotenv==1.0.1 # Load environment variables
```

---

## 📝 Changelog

### v6 ULTIMATE
- ✅ KG ore max dinaikkan hingga 100.000 KG
- ✅ Energy regen dipercepat: 10 menit → 5 menit
- ✅ Ore ditambah: 38 → 113 jenis
- ✅ Alat ditambah: 25 → 48 alat
- ✅ Semua alat tidak butuh level
- ✅ Ore requirement alat Tier 6+ dikurangi drastis
- ✅ XP bonus dari alat dihapus (fairness)
- ✅ Cooldown base 6 detik (Tier 1) → 1 detik (Tier 8)
- ✅ Mining x25 dan x50 tersedia untuk semua pemain
- ✅ Sistem VIP dengan 4 paket
- ✅ Shop VIP & Top Up via transfer bank
- ✅ Admin command: `/admin_givevip` & `/admin_revokevip`
- ✅ Zero syntax error di semua 19 file

---

## 📞 Support

Untuk pertanyaan dan bantuan, hubungi admin bot langsung melalui Telegram.

---

*MiningBot v6 ULTIMATE — Dibuat dengan ❤️ menggunakan Python & aiogram*
