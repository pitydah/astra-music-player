"""Section context provider for playback section."""

from __future__ import annotations

from typing import Any

from core.context.section_context_provider import SectionContextProvider


class PlaybackContextProvider(SectionContextProvider):
    section_key = "playback_hub"

    def __init__(self, db=None, playback=None):
        self._db = db
        self._playback = playback

    def get_context(self) -> dict[str, Any]:
        return _build_playback_section_context(self._playback)

    def get_suggestions(self) -> list[dict[str, Any]]:
        return _playback_suggestions(self._playback)

    def get_allowed_actions(self) -> list[str]:
        return [
            "add_tracks_to_queue",
            "play_track",
            "explain_current_track_quality",
            "continue_on_micro_server",
        ]


def _build_playback_section_context(playback) -> dict[str, Any]:
    ctx: dict[str, Any] = {
        "section": "playback_hub",
        "now_playing": None,
        "queue_length": 0,
        "current_source": "local",
    }
    if playback is None:
        return ctx
    try:
        if hasattr(playback, "current_track") and playback.current_track:
            track = playback.current_track
            ctx["now_playing"] = {
                "title": getattr(track, "title", None) or getattr(track, "name", None),
                "artist": getattr(track, "artist", None),
                "album": getattr(track, "album", None),
            }
        if hasattr(playback, "queue_length"):
            ctx["queue_length"] = playback.queue_length
        if hasattr(playback, "source_type"):
            ctx["current_source"] = playback.source_type
    except Exception:
        pass
    return ctx


def _playback_suggestions(playback) -> list[dict[str, Any]]:
    suggestions = []
    ctx = _build_playback_section_context(playback)
    np = ctx.get("now_playing")
    ql = ctx.get("queue_length", 0)
    if np is not None:
        suggestions.append({
            "id": "playback_explain_quality",
            "title": "Explicar calidad de pista actual",
            "description": f"'{np.get('title')}' — conoce la calidad y formato.",
            "section": "playback_hub",
            "action": "explain_current_track_quality",
            "args": {},
            "priority": "low",
            "requires_confirmation": False,
            "reason": "",
        })
    if ql == 0:
        suggestions.append({
            "id": "playback_add_to_queue",
            "title": "Anadir musica a la cola",
            "description": "La cola esta vacia. Anade canciones para seguir escuchando.",
            "section": "playback_hub",
            "action": "add_tracks_to_queue",
            "args": {},
            "priority": "medium",
            "requires_confirmation": True,
            "reason": "queue_length=0",
        })
    return suggestions[:5]
