"""VoxCraft Data Store — SQLite-backed persistence layer.

Replaces the fragile JSON filesystem duplication (issues 3.1–3.7).
Features:
- SQLite with WAL mode for concurrent reads
- Schema versioning with automatic migration
- Atomic writes via transactions
- Proper indexing for history queries
- Single source of truth — no duplicate storage
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger("voxcraft.data_store")

DB_PATH: Path = Path("data/voxcraft.db")
CURRENT_SCHEMA_VERSION = 1

# Thread-local connections for thread safety
_local = threading.local()


def _get_conn() -> sqlite3.Connection:
    """Get thread-local database connection."""
    if not hasattr(_local, "conn") or _local.conn is None:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        _local.conn = conn
    return _local.conn


def init_db() -> None:
    """Initialize database schema. Idempotent — safe to call on every startup."""
    conn = _get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER PRIMARY KEY,
            applied_at TEXT NOT NULL
        )
    """)
    row = conn.execute("SELECT MAX(version) as v FROM schema_version").fetchone()
    current = row["v"] if row and row["v"] is not None else 0

    if current < 1:
        _apply_v1(conn)

    logger.info("Data store ready (schema v%s) at %s", max(current, CURRENT_SCHEMA_VERSION), DB_PATH)


def _apply_v1(conn: sqlite3.Connection) -> None:
    """Apply schema v1: initial tables."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS exports (
            id TEXT PRIMARY KEY,
            filename TEXT NOT NULL UNIQUE,
            text TEXT NOT NULL,
            voice TEXT NOT NULL,
            language TEXT NOT NULL,
            duration_seconds REAL NOT NULL,
            format TEXT NOT NULL DEFAULT 'wav',
            sample_rate INTEGER NOT NULL DEFAULT 44100,
            speed REAL NOT NULL DEFAULT 1.05,
            quality INTEGER NOT NULL DEFAULT 8,
            audio_path TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_exports_created_at ON exports(created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_exports_voice ON exports(voice);
        CREATE INDEX IF NOT EXISTS idx_exports_language ON exports(language);

        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            export_id TEXT NOT NULL REFERENCES exports(id) ON DELETE CASCADE,
            accessed_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_history_accessed_at ON history(accessed_at DESC);
    """)
    conn.execute(
        "INSERT INTO schema_version (version, applied_at) VALUES (?, ?)",
        (1, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    logger.info("Applied schema migration v1")


def save_export(meta: dict) -> None:
    """Save an export record atomically."""
    conn = _get_conn()
    now = datetime.now(timezone.utc).isoformat()
    try:
        with conn:
            conn.execute(
                """INSERT OR REPLACE INTO exports
                   (id, filename, text, voice, language, duration_seconds,
                    format, sample_rate, speed, quality, audio_path, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    meta["id"],
                    meta["filename"],
                    meta["text"],
                    meta["voice"],
                    meta["language"],
                    meta["duration_seconds"],
                    meta.get("format", "wav"),
                    meta.get("sample_rate", 44100),
                    meta.get("speed", 1.05),
                    meta.get("quality", 8),
                    meta["audio_path"],
                    meta["created_at"],
                    now,
                ),
            )
            conn.execute(
                "INSERT INTO history (export_id, accessed_at) VALUES (?, ?)",
                (meta["id"], now),
            )
        logger.debug("Saved export %s", meta["id"])
    except sqlite3.Error as e:
        logger.error("Failed to save export %s: %s", meta.get("id", "unknown"), e)
        raise


def get_history(limit: int = 50, search: str | None = None) -> list[dict]:
    """Get recent generation history with optional search."""
    conn = _get_conn()
    query = """
        SELECT e.*, h.accessed_at as history_accessed_at
        FROM exports e
        INNER JOIN history h ON e.id = h.export_id
    """
    params: list[Any] = []
    if search:
        query += " WHERE e.text LIKE ? OR e.voice LIKE ?"
        s = f"%{search}%"
        params.extend([s, s])
    query += " ORDER BY h.accessed_at DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def get_export(export_id: str) -> dict | None:
    """Get a single export record by ID."""
    conn = _get_conn()
    row = conn.execute("SELECT * FROM exports WHERE id = ?", (export_id,)).fetchone()
    return dict(row) if row else None


def delete_export(export_id: str) -> int:
    """Delete an export and its history entry. Returns number of DB rows deleted."""
    conn = _get_conn()
    try:
        with conn:
            # Get audio path before deleting
            row = conn.execute("SELECT audio_path FROM exports WHERE id = ?", (export_id,)).fetchone()
            if not row:
                return 0

            audio_path = row["audio_path"]
            # Delete DB records (cascade handles history)
            cursor = conn.execute("DELETE FROM exports WHERE id = ?", (export_id,))
            db_deleted = cursor.rowcount

            # Remove audio file
            if audio_path:
                try:
                    os.remove(audio_path)
                except OSError as e:
                    logger.warning("Could not remove audio file %s: %s", audio_path, e)

            logger.info("Deleted export %s (%d DB rows, audio removed)", export_id, db_deleted)
            return db_deleted
    except sqlite3.Error as e:
        logger.error("Failed to delete export %s: %s", export_id, e)
        raise


def get_all_exports(limit: int = 200) -> list[dict]:
    """Get all exports for listing."""
    conn = _get_conn()
    rows = conn.execute(
        "SELECT * FROM exports ORDER BY created_at DESC LIMIT ?", (limit,)
    ).fetchall()
    return [dict(row) for row in rows]


def migrate_from_json() -> int:
    """Migrate existing JSON files into SQLite. Returns number of items migrated."""
    data_dir = DB_PATH.parent
    history_dir = data_dir / "history"
    if not history_dir.exists():
        return 0

    count = 0
    for f in sorted(history_dir.glob("*.json"), key=os.path.getmtime):
        try:
            with open(f) as fp:
                meta = json.load(fp)

            # Skip if already in DB
            existing = get_export(meta.get("id", ""))
            if existing:
                continue

            # Ensure required fields with defaults
            meta.setdefault("format", "wav")
            meta.setdefault("sample_rate", 44100)
            meta.setdefault("speed", 1.05)
            meta.setdefault("quality", 8)
            meta.setdefault("duration_seconds", 0.0)

            save_export(meta)
            count += 1
        except (json.JSONDecodeError, OSError, sqlite3.Error) as e:
            logger.warning("Skipping migration for %s: %s", f.name, e)

    logger.info("Migrated %d history items from JSON to SQLite", count)
    return count
