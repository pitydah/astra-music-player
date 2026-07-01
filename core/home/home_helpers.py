"""Shared helpers for Home dashboard — single source of truth for DB stats."""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("michi.home.helpers")


def get_db_stats(db) -> dict[str, Any]:
    """Get consolidated library stats from DB.

    Tries get_dashboard_stats first (richer), falls back to get_stats.
    Returns dict with at least: total_songs, total_albums, total_artists.
    """
    result: dict[str, Any] = {
        "total_songs": 0,
        "total_albums": 0,
        "total_artists": 0,
        "missing_metadata": 0,
    }
    if db is None:
        return result
    try:
        if hasattr(db, "get_dashboard_stats"):
            ds = db.get_dashboard_stats()
            if ds:
                result.update(ds)
        elif hasattr(db, "get_stats"):
            st = db.get_stats()
            if st:
                result["total_songs"] = st.get("total", result["total_songs"])
    except Exception:
        logger.debug("DB stats unavailable", exc_info=True)
    return result
