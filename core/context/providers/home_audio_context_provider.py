"""Section context provider for home_audio section."""

from __future__ import annotations

from typing import Any

from core.context.section_context_provider import SectionContextProvider


class HomeAudioContextProvider(SectionContextProvider):
    section_key = "home_audio"

    def __init__(self, db=None, snapcast_manager=None, ha_client=None):
        self._db = db
        self._snapcast = snapcast_manager
        self._ha_client = ha_client

    def get_context(self) -> dict[str, Any]:
        return _build_home_audio_context(self._snapcast)

    def get_suggestions(self) -> list[dict[str, Any]]:
        return _home_audio_suggestions(self._snapcast)

    def get_allowed_actions(self) -> list[str]:
        return [
            "diagnose_home_audio",
            "diagnose_ecosystem",
            "open_section",
        ]


def _build_home_audio_context(snapcast) -> dict[str, Any]:
    ctx: dict[str, Any] = {
        "section": "home_audio",
        "snapcast_active": False,
        "zone_count": 0,
        "client_count": 0,
    }
    if snapcast is None:
        return ctx
    try:
        if hasattr(snapcast, "is_running"):
            ctx["snapcast_active"] = snapcast.is_running()
        if hasattr(snapcast, "zones"):
            ctx["zone_count"] = len(snapcast.zones) if snapcast.zones else 0
        if hasattr(snapcast, "clients"):
            ctx["client_count"] = len(snapcast.clients) if snapcast.clients else 0
    except Exception:
        pass
    return ctx


def _home_audio_suggestions(snapcast) -> list[dict[str, Any]]:
    suggestions = []
    ctx = _build_home_audio_context(snapcast)
    if not ctx.get("snapcast_active"):
        suggestions.append({
            "id": "home_audio_snapcast_inactive",
            "title": "Activar Snapcast",
            "description": "Snapcast no esta activo. Activalo para usar audio multiroom.",
            "section": "home_audio",
            "action": "diagnose_home_audio",
            "args": {},
            "priority": "medium",
            "requires_confirmation": False,
            "reason": "snapcast_active=False",
        })
    suggestions.append({
        "id": "home_audio_diagnose",
        "title": "Diagnosticar Home Audio",
        "description": "Revisa el estado de Snapcast.",
        "section": "home_audio",
        "action": "diagnose_home_audio",
        "args": {},
        "priority": "low",
        "requires_confirmation": False,
        "reason": "",
    })
    return suggestions[:5]
