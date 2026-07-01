"""Section context provider for genres — stats, health, cleanup suggestions."""
from __future__ import annotations

from typing import Any

from core.context.section_context_provider import SectionContextProvider


class GenreContextProvider(SectionContextProvider):
    section_key = "genres"

    def __init__(self, db=None, genre_repo=None, genre_stats_svc=None):
        self._db = db
        self._repo = genre_repo
        self._stats_svc = genre_stats_svc

    def get_context(self) -> dict[str, Any]:
        return _build_genre_context(self._db, self._repo, self._stats_svc)

    def get_suggestions(self) -> list[dict[str, Any]]:
        return _genre_suggestions(self._db, self._repo, self._stats_svc)

    def get_allowed_actions(self) -> list[str]:
        return [
            "cleanup_genres",
            "merge_genres",
            "rename_genre",
            "create_mix_from_genre",
            "create_playlist_from_genre",
            "apply_genre_to_tracks",
            "normalize_genres",
        ]


def _build_genre_context(db, repo, stats_svc) -> dict[str, Any]:
    ctx: dict[str, Any] = {
        "section": "genres",
        "genre_count": 0,
        "total_tracks": 0,
        "untagged_count": 0,
        "duplicate_count": 0,
        "health_pct": 0,
        "genres": [],
    }
    if stats_svc:
        try:
            overview = stats_svc.get_genres_overview()
            health = stats_svc.get_health_summary()
            ctx["genre_count"] = len(overview)
            ctx["total_tracks"] = health.get("total_tracks", 0)
            ctx["health_pct"] = health.get("health_pct", 0)
            ctx["genres"] = [g.get("genre", "") for g in overview[:20]]
            untagged = stats_svc.get_tracks_without_genre()
            ctx["untagged_count"] = len(untagged)
        except Exception:
            pass
    if repo and ctx.get("duplicate_count", 0) == 0:
        try:
            from metadata.genre_normalizer import detect_duplicate_genres
            items = db.get_all() if db else []
            dups = detect_duplicate_genres(items)
            ctx["duplicate_count"] = len(dups)
        except Exception:
            pass
    return ctx


def _genre_suggestions(db, repo, stats_svc) -> list[dict[str, Any]]:
    suggestions = []
    if stats_svc:
        try:
            health = stats_svc.get_health_summary()
            if health.get("missing_metadata", 0) > 0:
                suggestions.append({
                    "id": "genre_untagged_tracks",
                    "title": "Revisar canciones sin género",
                    "description": f"{health['missing_metadata']} canciones sin género.",
                    "section": "genres",
                    "action": "cleanup_genres",
                    "args": {},
                    "priority": "medium",
                    "requires_confirmation": False,
                    "reason": f"untagged_count={health['missing_metadata']}",
                })
        except Exception:
            pass
    if repo:
        try:
            dups = repo.get_pending_suggestions("duplicate")
            if dups:
                suggestions.append({
                    "id": "genre_duplicates",
                    "title": "Fusionar géneros duplicados",
                    "description": f"{len(dups)} grupos de géneros duplicados detectados.",
                    "section": "genres",
                    "action": "merge_genres",
                    "args": {},
                    "priority": "medium",
                    "requires_confirmation": True,
                    "reason": f"duplicate_count={len(dups)}",
                })
        except Exception:
            pass
    return suggestions[:5]
