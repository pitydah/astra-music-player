"""Section context provider for playlist sections."""

from __future__ import annotations

from typing import Any

from core.context.section_context_provider import SectionContextProvider


class PlaylistContextProvider(SectionContextProvider):
    section_key = "playlists"

    def __init__(self, db=None):
        self._db = db

    def get_context(self) -> dict[str, Any]:
        return _build_playlist_context(self._db)

    def get_suggestions(self) -> list[dict[str, Any]]:
        return _playlist_suggestions(self._db)

    def get_allowed_actions(self) -> list[str]:
        return [
            "create_playlist",
            "export_playlist",
            "detect_duplicates",
            "create_mobile_version",
        ]


def _build_playlist_context(db) -> dict[str, Any]:
    ctx: dict[str, Any] = {
        "section": "playlists",
        "playlist_count": 0,
        "total_playlist_tracks": 0,
    }
    if db is None:
        return ctx
    try:
        if hasattr(db, "get_playlists"):
            playlists = db.get_playlists()
            ctx["playlist_count"] = len(playlists)
            ctx["total_playlist_tracks"] = sum(
                p.get("track_count", 0) for p in playlists
            )
    except Exception:
        pass
    return ctx


def _playlist_suggestions(db) -> list[dict[str, Any]]:
    suggestions = []
    ctx = _build_playlist_context(db)
    pc = ctx.get("playlist_count", 0)
    if pc == 0:
        suggestions.append({
            "id": "playlist_create_first",
            "title": "Crear tu primera playlist",
            "description": "No hay playlists todavia. Crea una desde tu biblioteca!",
            "section": "playlists",
            "action": "create_playlist",
            "args": {},
            "priority": "medium",
            "requires_confirmation": True,
            "reason": "playlist_count=0",
        })
    suggestions.append({
        "id": "playlist_export",
        "title": "Exportar playlists",
        "description": "Exporta tus playlists a formato M3U.",
        "section": "playlists",
        "action": "export_playlist",
        "args": {},
        "priority": "low",
        "requires_confirmation": True,
        "reason": "",
    })
    return suggestions[:5]
