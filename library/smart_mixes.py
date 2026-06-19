"""Smart Mixes — dynamic playlists based on play history and library data."""

import sqlite3
from library.library_db import DB_PATH


def get_daily_mix(limit: int = 30) -> list[str]:
    """Tracks played in the last 7 days, ordered by play count."""
    try:
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute(
            "SELECT m.filepath FROM media_items m "
            "JOIN play_history h ON make_track_id(m.filepath) = h.track_id "
            "WHERE h.last_played > strftime('%s','now') - 604800 "
            "ORDER BY h.play_count DESC LIMIT ?", (limit,)).fetchall()
        conn.close()
        return [r[0] for r in rows]
    except Exception:
        return []


def get_unplayed(limit: int = 20) -> list[str]:
    """Tracks never played."""
    try:
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute(
            "SELECT filepath FROM media_items WHERE id NOT IN "
            "(SELECT media_items.id FROM media_items "
            "JOIN play_history ON make_track_id(media_items.filepath) = "
            "play_history.track_id) ORDER BY RANDOM() LIMIT ?",
            (limit,)).fetchall()
        conn.close()
        return [r[0] for r in rows]
    except Exception:
        return []


def get_favorites_recent(limit: int = 20) -> list[str]:
    """Recently favorited tracks."""
    try:
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute(
            "SELECT m.filepath FROM media_items m "
            "JOIN favorites f ON make_track_id(m.filepath) = f.track_id "
            "ORDER BY m.date_added DESC LIMIT ?", (limit,)).fetchall()
        conn.close()
        return [r[0] for r in rows]
    except Exception:
        return []


def get_popular(limit: int = 30) -> list[str]:
    """Most played tracks overall."""
    try:
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute(
            "SELECT m.filepath FROM media_items m "
            "JOIN play_history h ON make_track_id(m.filepath) = h.track_id "
            "ORDER BY h.play_count DESC LIMIT ?", (limit,)).fetchall()
        conn.close()
        return [r[0] for r in rows]
    except Exception:
        return []


def get_by_genre(genre: str, limit: int = 30) -> list[str]:
    """Tracks of a specific genre."""
    try:
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute(
            "SELECT filepath FROM media_items WHERE genre LIKE ? "
            "ORDER BY RANDOM() LIMIT ?", (f"%{genre}%", limit)).fetchall()
        conn.close()
        return [r[0] for r in rows]
    except Exception:
        return []
