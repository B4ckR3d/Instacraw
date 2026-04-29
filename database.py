import sqlite3

DB_NAME = "instagram_data.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            shortcode   TEXT UNIQUE,
            url         TEXT,
            username    TEXT,
            caption     TEXT,
            likes       INTEGER,
            comments    INTEGER,
            tanggal     TEXT,
            keyword     TEXT,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            post_url    TEXT,
            shortcode   TEXT,
            username    TEXT,
            text        TEXT,
            is_negative INTEGER DEFAULT 0,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

def save_post(data: dict):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("""
            INSERT OR IGNORE INTO posts
            (shortcode, url, username, caption, likes, comments, tanggal, keyword)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["shortcode"], data["url"], data["username"],
            data["caption"], data["likes"], data["comments"],
            data["tanggal"], data["keyword"]
        ))
        conn.commit()
    except Exception as e:
        print(f"Error save_post: {e}")
    finally:
        conn.close()

def save_comment(post_url: str, shortcode: str, username: str, text: str, is_negative: int = 0):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("""
            INSERT INTO comments (post_url, shortcode, username, text, is_negative)
            VALUES (?, ?, ?, ?, ?)
        """, (post_url, shortcode, username, text, is_negative))
        conn.commit()
    except Exception as e:
        print(f"Error save_comment: {e}")
    finally:
        conn.close()

def get_all_posts(keyword: str = None):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    if keyword:
        c.execute("SELECT * FROM posts WHERE keyword = ? ORDER BY created_at DESC", (keyword,))
    else:
        c.execute("SELECT * FROM posts ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def get_comments(post_url: str = None, only_negative: bool = False):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    if post_url and only_negative:
        c.execute("SELECT * FROM comments WHERE post_url = ? AND is_negative = 1", (post_url,))
    elif post_url:
        c.execute("SELECT * FROM comments WHERE post_url = ?", (post_url,))
    elif only_negative:
        c.execute("SELECT * FROM comments WHERE is_negative = 1")
    else:
        c.execute("SELECT * FROM comments")
    rows = c.fetchall()
    conn.close()
    return rows

def get_stats():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM posts")
    total_posts = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM comments")
    total_comments = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM comments WHERE is_negative = 1")
    total_negative = c.fetchone()[0]
    c.execute("SELECT DISTINCT keyword FROM posts")
    keywords = [row[0] for row in c.fetchall()]
    conn.close()
    return {
        "total_posts": total_posts,
        "total_comments": total_comments,
        "total_negative_comments": total_negative,
        "keywords": keywords
    }
