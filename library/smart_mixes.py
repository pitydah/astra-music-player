"""Smart Mixes — dynamic playlists based on play history and library data.

Uses the real schema:
  - media_items: play_count, last_played, deleted_at, genre
  - play_history: track_id (= filepath), played_at
  - favorites:  track_id (= filepath), added_at
"""

import logging
import sqlite3

from core.paths import database_path

logger = logging.getLogger(__name__)


def _connect(conn: sqlite3.Connection | None = None) -> sqlite3.Connection:
    if conn is not None:
        return conn
    new_conn = sqlite3.connect(database_path())
    new_conn.execute("PRAGMA journal_mode=WAL")
    return new_conn


def _has_table(conn: sqlite3.Connection, table: str) -> bool:
    cur = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,))
    return cur.fetchone() is not None


def _has_column(conn: sqlite3.Connection, table: str, col: str) -> bool:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(r[1] == col for r in rows)


def _deleted_filter(conn: sqlite3.Connection, alias: str = "") -> str:
    """Return 'AND deleted_at IS NULL' (optionally qualified) if the column exists."""
    if not _has_column(conn, "media_items", "deleted_at"):
        return ""
    prefix = f"{alias}." if alias else ""
    return f"AND {prefix}deleted_at IS NULL"


def _run_query(sql: str, params: tuple = (), conn: sqlite3.Connection | None = None) -> list[str]:
    close_conn = conn is None
    conn = _connect(conn)
    try:
        rows = conn.execute(sql, params).fetchall()
        return [r[0] for r in rows]
    finally:
        if close_conn:
            conn.close()


def get_popular(limit: int = 30, conn: sqlite3.Connection | None = None) -> list[str]:
    """Most played tracks overall (by media_items.play_count)."""
    try:
        deleted = _deleted_filter(_connect(conn))
        return _run_query(
            f"SELECT filepath FROM media_items "
            f"WHERE play_count > 0 {deleted} "
            f"ORDER BY play_count DESC, last_played DESC LIMIT ?",
            (limit,), conn)
    except Exception as e:
        logger.warning("get_popular failed: %s", e)
        return []


def get_daily_mix(limit: int = 30, conn: sqlite3.Connection | None = None) -> list[str]:
    """Tracks played in the last 7 days."""
    c = _connect(conn)
    close_conn = conn is None
    try:
        deleted = _deleted_filter(c)
        if _has_table(c, "play_history"):
            rows = c.execute(
                f"SELECT m.filepath, MAX(h.played_at) as latest "
                f"FROM media_items m "
                f"JOIN play_history h ON h.track_id = m.filepath "
                f"WHERE h.played_at > strftime('%s','now') - 604800 {deleted} "
                f"GROUP BY m.filepath "
                f"ORDER BY m.play_count DESC, latest DESC LIMIT ?",
                (limit,)).fetchall()
            if rows:
                return [r[0] for r in rows]
        # Fallback: use media_items.last_played
        rows = c.execute(
            f"SELECT filepath FROM media_items "
            f"WHERE last_played IS NOT NULL "
            f"AND last_played > strftime('%s','now') - 604800 {deleted} "
            f"ORDER BY play_count DESC, last_played DESC LIMIT ?",
            (limit,)).fetchall()
        return [r[0] for r in rows]
    except Exception as e:
        logger.warning("get_daily_mix failed: %s", e)
        return []
    finally:
        if close_conn:
            c.close()


def get_unplayed(limit: int = 20, conn: sqlite3.Connection | None = None) -> list[str]:
    """Tracks with play_count = 0 or never played."""
    try:
        deleted = _deleted_filter(_connect(conn))
        return _run_query(
            f"SELECT filepath FROM media_items "
            f"WHERE (play_count = 0 OR play_count IS NULL) "
            f"AND (last_played IS NULL) {deleted} "
            f"ORDER BY RANDOM() LIMIT ?",
            (limit,), conn)
    except Exception as e:
        logger.warning("get_unplayed failed: %s", e)
        return []


def get_favorites_recent(limit: int = 20, conn: sqlite3.Connection | None = None) -> list[str]:
    """Recently favorited tracks, ordered by favorites.added_at."""
    c = _connect(conn)
    close_conn = conn is None
    try:
        if not _has_table(c, "favorites"):
            return []
        deleted = _deleted_filter(c)
        rows = c.execute(
            f"SELECT m.filepath FROM media_items m "
            f"JOIN favorites f ON f.track_id = m.filepath "
            f"WHERE 1=1 {deleted} "
            f"ORDER BY f.added_at DESC LIMIT ?",
            (limit,)).fetchall()
        return [r[0] for r in rows]
    except Exception as e:
        logger.warning("get_favorites_recent failed: %s", e)
        return []
    finally:
        if close_conn:
            c.close()


def get_by_genre(genre: str, limit: int = 30, conn: sqlite3.Connection | None = None) -> list[str]:
    """Tracks of a specific genre."""
    if not genre or not genre.strip():
        return []
    try:
        deleted = _deleted_filter(_connect(conn))
        return _run_query(
            f"SELECT filepath FROM media_items WHERE genre LIKE ? "
            f"{deleted} "
            f"ORDER BY RANDOM() LIMIT ?",
            (f"%{genre}%", limit), conn)
    except Exception as e:
        logger.warning("get_by_genre failed: %s", e)
        return []
