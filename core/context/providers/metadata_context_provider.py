"""Section context provider for metadata sections."""

from __future__ import annotations

from typing import Any

from core.context.section_context_provider import SectionContextProvider


class MetadataContextProvider(SectionContextProvider):
    section_key = "metadata_editor"

    def __init__(self, db=None):
        self._db = db

    def get_context(self) -> dict[str, Any]:
        return _build_metadata_context(self._db)

    def get_suggestions(self) -> list[dict[str, Any]]:
        return _metadata_suggestions(self._db)

    def get_allowed_actions(self) -> list[str]:
        return [
            "find_metadata_gaps",
            "suggest_metadata_for_track",
            "suggest_metadata_for_album",
            "refresh_artist_metadata",
            "refresh_album_metadata",
        ]


def _build_metadata_context(db) -> dict[str, Any]:
    ctx: dict[str, Any] = {
        "section": "metadata_editor",
        "summary": {
            "missing_metadata_count": 0,
            "tracks_without_genre": 0,
            "tracks_without_year": 0,
        },
    }
    if db is None:
        return ctx
    try:
        if hasattr(db, "get_dashboard_stats"):
            stats = db.get_dashboard_stats()
            ctx["summary"]["missing_metadata_count"] = stats.get("missing_metadata", 0)
        if hasattr(db, "conn") and db.conn:
            conn = db.conn
            ctx["summary"]["tracks_without_genre"] = conn.execute(
                "SELECT COUNT(*) FROM media_items WHERE "
                "(genre IS NULL OR genre = '') AND deleted_at IS NULL AND kind='audio'"
            ).fetchone()[0]
            ctx["summary"]["tracks_without_year"] = conn.execute(
                "SELECT COUNT(*) FROM media_items WHERE "
                "(year IS NULL OR year = 0) AND deleted_at IS NULL AND kind='audio'"
            ).fetchone()[0]
    except Exception:
        pass
    return ctx


def _metadata_suggestions(db) -> list[dict[str, Any]]:
    suggestions = []
    ctx = _build_metadata_context(db).get("summary", {})
    mm = ctx.get("missing_metadata_count", 0)
    wg = ctx.get("tracks_without_genre", 0)
    wy = ctx.get("tracks_without_year", 0)
    if mm > 0:
        suggestions.append({
            "id": "metadata_review_gaps",
            "title": "Revisar metadatos incompletos",
            "description": f"{mm} canciones con campos vacios.",
            "section": "metadata_editor",
            "action": "find_metadata_gaps",
            "args": {},
            "priority": "medium",
            "requires_confirmation": False,
            "reason": f"missing_metadata_count={mm}",
        })
    if wg > 10:
        suggestions.append({
            "id": "metadata_missing_genres",
            "title": "Completar generos",
            "description": f"{wg} canciones sin genero asignado.",
            "section": "metadata_editor",
            "action": "suggest_metadata_for_track",
            "args": {"focus": "genre"},
            "priority": "low",
            "requires_confirmation": False,
            "reason": f"tracks_without_genre={wg}",
        })
    if wy > 10:
        suggestions.append({
            "id": "metadata_missing_year",
            "title": "Completar anos",
            "description": f"{wy} canciones sin ano.",
            "section": "metadata_editor",
            "action": "suggest_metadata_for_track",
            "args": {"focus": "year"},
            "priority": "low",
            "requires_confirmation": False,
            "reason": f"tracks_without_year={wy}",
        })
    return suggestions[:5]
