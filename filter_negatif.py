# ============================================================
# Filter Komentar Negatif
# Bisa ditambah keyword sesuai kebutuhan
# ============================================================

KATA_NEGATIF = [
    # Umum
    "bohong", "tipu", "penipu", "penipuan", "scam", "palsu", "hoax",
    "sampah", "busuk", "jelek", "buruk", "gagal", "hancur",
    "malu", "memalukan", "hina", "nista", "rendah",

    # Makian
    "bajingan", "brengsek", "bangsat", "keparat", "bedebah",
    "babi", "anjing", "kampret", "goblok", "tolol", "idiot",
    "bodoh", "dungu", "tai", "setan", "iblis", "laknat",

    # Kebencian
    "benci", "muak", "jijik", "muntah", "menjijikkan",
    "tidak suka", "nggak suka", "ga suka", "gak suka",

    # Kritik keras
    "parah", "payah", "lemah", "tidak berguna", "gak berguna",
    "nggak berguna", "percuma", "sia-sia", "buang waktu",
    "mengecewakan", "kecewa", "nyesel", "rugi",

    # Ancaman
    "laporkan", "polisi", "tuntut", "gugat", "viral",
    "sebar", "expose", "bongkar",

    # Bahasa Inggris umum
    "fake", "fraud", "liar", "scammer", "worst", "terrible",
    "horrible", "disgusting", "hate", "stupid", "idiot",
    "shame", "shameful", "pathetic", "useless", "garbage", "trash"
]

def is_negative(text: str) -> bool:
    """Cek apakah komentar mengandung kata negatif"""
    if not text:
        return False
    text_lower = text.lower()
    for kata in KATA_NEGATIF:
        if kata in text_lower:
            return True
    return False

def get_negative_score(text: str) -> int:
    """Hitung jumlah kata negatif dalam teks (skor)"""
    if not text:
        return 0
    text_lower = text.lower()
    score = sum(1 for kata in KATA_NEGATIF if kata in text_lower)
    return score

def filter_comments(comments: list) -> dict:
    """
    Filter list komentar menjadi positif dan negatif
    Input: [{"username": ..., "text": ...}, ...]
    Output: {"negative": [...], "positive": [...], "summary": {...}}
    """
    negative = []
    positive = []

    for c in comments:
        text = c.get("text", "")
        score = get_negative_score(text)
        c["negative_score"] = score
        if is_negative(text):
            c["label"] = "NEGATIF"
            negative.append(c)
        else:
            c["label"] = "POSITIF"
            positive.append(c)

    return {
        "negative": negative,
        "positive": positive,
        "summary": {
            "total": len(comments),
            "total_negative": len(negative),
            "total_positive": len(positive),
            "persen_negatif": round(len(negative) / len(comments) * 100, 2) if comments else 0
        }
    }

def tambah_kata_negatif(kata: str):
    """Tambah kata baru ke daftar negatif"""
    kata = kata.lower().strip()
    if kata not in KATA_NEGATIF:
        KATA_NEGATIF.append(kata)
        return True
    return False
