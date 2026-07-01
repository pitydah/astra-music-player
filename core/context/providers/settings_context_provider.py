"""Section context provider for settings section."""

from __future__ import annotations

from typing import Any

from core.context.section_context_provider import SectionContextProvider


class SettingsContextProvider(SectionContextProvider):
    section_key = "settings"

    def __init__(self, db=None, settings_manager=None):
        self._db = db
        self._settings = settings_manager

    def get_context(self) -> dict[str, Any]:
        return _build_settings_context(self._settings)

    def get_suggestions(self) -> list[dict[str, Any]]:
        return _settings_suggestions(self._settings)

    def get_allowed_actions(self) -> list[str]:
        return [
            "open_section",
        ]


def _build_settings_context(settings) -> dict[str, Any]:
    ctx: dict[str, Any] = {
        "section": "settings",
        "ai_assistant_configured": False,
        "ollama_model": "",
        "sync_enabled": False,
        "audio_analysis_enabled": False,
        "offline_strict": True,
    }
    if settings is None:
        return ctx
    try:
        if hasattr(settings, "get_str"):
            model = settings.get_str("ai_assistant/model", "")
            ctx["ai_assistant_configured"] = bool(model)
            ctx["ollama_model"] = model
            ctx["sync_enabled"] = settings.get_bool("sync/enabled", False)
            ctx["audio_analysis_enabled"] = settings.get_bool("audio_analysis/enabled", False)
            ctx["offline_strict"] = settings.get_bool("ai_assistant/offline_strict", True)
    except Exception:
        pass
    return ctx


def _settings_suggestions(settings) -> list[dict[str, Any]]:
    suggestions = []
    ctx = _build_settings_context(settings)
    if not ctx.get("ai_assistant_configured"):
        suggestions.append({
            "id": "settings_configure_ollama",
            "title": "Configurar IA local",
            "description": "No hay modelo de Ollama configurado. Configuralo para usar Michi Assistant.",
            "section": "settings",
            "action": "open_section",
            "args": {"target": "ai_assistant"},
            "priority": "medium",
            "requires_confirmation": False,
            "reason": "ai_assistant_configured=False",
        })
    return suggestions[:5]
