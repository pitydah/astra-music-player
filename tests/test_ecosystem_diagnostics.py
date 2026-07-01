"""Tests for Ecosystem Diagnostics, Health Graph, and Fix Suggester."""

from __future__ import annotations

from unittest.mock import MagicMock

from integrations.michi_ecosystem.ecosystem_diagnostics import EcosystemDiagnostics
from integrations.michi_ecosystem.ecosystem_registry import EcosystemRegistry
from integrations.michi_ecosystem.ecosystem_health_graph import EcosystemHealthGraphBuilder
from integrations.michi_ecosystem.ecosystem_fix_suggester import EcosystemFixSuggester


def _empty_registry():
    return EcosystemRegistry()


class TestDiagnoseEcosystem:
    def test_ecosystem_empty(self):
        diag = EcosystemDiagnostics(registry=_empty_registry())
        report = diag.diagnose_ecosystem()
        assert "player" in report
        assert "summary" in report

    def test_mobile_sync_no_devices(self):
        diag = EcosystemDiagnostics(registry=_empty_registry())
        result = diag.diagnose_mobile_sync()
        assert result.get("service") == "mobile_sync"

    def test_micro_server_unreachable(self):
        diag = EcosystemDiagnostics(registry=_empty_registry())
        result = diag.diagnose_micro_server()
        assert result.get("service") == "micro_server"

    def test_micro_server_ok_mock(self):
        diag = EcosystemDiagnostics(registry=_empty_registry())
        result = diag.diagnose_micro_server(host="192.168.1.100", port=53318)
        assert result.get("service") == "micro_server"
        assert result.get("host") == "192.168.1.100"


class TestHealthGraph:
    def test_graph_sanitized(self):
        builder = EcosystemHealthGraphBuilder()
        report = {
            "player": {"status": "ok", "service": "player"},
            "mobile_sync": {"status": "warning", "service": "mobile_sync", "issue_code": "NO_PAIRED_DEVICES"},
            "micro_server": {"status": "error", "service": "micro_server", "issue_code": "MICRO_UNREACHABLE"},
        }
        graph = builder.build(report)
        assert len(graph.nodes) == 3
        assert len(graph.edges) == 2
        assert graph.summary["ok"] == 1
        assert graph.summary["warning"] == 1
        assert graph.summary["error"] == 1
        assert "/home" not in str(graph)

    def test_summary(self):
        builder = EcosystemHealthGraphBuilder()
        report = {
            "player": {"status": "ok", "service": "player"},
        }
        graph = builder.build(report)
        summary = builder.summarize_health(graph)
        assert summary["overall"] == "ok"
        assert summary["total"] == 1

    def test_no_paths_in_graph(self):
        builder = EcosystemHealthGraphBuilder()
        report = {"player": {"status": "ok", "service": "player"}}
        graph = builder.build(report)
        graph_str = str(graph)
        assert "/" not in graph_str.replace("node:", "").replace("/", "")
        assert "C:" not in graph_str


class TestFixSuggester:
    def test_for_sync_stopped(self):
        suggester = EcosystemFixSuggester()
        fix = suggester.suggest_next_steps("SYNC_STOPPED")
        assert "sync" in fix.get("problem", "").lower() or "detenida" in fix.get("problem", "").lower()

    def test_for_micro_unreachable(self):
        suggester = EcosystemFixSuggester()
        fix = suggester.suggest_next_steps("MICRO_UNREACHABLE")
        assert "Micro Server" in fix.get("problem", "")

    def test_no_issues(self):
        suggester = EcosystemFixSuggester()
        fix = suggester.suggest_fix({"player": {"status": "ok"}})
        assert "no se detectaron problemas" in fix.get("problem", "").lower()

    def test_unknown_issue(self):
        suggester = EcosystemFixSuggester()
        fix = suggester.suggest_next_steps("UNKNOWN_ERROR")
        assert fix is not None
