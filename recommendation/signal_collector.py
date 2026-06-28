"""Signal collector — wraps existing DB operations to track recommendation signals."""

from __future__ import annotations

import hashlib
import logging
import time
from typing import Any

logger = logging.getLogger("michi.recommendation.signal_collector")


class SignalCollector:
    def __init__(self, db: Any, enabled: bool = True,
                 use_history: bool = False, use_favorites: bool = True,
                 use_playlists: bool = True, use_skips: bool = False):
        self._db = db
        self._enabled = enabled
        self._use_history = use_history
        self._use_favorites = use_favorites
        self._use_playlists = use_playlists
        self._use_skips = use_skips

    def record_played(self, track_id: str):
        if not self._enabled or not self._use_history:
            return
        self._save_signal(track_id, "played")

    def record_skipped(self, track_id: str):
        if not self._enabled or not self._use_skips:
            return
        self._save_signal(track_id, "skipped")

    def record_favorited(self, track_id: str):
        if not self._enabled or not self._use_favorites:
            return
        self._save_signal(track_id, "favorited")

    def record_unfavorited(self, track_id: str):
        if not self._enabled or not self._use_favorites:
            return
        self._save_signal(track_id, "unfavorited")

    def record_added_to_playlist(self, track_id: str):
        if not self._enabled or not self._use_playlists:
            return
        self._save_signal(track_id, "added_to_playlist")

    def _save_signal(self, track_id: str, signal_type: str):
        try:
            key = hashlib.sha256(track_id.encode()).hexdigest()[:16]
            self._db.conn.execute(
                "INSERT INTO track_signal (track_key, signal_type, timestamp) VALUES (?,?,?)",
                (key, signal_type, time.strftime("%Y-%m-%dT%H:%M:%S")),
            )
            self._db.conn.commit()
        except Exception as e:
            logger.debug("Signal record failed: %s", e)

    def get_signals(self, signal_type: str = "", limit: int = 500) -> list[str]:
        try:
            if signal_type:
                rows = self._db.conn.execute(
                    "SELECT DISTINCT track_key FROM track_signal WHERE signal_type=? LIMIT ?",
                    (signal_type, limit),
                ).fetchall()
            else:
                rows = self._db.conn.execute(
                    "SELECT DISTINCT track_key FROM track_signal LIMIT ?",
                    (limit,),
                ).fetchall()
            return [r[0] for r in rows]
        except Exception as e:
            logger.debug("Signal fetch failed: %s", e)
            return []

    def clear_signals(self):
        try:
            self._db.conn.execute("DELETE FROM track_signal")
            self._db.conn.commit()
        except Exception as e:
            logger.debug("Signal clear failed: %s", e)
