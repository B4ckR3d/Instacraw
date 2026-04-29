import instaloader
import time
import random
from database import save_post, save_comment
from filter_negatif import is_negative, get_negative_score

# ============================================================
# Inisialisasi Instaloader
# ============================================================
L = instaloader.Instaloader(
    sleep=True,
    quiet=True,
    request_timeout=30,
    max_connection_attempts=3,
)

_logged_in = False

def login(username: str, password: str) -> bool:
    global _logged_in
    try:
        L.login(username, password)
        _logged_in = True
        print(f"✅ Login berhasil: {username}")
        return True
    except Exception as e:
        print(f"❌ Login gagal: {e}")
        return False

def cek_login():
    if not _logged_in:
        raise Exception("Belum login! Panggil /login dulu.")

# ============================================================
# Scrape Post by Hashtag/Keyword
# ============================================================
def scrape_by_hashtag(keyword: str, limit: int = 50) -> list:
    cek_login()
    results = []
    count = 0

    try:
        hashtag = instaloader.Hashtag.from_name(L.context, keyword)
        print(f"🔍 Mulai scrape hashtag: #{keyword} | Target: {limit} post")

        for post in hashtag.get_posts():
            if count >= limit:
                break
            try:
                data = {
                    "shortcode": post.shortcode,
                    "url":       f"https://www.instagram.com/p/{post.shortcode}/",
                    "username":  post.owner_username,
                    "caption":   (post.caption or "")[:500],
                    "likes":     post.likes,
                    "comments":  post.comments,
                    "tanggal":   str(post.date),
                    "keyword":   keyword,
                }
                save_post(data)
                results.append(data)
                count += 1
                print(f"  [{count}/{limit}] @{data['username']} — {data['url']}")
                time.sleep(random.uniform(2, 5))
            except Exception as e:
                print(f"  ⚠️ Skip post error: {e}")
                continue

    except Exception as e:
        print(f"❌ Error scrape hashtag: {e}")

    print(f"✅ Selesai. Terkumpul: {len(results)} post")
    return results

# ============================================================
# Scrape Komentar dari 1 Post
# ============================================================
def scrape_comments(shortcode: str, limit: int = 50) -> list:
    cek_login()
    comments = []
    post_url = f"https://www.instagram.com/p/{shortcode}/"

    try:
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        count = 0
        print(f"💬 Scrape komentar: {post_url} | Target: {limit}")

        for comment in post.get_comments():
            if count >= limit:
                break
            try:
                text     = comment.text or ""
                neg_flag = 1 if is_negative(text) else 0
                neg_score = get_negative_score(text)

                save_comment(post_url, shortcode, comment.owner.username, text, neg_flag)
                comments.append({
                    "post_url":       post_url,
                    "shortcode":      shortcode,
                    "username":       comment.owner.username,
                    "text":           text,
                    "is_negative":    neg_flag,
                    "negative_score": neg_score,
                    "label":          "NEGATIF" if neg_flag else "POSITIF",
                })
                count += 1
                label = "🔴" if neg_flag else "🟢"
                print(f"  [{count}] {label} @{comment.owner.username}: {text[:60]}")
                time.sleep(random.uniform(1, 3))
            except Exception as e:
                print(f"  ⚠️ Skip comment error: {e}")
                continue

    except Exception as e:
        print(f"❌ Error scrape komentar: {e}")

    print(f"✅ Selesai. Komentar: {len(comments)} | Negatif: {sum(1 for c in comments if c['is_negative'])}")
    return comments

# ============================================================
# Scrape Komentar dari Semua Post (Batch)
# ============================================================
def scrape_all_comments_from_posts(posts: list, comment_limit: int = 30) -> list:
    """Ambil komentar dari daftar post hasil scrape_by_hashtag"""
    all_comments = []
    total = len(posts)
    for i, post in enumerate(posts, 1):
        print(f"\n📌 [{i}/{total}] Ambil komentar dari: {post['url']}")
        comments = scrape_comments(post["shortcode"], limit=comment_limit)
        all_comments.extend(comments)
        # Jeda lebih lama antar post
        time.sleep(random.uniform(5, 10))
    return all_comments
