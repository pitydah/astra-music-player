"""Smart Mixes — dynamic playlists based on play history and library data."""

import sqlite3
import logging
from library.library_db import DB_PATH

logger = logging.getLogger(__name__)


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def _make_track_id(filepath: str) -> str:
    import hashlib
    return hashlib.sha256(filepath.encode()).hexdigest()[:16]


def _register_functions(conn: sqlite3.Connection):
    conn.create_function("make_track_id", 1, _make_track_id)


def _has_table(conn: sqlite3.Connection, table: str) -> bool:
    cur = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,))
    return cur.fetchone() is not None


def get_daily_mix(limit: int = 30) -> list[str]:
    """Tracks played in the last 7 days, ordered by play count."""
    try:
        conn = _connect()
        _register_functions(conn)
        if not _has_table(conn, "play_history"):
            logger.warning("play_history table not found — daily mix skipped")
            conn.close()
            return []
        rows = conn.execute(
            "SELECT m.filepath FROM media_items m "
            "JOIN play_history h ON make_track_id(m.filepath) = h.track_id "
            "WHERE h.last_played > strftime('%s','now') - 604800 "
            "ORDER BY h.play_count DESC LIMIT ?", (limit,)).fetchall()
        conn.close()
        return [r[0] for r in rows]
    except Exception as e:
        logger.warning("get_daily_mix failed: %s", e)
        return []


def get_unplayed(limit: int = 20) -> list[str]:
    """Tracks never played."""
    try:
        conn = _connect()
        _register_functions(conn)
        if not _has_table(conn, "play_history"):
            logger.warning("play_history table not found — unplayed skipped")
            conn.close()
            return []
        rows = conn.execute(
            "SELECT filepath FROM media_items WHERE filepath NOT IN "
            "(SELECT m.filepath FROM media_items m "
            "JOIN play_history h ON make_track_id(m.filepath) = h.track_id) "
            "ORDER BY RANDOM() LIMIT ?",
            (limit,)).fetchall()
        conn.close()
        return [r[0] for r in rows]
    except Exception as e:
        logger.warning("get_unplayed failed: %s", e)
        return []


def get_favorites_recent(limit: int = 20) -> list[str]:
    """Recently favorited tracks."""
    try:
        conn = _connect()
        _register_functions(conn)
        if not _has_table(conn, "favorites"):
            logger.warning("favorites table not found — favorites skipped")
            conn.close()
            return []
        rows = conn.execute(
            "SELECT m.filepath FROM media_items m "
            "JOIN favorites f ON make_track_id(m.filepath) = f.track_id "
            "ORDER BY m.date_added DESC LIMIT ?", (limit,)).fetchall()
        conn.close()
        return [r[0] for r in rows]
    except Exception as e:
        logger.warning("get_favorites_recent failed: %s", e)
        return []


def get_popular(limit: int = 30) -> list[str]:
    """Most played tracks overall."""
    try:
        conn = _connect()
        _register_functions(conn)
        if not _has_table(conn, "play_history"):
            logger.warning("play_history table not found — popular skipped")
            conn.close()
            return []
        rows = conn.execute(
            "SELECT m.filepath FROM media_items m "
            "JOIN play_history h ON make_track_id(m.filepath) = h.track_id "
            "ORDER BY h.play_count DESC LIMIT ?", (limit,)).fetchall()
        conn.close()
        return [r[0] for r in rows]
    except Exception as e:
        logger.warning("get_popular failed: %s", e)
        return []


def get_by_genre(genre: str, limit: int = 30) -> list[str]:
    """Tracks of a specific genre."""
    try:
        conn = _connect()
        rows = conn.execute(
            "SELECT filepath FROM media_items WHERE genre LIKE ? "
            "ORDER BY RANDOM() LIMIT ?", (f"%{genre}%", limit)).fetchall()
        conn.close()
        return [r[0] for r in rows]
    except Exception as e:
        logger.warning("get_by_genre failed: %s", e)
        return []
