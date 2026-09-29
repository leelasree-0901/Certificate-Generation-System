import sqlite3
from datetime import datetime
from config import Config


def get_connection():
    conn = sqlite3.connect(Config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS certificates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            certificate_id TEXT UNIQUE NOT NULL,
            participant_name TEXT NOT NULL,
            course TEXT,
            email TEXT,
            issue_date TEXT,
            file_path TEXT,
            created_at TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS verification_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            certificate_id TEXT,
            verified INTEGER,
            verified_at TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    cur.execute(
        "INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)",
        ("admin", "admin")
    )

    default_settings = {
        "organization": "Certificate Generation System",
        "signatory": "Authorized Signatory",
        "course": "Certificate of Participation"
    }

    for key, value in default_settings.items():
        cur.execute(
            "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
            (key, value)
        )

    conn.commit()
    conn.close()


def verify_user(username, password):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (username, password)
    ).fetchone()
    conn.close()
    return row is not None


def stats():
    conn = get_connection()

    total = conn.execute(
        "SELECT COUNT(*) AS count FROM certificates"
    ).fetchone()["count"]

    conn.close()

    return {
        "total": total
    }


def list_certificates(limit=100, search=None):
    conn = get_connection()

    if search:
        rows = conn.execute(
            """
            SELECT * FROM certificates
            WHERE participant_name LIKE ?
               OR certificate_id LIKE ?
               OR email LIKE ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (f"%{search}%", f"%{search}%", f"%{search}%", limit)
        ).fetchall()
    else:
        rows = conn.execute(
            """
            SELECT * FROM certificates
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,)
        ).fetchall()

    conn.close()
    return rows


def add_certificate(
    certificate_id,
    participant_name,
    course,
    email,
    issue_date,
    file_path
):
    conn = get_connection()

    conn.execute(
        """
        INSERT OR REPLACE INTO certificates
        (certificate_id, participant_name, course, email,
         issue_date, file_path, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            certificate_id,
            participant_name,
            course,
            email,
            issue_date,
            file_path,
            datetime.now().isoformat()
        )
    )

    conn.commit()
    conn.close()


def get_certificate(certificate_id):
    conn = get_connection()

    row = conn.execute(
        "SELECT * FROM certificates WHERE certificate_id = ?",
        (certificate_id,)
    ).fetchone()

    conn.close()

    return row


def delete_certificate(certificate_id):
    conn = get_connection()

    conn.execute(
        "DELETE FROM certificates WHERE certificate_id = ?",
        (certificate_id,)
    )

    conn.commit()
    conn.close()


def log_verification(certificate_id, verified):
    conn = get_connection()

    conn.execute(
        """
        INSERT INTO verification_logs
        (certificate_id, verified, verified_at)
        VALUES (?, ?, ?)
        """,
        (
            certificate_id,
            int(verified),
            datetime.now().isoformat()
        )
    )

    conn.commit()
    conn.close()


def get_settings():
    conn = get_connection()

    rows = conn.execute(
        "SELECT key, value FROM settings"
    ).fetchall()

    conn.close()

    return {row["key"]: row["value"] for row in rows}


def update_settings(data):
    conn = get_connection()

    for key, value in data.items():
        conn.execute(
            """
            INSERT OR REPLACE INTO settings (key, value)
            VALUES (?, ?)
            """,
            (key, value)
        )

    conn.commit()
    conn.close()