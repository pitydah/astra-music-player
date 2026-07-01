"""Tests for PromptContextBuilder — sanitized, no paths, no tokens."""

from __future__ import annotations

from integrations.ai_assistant.prompt_context_builder import PromptContextBuilder
from integrations.ai_assistant.schemas import ToolResult


def _safe_snapshot():
    return {
        "section": "library_hub",
        "selection": {"scope": "track", "track": "Song Title", "artist": "Artist"},
        "summary": {"track_count": 100, "album_count": 10},
        "allowed_actions": ["search_library", "draft_playlist"],
    }


class TestPromptContextBuilder:
    def test_build_no_paths(self):
        builder = PromptContextBuilder()
        messages = builder.build("hello", _safe_snapshot())
        text = " ".join(m.get("content", "") for m in messages)
        assert "/home" not in text
        assert "/tmp" not in text
        assert "C:\\" not in text

    def test_build_with_tool_result(self):
        builder = PromptContextBuilder()
        result = ToolResult(name="search_library", success=True, data={"count": 5})
        messages = builder.build("find something", _safe_snapshot(), tool_result=result)
        assert len(messages) >= 2

    def test_build_with_tool_error(self):
        builder = PromptContextBuilder()
        result = ToolResult(name="search_library", success=False, error="DB error")
        messages = builder.build("find", _safe_snapshot(), tool_result=result)
        text = " ".join(m.get("content", "") for m in messages)
        assert "DB error" in text

    def test_build_truncates_long_text(self):
        builder = PromptContextBuilder()
        long_text = "x" * 5000
        messages = builder.build(long_text, _safe_snapshot())
        user_msg = [m for m in messages if m["role"] == "user"]
        assert len(user_msg[0]["content"]) <= 2000

    def test_build_no_tokens(self):
        builder = PromptContextBuilder()
        messages = builder.build("test", _safe_snapshot())
        text = " ".join(m.get("content", "") for m in messages)
        assert "token" not in text.lower() or "api_key" not in text.lower()

    def test_build_includes_section(self):
        builder = PromptContextBuilder()
        messages = builder.build("test", _safe_snapshot())
        text = " ".join(m.get("content", "") for m in messages)
        assert "library_hub" in text
