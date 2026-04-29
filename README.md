# 📸 Instagram Scraper API

API untuk scraping post & komentar Instagram, filter komentar negatif, dan export ke Excel.

---

## 🗂️ Struktur File

```
instagram-api/
├── main.py             ← API utama (FastAPI)
├── scraper.py          ← Logic scraping Instagram
├── database.py         ← Simpan data ke SQLite
├── filter_negatif.py   ← Filter komentar negatif
├── export_excel.py     ← Export ke Excel (.xlsx)
├── requirements.txt    ← Daftar library
└── README.md           ← Panduan ini
```

---

## ⚙️ Instalasi

### 1. Install Python (minimal 3.9)
Download di: https://python.org

### 2. Install dependencies
Buka terminal/cmd di folder ini, lalu:
```bash
pip install -r requirements.txt
```

### 3. Jalankan server
```bash
uvicorn main:app --reload --port 8000
```

### 4. Buka Swagger UI
Buka browser: **http://localhost:8000/docs**

---

## 🚀 Cara Pakai (Urutan yang Benar)

### Step 1 — Login Instagram
```
POST http://localhost:8000/login
Body: {"username": "akun_kamu", "password": "password_kamu"}
```

### Step 2 — Scrape Post by Keyword
```
GET http://localhost:8000/scrape/hashtag?keyword=targetmu&limit=100
```

### Step 3 — Scrape Komentar dari 1 Post
```
GET http://localhost:8000/scrape/comments?shortcode=AbCdEfG123&limit=50
```

### Step 4 — Scrape Batch (Post + Komentar Sekaligus)
```
GET http://localhost:8000/scrape/batch?keyword=targetmu&post_limit=20&comment_limit=30
```
⚠️ Gunakan nilai kecil dulu untuk test sebelum ribuan.

### Step 5 — Lihat Data Tersimpan
```
GET http://localhost:8000/data/posts?keyword=targetmu
GET http://localhost:8000/data/comments?only_negative=true
```

### Step 6 — Filter Komentar Negatif
```
GET http://localhost:8000/filter?keyword=targetmu
```

### Step 7 — Export ke Excel
```
GET http://localhost:8000/export/excel?keyword=targetmu
```
File Excel akan otomatis terdownload dengan 4 sheet:
- 📊 Dashboard (ringkasan)
- 📄 Semua Post
- 🔴 Komentar Negatif
- 💬 Semua Komentar

### Step 8 — Tambah Kata Negatif Baru
```
POST http://localhost:8000/kata-negatif/tambah
Body: {"kata": "kata_baru"}
```

---

## 📊 Contoh Shortcode

URL Post Instagram:
```
https://www.instagram.com/p/AbCdEfG123/
                                ^^^^^^^^^
                              ini shortcodenya
```

---

## ⚠️ Tips Anti-Ban

1. Jangan scrape terlalu cepat (sudah ada delay otomatis)
2. Mulai dengan limit kecil (50-100) untuk test
3. Jangan pakai akun utama — buat akun khusus scraping
4. Jeda istirahat tiap 1-2 jam jika scraping massal
5. Gunakan koneksi berbeda (VPN) jika mulai kena rate-limit

---

## 🔴 Kata Negatif yang Sudah Ada

Cek file `filter_negatif.py` bagian `KATA_NEGATIF` untuk melihat
semua kata yang sudah terdaftar. Bisa ditambah via endpoint atau
langsung edit file tersebut.
"# Instacraw" 
