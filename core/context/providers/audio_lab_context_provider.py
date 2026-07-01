"""Section context provider for audio_lab sections."""

from __future__ import annotations

from typing import Any

from core.context.section_context_provider import SectionContextProvider


class AudioLabContextProvider(SectionContextProvider):
    section_key = "audio_lab"

    def __init__(self, db=None, analysis_service=None):
        self._db = db
        self._analysis_svc = analysis_service

    def get_context(self) -> dict[str, Any]:
        return _build_audio_lab_context(self._db)

    def get_suggestions(self) -> list[dict[str, Any]]:
        return _audio_lab_suggestions(self._db)

    def get_allowed_actions(self) -> list[str]:
        return [
            "explain_audio_format",
            "recommend_conversion_profile",
            "suggest_mobile_audio_profile",
            "suggest_micro_server_streaming_profile",
            "analyze_track_audio",
            "list_tracks_missing_features",
        ]


def _build_audio_lab_context(db) -> dict[str, Any]:
    ctx: dict[str, Any] = {
        "section": "audio_lab",
        "analysis": {
            "audio_analysis_enabled": False,
            "missing_features_count": 0,
            "conversion_available": False,
        },
    }
    if db is None:
        return ctx
    try:
        if hasattr(db, "conn") and db.conn:
            conn = db.conn
            ctx["analysis"]["missing_features_count"] = conn.execute(
                "SELECT COUNT(*) FROM media_items WHERE "
                "analysis_status IS NULL AND deleted_at IS NULL AND kind='audio'"
            ).fetchone()[0]
            ctx["analysis"]["conversion_available"] = True
    except Exception:
        pass
    return ctx


def _audio_lab_suggestions(db) -> list[dict[str, Any]]:
    suggestions = []
    ctx = _build_audio_lab_context(db).get("analysis", {})
    missing = ctx.get("missing_features_count", 0)
    if missing > 0:
        suggestions.append({
            "id": "audio_lab_missing_features",
            "title": "Analizar audio pendiente",
            "description": f"{missing} canciones sin analisis acustico.",
            "section": "audio_lab",
            "action": "list_tracks_missing_features",
            "args": {},
            "priority": "medium",
            "requires_confirmation": False,
            "reason": f"missing_features_count={missing}",
        })
    suggestions.append({
        "id": "audio_lab_explain_format",
        "title": "Explicar formatos de audio",
        "description": "Descubre la calidad de tus archivos de audio.",
        "section": "audio_lab",
        "action": "explain_audio_format",
        "args": {},
        "priority": "low",
        "requires_confirmation": False,
        "reason": "",
    })
    return suggestions[:5]
