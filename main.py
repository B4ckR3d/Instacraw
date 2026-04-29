from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import json

from scraper import login, scrape_by_hashtag, scrape_comments, scrape_all_comments_from_posts
from database import init_db, get_all_posts, get_comments, get_stats
from filter_negatif import filter_comments, tambah_kata_negatif
from export_excel import export_ke_excel

# ============================================================
app = FastAPI(
    title="📸 Instagram Scraper API",
    description="API untuk scraping post & komentar Instagram + filter negatif + export Excel",
    version="2.0.0"
)

init_db()

# ============================================================
# Models
# ============================================================
class LoginRequest(BaseModel):
    username: str
    password: str

class TambahKataRequest(BaseModel):
    kata: str

# ============================================================
# ROOT
# ============================================================
@app.get("/", tags=["Info"])
def root():
    return {
        "app":     "Instagram Scraper API",
        "version": "2.0",
        "docs":    "Buka /docs untuk Swagger UI",
        "endpoints": [
            "POST /login",
            "GET  /scrape/hashtag?keyword=xxx&limit=100",
            "GET  /scrape/comments?shortcode=xxx&limit=50",
            "GET  /scrape/batch?keyword=xxx&post_limit=50&comment_limit=30",
            "GET  /data/posts?keyword=xxx",
            "GET  /data/comments?only_negative=true",
            "GET  /filter?keyword=xxx",
            "GET  /export/excel?keyword=xxx",
            "POST /kata-negatif/tambah",
            "GET  /stats",
        ]
    }

# ============================================================
# LOGIN
# ============================================================
@app.post("/login", tags=["Auth"])
def do_login(req: LoginRequest):
    """Login ke akun Instagram kamu"""
    success = login(req.username, req.password)
    if not success:
        raise HTTPException(status_code=401, detail="Login gagal. Cek username/password.")
    return {"status": "ok", "message": f"Login berhasil sebagai @{req.username}"}

# ============================================================
# SCRAPE POST
# ============================================================
@app.get("/scrape/hashtag", tags=["Scraping"])
def scrape_hashtag(keyword: str, limit: int = 50):
    """
    Scrape post berdasarkan hashtag/keyword.
    - keyword : hashtag tanpa #  (contoh: beritanegatif)
    - limit   : jumlah post (default 50, max bebas tapi hati-hati ban)
    """
    hasil = scrape_by_hashtag(keyword, limit)
    return {
        "keyword": keyword,
        "total":   len(hasil),
        "data":    hasil
    }

# ============================================================
# SCRAPE KOMENTAR
# ============================================================
@app.get("/scrape/comments", tags=["Scraping"])
def scrape_post_comments(shortcode: str, limit: int = 50):
    """
    Scrape + filter komentar dari 1 post.
    - shortcode : kode unik post (dari URL instagram.com/p/SHORTCODE/)
    - limit     : jumlah komentar
    """
    comments = scrape_comments(shortcode, limit)
    filtered = filter_comments(comments)
    return {
        "post_url":  f"https://www.instagram.com/p/{shortcode}/",
        "summary":   filtered["summary"],
        "negative":  filtered["negative"],
        "positive":  filtered["positive"],
    }

# ============================================================
# SCRAPE BATCH (POST + SEMUA KOMENTAR)
# ============================================================
@app.get("/scrape/batch", tags=["Scraping"])
def scrape_batch(keyword: str, post_limit: int = 20, comment_limit: int = 30):
    """
    Scrape post + komentar sekaligus (batch).
    Cocok untuk kumpulan ribuan data.
    ⚠️ Proses lama — gunakan nilai kecil dulu untuk test.
    """
    print(f"\n🚀 BATCH SCRAPE START | keyword={keyword} | post={post_limit} | comment={comment_limit}")

    # 1. Kumpulkan post
    posts = scrape_by_hashtag(keyword, post_limit)

    # 2. Kumpulkan komentar dari setiap post
    all_comments = scrape_all_comments_from_posts(posts, comment_limit)

    # 3. Filter
    filtered = filter_comments(all_comments)

    return {
        "keyword":          keyword,
        "total_post":       len(posts),
        "total_komentar":   len(all_comments),
        "summary_negatif":  filtered["summary"],
        "komentar_negatif": filtered["negative"][:50],   # preview 50 pertama
    }

# ============================================================
# DATA TERSIMPAN
# ============================================================
@app.get("/data/posts", tags=["Data"])
def lihat_posts(keyword: str = None):
    """Lihat semua post yang sudah discrape & tersimpan di DB"""
    rows = get_all_posts(keyword)
    posts = [
        {"id": r[0], "shortcode": r[1], "url": r[2], "username": r[3],
         "caption": r[4], "likes": r[5], "comments": r[6], "tanggal": r[7], "keyword": r[8]}
        for r in rows
    ]
    return {"total": len(posts), "data": posts}

@app.get("/data/comments", tags=["Data"])
def lihat_comments(post_url: str = None, only_negative: bool = False):
    """Lihat komentar tersimpan, bisa filter hanya negatif"""
    rows = get_comments(post_url, only_negative)
    comments = [
        {"id": r[0], "post_url": r[1], "shortcode": r[2],
         "username": r[3], "text": r[4], "is_negative": r[5]}
        for r in rows
    ]
    return {"total": len(comments), "data": comments}

# ============================================================
# FILTER KOMENTAR NEGATIF
# ============================================================
@app.get("/filter", tags=["Filter"])
def filter_dari_db(keyword: str = None):
    """
    Ambil semua komentar dari DB lalu filter mana yang negatif.
    """
    rows = get_comments()
    comments = [
        {"post_url": r[1], "username": r[3], "text": r[4], "is_negative": r[5]}
        for r in rows
    ]
    hasil = filter_comments(comments)
    return {
        "summary":   hasil["summary"],
        "negative":  hasil["negative"],
    }

@app.post("/kata-negatif/tambah", tags=["Filter"])
def tambah_kata(req: TambahKataRequest):
    """Tambah kata negatif baru ke daftar filter"""
    berhasil = tambah_kata_negatif(req.kata)
    if berhasil:
        return {"status": "ok", "message": f"Kata '{req.kata}' berhasil ditambahkan"}
    return {"status": "skip", "message": f"Kata '{req.kata}' sudah ada di daftar"}

# ============================================================
# EXPORT EXCEL
# ============================================================
@app.get("/export/excel", tags=["Export"])
def export_excel(keyword: str = None):
    """
    Export semua data ke file Excel (.xlsx):
    - Sheet Dashboard (ringkasan)
    - Sheet Semua Post
    - Sheet Komentar Negatif
    - Sheet Semua Komentar
    """
    # Ambil posts
    rows_post = get_all_posts(keyword)
    posts = [
        {"shortcode": r[1], "url": r[2], "username": r[3], "caption": r[4],
         "likes": r[5], "comments": r[6], "tanggal": r[7], "keyword": r[8]}
        for r in rows_post
    ]

    # Ambil semua komentar
    rows_kom = get_comments()
    semua_komentar = [
        {"post_url": r[1], "shortcode": r[2], "username": r[3], "text": r[4], "is_negative": r[5]}
        for r in rows_kom
    ]

    # Komentar negatif saja
    rows_neg = get_comments(only_negative=True)
    komentar_negatif = [
        {"post_url": r[1], "shortcode": r[2], "username": r[3],
         "text": r[4], "negative_score": 1}
        for r in rows_neg
    ]

    stats = get_stats()

    filename = export_ke_excel(
        posts=posts,
        semua_komentar=semua_komentar,
        komentar_negatif=komentar_negatif,
        stats=stats,
        keyword=keyword or "semua",
    )

    return FileResponse(
        path=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=filename
    )

# ============================================================
# EXPORT JSON
# ============================================================
@app.get("/export/json", tags=["Export"])
def export_json(keyword: str = None):
    """Export data ke JSON"""
    rows = get_all_posts(keyword)
    data = [
        {"url": r[2], "username": r[3], "caption": r[4],
         "likes": r[5], "comments": r[6], "tanggal": r[7]}
        for r in rows
    ]
    filename = f"export_{keyword or 'semua'}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return {"message": f"Tersimpan di {filename}", "total": len(data), "filename": filename}

# ============================================================
# STATS
# ============================================================
@app.get("/stats", tags=["Info"])
def statistik():
    """Lihat ringkasan statistik semua data di database"""
    return get_stats()
