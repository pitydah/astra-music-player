"""ContextualSuggestionEngine — generates local suggestions without calling Ollama."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from core.context.context_snapshot import sanitize_snapshot


@dataclass
class ContextualSuggestion:
    id: str
    title: str
    description: str
    section: str
    action: str
    args: dict[str, Any] = field(default_factory=dict)
    priority: str = "low"
    requires_confirmation: bool = False
    reason: str = ""
    dismissible: bool = True


_MAX_SUGGESTIONS = 5
_MAX_VISIBLE = 3


class ContextualSuggestionEngine:
    def __init__(self):
        self._last_section = ""
        self._last_suggestions: list[dict[str, Any]] = []

    def get_suggestions(self, section_snapshot: dict[str, Any], section_provider_suggestions: list[dict[str, Any]]) -> list[dict[str, Any]]:
        section = section_snapshot.get("section", "")
        if not section:
            return []
        raw = list(section_provider_suggestions)
        raw = [s for s in raw if not self._is_duplicate(s)]
        raw = sorted(raw, key=_priority_key, reverse=True)
        raw = raw[:_MAX_SUGGESTIONS]
        self._last_section = section
        self._last_suggestions = raw
        return sanitize_snapshot(raw)

    def get_visible(self) -> list[dict[str, Any]]:
        return self._last_suggestions[:_MAX_VISIBLE]

    def get_all(self) -> list[dict[str, Any]]:
        return list(self._last_suggestions)

    def dismiss(self, suggestion_id: str) -> bool:
        before = len(self._last_suggestions)
        self._last_suggestions = [s for s in self._last_suggestions if s.get("id") != suggestion_id]
        return len(self._last_suggestions) < before

    def clear(self) -> None:
        self._last_section = ""
        self._last_suggestions = []

    def _is_duplicate(self, suggestion: dict[str, Any]) -> bool:
        sid = suggestion.get("id", "")
        return any(s.get("id") == sid for s in self._last_suggestions)


def _priority_key(s: dict[str, Any]) -> int:
    mapping = {"critical": 4, "high": 3, "medium": 2, "low": 1}
    return mapping.get(s.get("priority", "low"), 0)
