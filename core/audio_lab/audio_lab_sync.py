"""Audio Lab sync — synchronise diagnostic cache results with media_items columns.

Updates quality, analysis_status, and spectral_verdict in the main library DB
so that SearchEngine filters (quality:, analysis:, spectral:) work in real time.
"""

from __future__ import annotations

import logging
import sqlite3
from typing import Any

logger = logging.getLogger("michi.audio_lab.sync")

_SPECIAL_VALUES = frozenset({"SUSPICIOUS_UPSAMPLING", "POSSIBLE_LOSSY_SOURCE"})


def _ensure_columns(conn: sqlite3.Connection):
    """Ensure sync columns exist in media_items (idempotent)."""
    cols = {r[1] for r in conn.execute("PRAGMA table_info(media_items)").fetchall()}
    for col, definition in (
        ("quality", "TEXT DEFAULT ''"),
        ("analysis_status", "TEXT DEFAULT ''"),
        ("spectral_verdict", "TEXT DEFAULT ''"),
    ):
        if col not in cols:
            try:
                conn.execute(f"ALTER TABLE media_items ADD COLUMN {col} {definition}")
                logger.info("Added column %s to media_items", col)
            except Exception:
                pass
    conn.commit()


def sync_audio_lab_result_to_media_item(
    conn: sqlite3.Connection, filepath: str, result: dict[str, Any],
) -> bool:
    """Write a single diagnostic result into the media_items row for filepath.

    Updates quality, analysis_status, and spectral_verdict columns.

    Returns True if a row was updated, False otherwise.
    """
    _ensure_columns(conn)
    q = result.get("quality", {})
    quality = q.get("category", "") or ""
    error = result.get("error", "")
    if not quality and not error:
        quality = "unknown"
    analysis_status = "error" if error else "done"
    spec = result.get("spectral", {})
    spectral_verdict = spec.get("verdict", "") if isinstance(spec, dict) else ""

    conn.execute(
        "UPDATE media_items SET quality=?, analysis_status=?, spectral_verdict=? "
        "WHERE filepath=?",
        (quality, analysis_status, spectral_verdict, filepath),
    )
    conn.commit()
    return conn.total_changes > 0


def sync_audio_lab_cache_to_media_items(
    conn: sqlite3.Connection, paths: list[str] | None = None,
) -> int:
    """Synchronise all (or given) paths from the diagnostics cache to media_items.

    Returns the number of rows updated.
    """
    _ensure_columns(conn)
    from core.audio_lab.diagnostics_service import _get_cache

    cache = _get_cache()
    if cache is None:
        return 0

    if paths:
        cached = cache.get_many(paths)
    else:
        cached = {}
        all_rows = conn.execute(
            "SELECT filepath FROM media_items WHERE deleted_at IS NULL"
        ).fetchall()
        for (fp,) in all_rows:
            cached[fp] = cache.get(fp)

    updated = 0
    for fp, c in cached.items():
        if c is None:
            conn.execute(
                "UPDATE media_items SET quality='pending', "
                "analysis_status='pending', spectral_verdict='' WHERE filepath=?",
                (fp,),
            )
        else:
            q = c.get("quality", {})
            quality = q.get("category", "") or "unknown"
            error = c.get("error", "")
            analysis_status = "error" if error else "done"
            spec = c.get("spectral", {})
            spectral_verdict = spec.get("verdict", "") if isinstance(spec, dict) else ""
            conn.execute(
                "UPDATE media_items SET quality=?, analysis_status=?, "
                "spectral_verdict=? WHERE filepath=?",
                (quality, analysis_status, spectral_verdict, fp),
            )
        updated += conn.total_changes
        if updated % 100 == 0:
            conn.commit()
    conn.commit()
    return updated


def mark_audio_lab_pending(conn: sqlite3.Connection, filepath: str) -> bool:
    """Mark a file as pending analysis."""
    _ensure_columns(conn)
    conn.execute(
        "UPDATE media_items SET quality='pending', "
        "analysis_status='pending' WHERE filepath=?",
        (filepath,),
    )
    conn.commit()
    return conn.total_changes > 0


def mark_audio_lab_error(
    conn: sqlite3.Connection, filepath: str, error: str = "",
) -> bool:
    """Mark a file as analysis error."""
    _ensure_columns(conn)
    conn.execute(
        "UPDATE media_items SET quality='error', analysis_status='error', "
        "spectral_verdict='' WHERE filepath=?",
        (filepath,),
    )
    conn.commit()
    return conn.total_changes > 0
