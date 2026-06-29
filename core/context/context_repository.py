"""Context repository — SQLite storage for events, state, summaries and dirty flags.

Uses a separate context.sqlite (WAL mode) independent from library.db.
"""

from __future__ import annotations

import contextlib
import json
import logging
import os
import sqlite3
import time
from typing import Any

from core.paths import context_db_path

logger = logging.getLogger("michi.context_repo")

_DB_PATH: str | None = None

_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS context_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    payload_json TEXT DEFAULT '{}',
    created_at REAL NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_context_events_created ON context_events(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_context_events_type ON context_events(event_type);

CREATE TABLE IF NOT EXISTS context_state (
    key TEXT PRIMARY KEY,
    value_json TEXT DEFAULT '{}',
    updated_at REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS context_summary (
    key TEXT PRIMARY KEY,
    value_json TEXT DEFAULT '{}',
    expires_at REAL DEFAULT 0,
    updated_at REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS context_dirty_flags (
    key TEXT PRIMARY KEY,
    dirty INTEGER DEFAULT 1,
    updated_at REAL NOT NULL
);
"""


def _db_path() -> str:
    if _DB_PATH:
        return _DB_PATH
    return context_db_path()


def override_db_path(path: str | None):
    global _DB_PATH
    _DB_PATH = path


def _conn() -> sqlite3.Connection:
    path = _db_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    c = sqlite3.connect(path, timeout=3)
    c.execute("PRAGMA journal_mode=WAL")
    c.execute("PRAGMA synchronous=NORMAL")
    c.row_factory = sqlite3.Row
    _ensure_schema(c)
    return c


def _ensure_schema(c: sqlite3.Connection):
    for statement in _SCHEMA_SQL.split(";"):
        s = statement.strip()
        if s:
            with contextlib.suppress(Exception):
                c.execute(s + ";")


def _j(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, default=str) if obj is not None else "{}"


def record_event(event_type: str, payload: dict | None = None) -> None:
    if not event_type or not str(event_type).strip():
        return
    try:
        c = _conn()
        c.execute(
            "INSERT INTO context_events (event_type, payload_json, created_at) VALUES (?, ?, ?)",
            (event_type, _j(payload), time.time()),
        )
        c.commit()
        c.close()
    except Exception as e:
        logger.debug("Failed to record event %s: %s", event_type, e)


def set_state(key: str, value: dict) -> None:
    try:
        c = _conn()
        c.execute(
            "INSERT OR REPLACE INTO context_state (key, value_json, updated_at) VALUES (?, ?, ?)",
            (key, _j(value), time.time()),
        )
        c.commit()
        c.close()
    except Exception as e:
        logger.debug("Failed to set state %s: %s", key, e)


def get_state(key: str, default: dict | None = None) -> dict:
    try:
        c = _conn()
        row = c.execute("SELECT value_json FROM context_state WHERE key = ?", (key,)).fetchone()
        c.close()
        if row:
            return json.loads(row["value_json"])
    except Exception as e:
        logger.debug("Failed to get state %s: %s", key, e)
    return default or {}


def set_summary(key: str, value: dict, ttl_seconds: int = 300) -> None:
    expires = time.time() + ttl_seconds
    try:
        c = _conn()
        c.execute(
            "INSERT OR REPLACE INTO context_summary (key, value_json, expires_at, updated_at) VALUES (?, ?, ?, ?)",
            (key, _j(value), expires, time.time()),
        )
        c.commit()
        c.close()
    except Exception as e:
        logger.debug("Failed to set summary %s: %s", key, e)


def get_summary(key: str) -> dict | None:
    try:
        c = _conn()
        row = c.execute("SELECT value_json, expires_at FROM context_summary WHERE key = ?", (key,)).fetchone()
        c.close()
        if row and row["expires_at"] > time.time():
            return json.loads(row["value_json"])
    except Exception as e:
        logger.debug("Failed to get summary %s: %s", key, e)
    return None


def mark_dirty(key: str) -> None:
    try:
        c = _conn()
        c.execute(
            "INSERT OR REPLACE INTO context_dirty_flags (key, dirty, updated_at) VALUES (?, 1, ?)",
            (key, time.time()),
        )
        c.commit()
        c.close()
    except Exception as e:
        logger.debug("Failed to mark dirty %s: %s", key, e)


def clear_dirty(key: str) -> None:
    try:
        c = _conn()
        c.execute("DELETE FROM context_dirty_flags WHERE key = ?", (key,))
        c.commit()
        c.close()
    except Exception as e:
        logger.debug("Failed to clear dirty %s: %s", key, e)


def is_dirty(key: str) -> bool:
    try:
        c = _conn()
        row = c.execute("SELECT dirty FROM context_dirty_flags WHERE key = ?", (key,)).fetchone()
        c.close()
        return bool(row and row["dirty"])
    except Exception as e:
        logger.debug("Failed to check dirty %s: %s", key, e)
    return False


def recent_events(limit: int = 20) -> list[dict]:
    try:
        c = _conn()
        rows = c.execute(
            "SELECT id, event_type, payload_json, created_at FROM context_events ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        c.close()
        result = []
        for row in rows:
            try:
                payload = json.loads(row["payload_json"]) if row["payload_json"] else {}
            except Exception:
                payload = {}
            result.append({
                "id": row["id"],
                "event_type": row["event_type"],
                "payload": payload,
                "created_at": row["created_at"],
            })
        return result
    except Exception as e:
        logger.debug("Failed to get recent events: %s", e)
    return []


def cleanup_old_events(max_age_days: int = 30) -> int:
    try:
        cutoff = time.time() - max_age_days * 86400
        c = _conn()
        c.execute("DELETE FROM context_events WHERE created_at < ?", (cutoff,))
        deleted = c.rowcount
        c.commit()
        c.close()
        return deleted or 0
    except Exception as e:
        logger.debug("Failed to cleanup events: %s", e)
    return 0


def close():
    global _DB_PATH
    _DB_PATH = None
