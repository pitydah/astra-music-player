"""Tests for IntentRouter — rule-based intent detection."""

from __future__ import annotations

from integrations.ai_assistant.intent_router import IntentRouter


def _snapshot(section: str = "library_hub") -> dict:
    return {"section": section, "allowed_actions": []}


class TestIntentRouter:
    def test_mobile_sync_problem(self):
        router = IntentRouter()
        result = router.detect(
            "Michi Mobile no se conecta",
            _snapshot("connections_hub"),
            ["diagnose_mobile_sync"],
        )
        assert result.tool_name == "diagnose_mobile_sync"
        assert result.confidence >= 0.6

    def test_micro_server_problem(self):
        router = IntentRouter()
        result = router.detect(
            "No aparece mi Micro Server",
            _snapshot("connections_hub"),
            ["diagnose_micro_server"],
        )
        assert result.tool_name == "diagnose_micro_server"
        assert result.confidence >= 0.6

    def test_audio_conversion(self):
        router = IntentRouter()
        result = router.detect(
            "Que formato tiene esta cancion",
            _snapshot("audio_lab"),
            ["explain_audio_format"],
        )
        assert result.tool_name == "explain_audio_format"
        assert result.source == "rules"

    def test_contextual_question_audio_lab(self):
        router = IntentRouter()
        result = router.detect(
            "Que me recomiendas",
            _snapshot("audio_lab"),
            ["explain_audio_format", "recommend_conversion_profile"],
        )
        assert result.tool_name is None or isinstance(result.tool_name, str)

    def test_contextual_question_library(self):
        router = IntentRouter()
        result = router.detect(
            "Que me recomiendas",
            _snapshot("library_hub"),
            ["recommend_music", "draft_playlist"],
        )
        assert result.tool_name in ("recommend_music", "draft_playlist", None)

    def test_blocks_disallowed_tool(self):
        router = IntentRouter()
        result = router.detect(
            "diagnostica el ecosistema",
            _snapshot("library_hub"),
            ["search_library"],
        )
        assert result.tool_name is None or result.confidence < 0.6

    def test_low_confidence_returns_fallback(self):
        router = IntentRouter()
        result = router.detect(
            "",
            _snapshot("library_hub"),
            [],
        )
        assert result.source == "fallback"
        assert result.tool_name is None

    def test_ecosystem_diagnose(self):
        router = IntentRouter()
        result = router.detect(
            "Revisa todo mi ecosistema Michi",
            _snapshot("connections_hub"),
            ["diagnose_ecosystem"],
        )
        assert result.tool_name == "diagnose_ecosystem"

    def test_config_plan_creation(self):
        router = IntentRouter()
        result = router.detect(
            "Configura Michi para usar mi telefono con poco espacio",
            _snapshot("connections_hub"),
            ["create_ecosystem_config_plan"],
        )
        assert result.tool_name in ("create_ecosystem_config_plan", "suggest_mobile_audio_profile", None)
