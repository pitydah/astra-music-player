"""Section context provider for mix sections."""

from __future__ import annotations

from typing import Any

from core.context.section_context_provider import SectionContextProvider


class MixContextProvider(SectionContextProvider):
    section_key = "mix_hub"

    def __init__(self, db=None):
        self._db = db

    def get_context(self) -> dict[str, Any]:
        return _build_mix_context(self._db)

    def get_suggestions(self) -> list[dict[str, Any]]:
        return _mix_suggestions()

    def get_allowed_actions(self) -> list[str]:
        return [
            "create_smart_mix",
            "explain_recommendation",
            "save_mix_as_playlist",
        ]


def _build_mix_context(db) -> dict[str, Any]:
    ctx: dict[str, Any] = {
        "section": "mix_hub",
        "mix_health": {
            "has_library": False,
            "has_enough_history": False,
            "has_favorites": False,
        },
    }
    if db is None:
        return ctx
    try:
        if hasattr(db, "get_dashboard_stats"):
            stats = db.get_dashboard_stats()
            ctx["mix_health"]["has_library"] = stats.get("total_songs", 0) > 0
        if hasattr(db, "get_favorites"):
            ctx["mix_health"]["has_favorites"] = len(db.get_favorites()) > 0
        if hasattr(db, "get_play_history"):
            ctx["mix_health"]["has_enough_history"] = len(db.get_play_history(limit=10)) >= 5
    except Exception:
        pass
    return ctx


def _mix_suggestions() -> list[dict[str, Any]]:
    return [
        {
            "id": "mix_balanced",
            "title": "Mix balanceado",
            "description": "Crea un mix con variedad de artistas y generos.",
            "section": "mix_hub",
            "action": "create_smart_mix",
            "args": {"strategy": "balanced"},
            "priority": "low",
            "requires_confirmation": True,
            "reason": "",
        },
        {
            "id": "mix_favorites",
            "title": "Mix de favoritos",
            "description": "Crea un mix con tus canciones favoritas.",
            "section": "mix_hub",
            "action": "create_smart_mix",
            "args": {"strategy": "favorites_neighbors"},
            "priority": "low",
            "requires_confirmation": True,
            "reason": "",
        },
    ]
