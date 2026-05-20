import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(os.getenv("BIKES_DB", "data/bikes.db"))


def normalize_serial(s: str) -> str:
    return "".join(ch for ch in s.upper() if ch.isalnum())


@contextmanager
def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS bikes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                serial TEXT NOT NULL,
                serial_normalized TEXT NOT NULL,
                brand TEXT,
                model TEXT,
                color TEXT,
                theft_date TEXT,
                theft_location TEXT,
                owner_email TEXT NOT NULL,
                photo_path TEXT,
                status TEXT NOT NULL DEFAULT 'pending',
                verification_token TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                verified_at TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_serial_norm ON bikes(serial_normalized);
            CREATE INDEX IF NOT EXISTS idx_token ON bikes(verification_token);
            """
        )


def insert_report(
    *,
    serial: str,
    brand: str | None,
    model: str | None,
    color: str | None,
    theft_date: str | None,
    theft_location: str | None,
    owner_email: str,
    photo_path: str | None,
    token: str,
) -> int:
    with connect() as conn:
        cur = conn.execute(
            """
            INSERT INTO bikes (
                serial, serial_normalized, brand, model, color,
                theft_date, theft_location, owner_email, photo_path,
                verification_token
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                serial,
                normalize_serial(serial),
                brand,
                model,
                color,
                theft_date,
                theft_location,
                owner_email,
                photo_path,
                token,
            ),
        )
        return cur.lastrowid


def search_by_serial(serial: str) -> list[dict]:
    norm = normalize_serial(serial)
    if not norm:
        return []
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT * FROM bikes
            WHERE serial_normalized = ? AND status = 'verified'
            ORDER BY created_at DESC
            """,
            (norm,),
        ).fetchall()
        return [dict(r) for r in rows]


def verify_token(token: str) -> bool:
    if not token:
        return False
    with connect() as conn:
        row = conn.execute(
            "SELECT id FROM bikes WHERE verification_token = ? AND status = 'pending'",
            (token,),
        ).fetchone()
        if not row:
            return False
        conn.execute(
            """
            UPDATE bikes
            SET status = 'verified',
                verified_at = datetime('now'),
                verification_token = NULL
            WHERE id = ?
            """,
            (row["id"],),
        )
        return True
