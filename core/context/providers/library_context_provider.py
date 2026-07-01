"""Section context provider for library_hub and sub-sections (albums, artists, genres)."""

from __future__ import annotations

from typing import Any

from core.context.section_context_provider import SectionContextProvider


class LibraryContextProvider(SectionContextProvider):
    section_key = "library_hub"

    def __init__(self, db=None, cover_art_service=None):
        self._db = db
        self._cover_svc = cover_art_service

    def get_context(self) -> dict[str, Any]:
        return _build_library_context(self._db)

    def get_suggestions(self) -> list[dict[str, Any]]:
        return _library_suggestions(self._db)

    def get_allowed_actions(self) -> list[str]:
        return [
            "search_library",
            "find_metadata_gaps",
            "draft_playlist",
            "open_album_view",
            "open_artist_view",
            "send_to_audio_lab",
            "explain_audio_format",
            "recommend_music",
        ]


def _build_library_context(db) -> dict[str, Any]:
    ctx: dict[str, Any] = {
        "section": "library_hub",
        "summary": {
            "track_count": 0,
            "album_count": 0,
            "artist_count": 0,
            "genre_count": 0,
            "lossless_count": 0,
            "lossy_count": 0,
            "hires_count": 0,
            "missing_metadata_count": 0,
            "missing_cover_count": 0,
        },
    }
    if db is None:
        return ctx
    try:
        if hasattr(db, "get_dashboard_stats"):
            stats = db.get_dashboard_stats()
            ctx["summary"]["track_count"] = stats.get("total_songs", 0)
            ctx["summary"]["album_count"] = stats.get("total_albums", 0)
            ctx["summary"]["artist_count"] = stats.get("total_artists", 0)
            ctx["summary"]["missing_metadata_count"] = stats.get("missing_metadata", 0)
        if hasattr(db, "conn") and db.conn:
            conn = db.conn
            ctx["summary"]["genre_count"] = conn.execute(
                "SELECT COUNT(DISTINCT COALESCE(NULLIF(genre,''),'Sin genero')) "
                "FROM media_items WHERE deleted_at IS NULL"
            ).fetchone()[0]
            lossless = conn.execute(
                "SELECT COUNT(*) FROM media_items WHERE kind='audio' AND deleted_at IS NULL "
                "AND (codec IN ('FLAC','ALAC','WAV','AIFF','APE','WV') "
                "OR container IN ('flac','wav','aiff','ape','wv'))"
            ).fetchone()[0]
            ctx["summary"]["lossless_count"] = lossless
            hires = conn.execute(
                "SELECT COUNT(*) FROM media_items WHERE kind='audio' AND deleted_at IS NULL "
                "AND bit_depth >= 24 AND sample_rate >= 96000"
            ).fetchone()[0]
            ctx["summary"]["hires_count"] = hires
            ctx["summary"]["lossy_count"] = max(0, ctx["summary"]["track_count"] - lossless)
    except Exception:
        pass
    return ctx


def _library_suggestions(db) -> list[dict[str, Any]]:
    suggestions = []
    stats = _build_library_context(db).get("summary", {})
    mm = stats.get("missing_metadata_count", 0)
    tc = stats.get("track_count", 0)
    if mm > 0:
        suggestions.append({
            "id": "library_missing_metadata",
            "title": "Revisar metadatos incompletos",
            "description": f"{mm} canciones con metadatos incompletos.",
            "section": "library_hub",
            "action": "find_metadata_gaps",
            "args": {},
            "priority": "medium",
            "requires_confirmation": False,
            "reason": f"missing_metadata_count={mm}",
        })
    if tc > 0:
        suggestions.append({
            "id": "library_draft_playlist",
            "title": "Crear playlist",
            "description": "Crea una playlist inteligente desde tu biblioteca.",
            "section": "library_hub",
            "action": "draft_playlist",
            "args": {},
            "priority": "low",
            "requires_confirmation": True,
            "reason": "",
        })
    return suggestions[:5]
