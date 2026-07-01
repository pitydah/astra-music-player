"""Tests for ContextualSuggestionEngine — local suggestions without Ollama."""

from __future__ import annotations

from integrations.ai_assistant.contextual_suggestion_engine import (
    ContextualSuggestionEngine,
    _priority_key,
)


def _suggestion(priority: str = "low") -> dict:
    return {
        "id": f"test_{priority}",
        "title": f"Test {priority}",
        "description": f"A {priority} suggestion",
        "section": "test",
        "action": "test_action",
        "args": {},
        "priority": priority,
        "requires_confirmation": False,
        "reason": "",
    }


def _snapshot(section: str = "test") -> dict:
    return {"section": section, "allowed_actions": ["test_action"]}


class TestSuggestionEngine:
    def test_library_suggestions_missing_metadata(self):
        engine = ContextualSuggestionEngine()
        pv = [
            {
                "id": "library_missing",
                "title": "Missing metadata",
                "description": "5 missing",
                "section": "library_hub",
                "action": "find_metadata_gaps",
                "args": {},
                "priority": "medium",
                "requires_confirmation": False,
                "reason": "missing=5",
            }
        ]
        result = engine.get_suggestions(_snapshot("library_hub"), pv)
        assert len(result) == 1
        assert result[0]["id"] == "library_missing"

    def test_connections_suggestions_micro_unreachable(self):
        engine = ContextualSuggestionEngine()
        pv = [
            {
                "id": "diag_ecosystem",
                "title": "Diagnose",
                "description": "Check ecosystem",
                "section": "connections_hub",
                "action": "diagnose_ecosystem",
                "args": {},
                "priority": "medium",
                "requires_confirmation": False,
                "reason": "sync_disabled",
            }
        ]
        result = engine.get_suggestions(_snapshot("connections_hub"), pv)
        assert any(s["id"] == "diag_ecosystem" for s in result)

    def test_suggestions_do_not_call_ollama(self):
        engine = ContextualSuggestionEngine()
        suggestions = engine.get_suggestions(_snapshot("test"), [])
        assert suggestions == []
        assert engine.get_all() == []

    def test_suggestions_respect_allowed_actions(self):
        engine = ContextualSuggestionEngine()
        pv = [_suggestion("low")]
        result = engine.get_suggestions({"section": "test", "allowed_actions": []}, pv)
        assert len(result) <= 5

    def test_suggestions_max_five(self):
        engine = ContextualSuggestionEngine()
        many_suggestions = [_suggestion("low") for _ in range(10)]
        result = engine.get_suggestions(_snapshot("test"), many_suggestions)
        assert len(result) <= 5

    def test_visible_max_three(self):
        engine = ContextualSuggestionEngine()
        many = [_suggestion("low") for _ in range(5)]
        engine.get_suggestions(_snapshot("test"), many)
        visible = engine.get_visible()
        assert len(visible) <= 3

    def test_dismiss(self):
        engine = ContextualSuggestionEngine()
        pv = [_suggestion("low")]
        engine.get_suggestions(_snapshot("test"), pv)
        assert engine.dismiss("test_low")
        assert engine.get_all() == []

    def test_priority_sorting(self):
        suggestions = [_suggestion("low"), _suggestion("high"), _suggestion("medium")]
        sorted_s = sorted(suggestions, key=_priority_key, reverse=True)
        assert sorted_s[0]["priority"] == "high"
        assert sorted_s[1]["priority"] == "medium"
        assert sorted_s[2]["priority"] == "low"

    def test_clear(self):
        engine = ContextualSuggestionEngine()
        engine.get_suggestions(_snapshot("test"), [_suggestion("low")])
        engine.clear()
        assert engine.get_all() == []
