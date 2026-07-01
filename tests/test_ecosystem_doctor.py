"""Tests for MichiEcosystemDoctor — facade over existing Michi Link services."""

from __future__ import annotations

from unittest.mock import MagicMock


from integrations.michi_ecosystem.ecosystem_doctor import MichiEcosystemDoctor
from integrations.michi_ecosystem import constants as C


class TestDiagnoseMicroServer:
    def test_not_configured(self):
        doctor = MichiEcosystemDoctor()
        result = doctor.diagnose_micro_server(host="")
        assert result["state"] == C.STATUS_NOT_CONFIGURED
        assert result["issue_code"] == C.MICRO_NOT_CONFIGURED

    def test_unreachable(self):
        diag_svc = MagicMock()
        diag_svc.check_remote_micro.return_value = {"status": "error"}
        doctor = MichiEcosystemDoctor(diagnostics_service=diag_svc)
        result = doctor.diagnose_micro_server(host="192.168.1.100", port=53318)
        assert result["state"] == C.STATUS_UNREACHABLE

    def test_connected_via_diag(self):
        diag_svc = MagicMock()
        diag_svc.check_remote_micro.return_value = {"status": "ok"}
        doctor = MichiEcosystemDoctor(diagnostics_service=diag_svc)
        result = doctor.diagnose_micro_server(host="192.168.1.100")
        assert result["state"] == C.STATUS_CONNECTED

    def test_requires_pairing(self):
        micro_svc = MagicMock()
        info = MagicMock()
        info.ok = True
        info.data = MagicMock(requires_pairing=True)
        micro_svc.discover.return_value = info
        doctor = MichiEcosystemDoctor(micro_server_service=micro_svc)
        result = doctor.diagnose_micro_server(host="192.168.1.100")
        assert result["state"] == C.STATUS_REQUIRES_PAIRING


class TestDiagnoseMobileSync:
    def test_no_devices(self):
        doctor = MichiEcosystemDoctor()
        result = doctor.diagnose_mobile_sync()
        assert result["status"] in (C.STATUS_NO_DEVICE,)

    def test_uses_diagnostics_service(self):
        diag_svc = MagicMock()
        diag_svc.check_pairing.return_value = {"status": "ok", "count": 2}
        doctor = MichiEcosystemDoctor(diagnostics_service=diag_svc)
        result = doctor.diagnose_mobile_sync()
        assert result["paired_devices"] == 2


class TestDiagnoseRemoteServers:
    def test_separate_from_micro(self):
        doctor = MichiEcosystemDoctor()
        result = doctor.diagnose_remote_music_servers()
        assert "configured" in result
        assert "count" in result


class TestSanitize:
    def test_sanitizes_tokens(self):
        from integrations.michi_ecosystem.sanitizer import sanitize_for_diagnostic
        data = {"status": "ok", "token": "secret123", "password": "pass", "path": "/home/user/music"}
        clean = sanitize_for_diagnostic(data)
        assert "token" not in clean
        assert "password" not in clean
        assert "path" not in clean

    def test_sanitizes_paths(self):
        from integrations.michi_ecosystem.sanitizer import sanitize_for_diagnostic
        data = {"filepath": "/home/user/music/song.flac"}
        clean = sanitize_for_diagnostic(data)
        fp = clean.get("filepath", "")
        assert isinstance(fp, str)
        assert "/home/" not in fp


class TestHomeAudio:
    def test_disabled_by_default(self):
        doctor = MichiEcosystemDoctor()
        result = doctor.diagnose_home_audio()
        assert result["status"] in (C.STATUS_DISABLED,)


class TestAssistantRuntime:
    def test_disabled_by_default(self):
        doctor = MichiEcosystemDoctor()
        result = doctor.diagnose_assistant_runtime()
        assert result["status"] in (C.STATUS_DISABLED,)


class TestOverallStatus:
    def test_overall_from_statuses_ok(self):
        assert C.overall_from_statuses([C.STATUS_OK, C.STATUS_CONNECTED]) == C.STATUS_OK

    def test_overall_from_statuses_warning(self):
        assert C.overall_from_statuses([C.STATUS_OK, C.STATUS_UNREACHABLE]) == C.STATUS_WARNING

    def test_overall_from_statuses_error(self):
        assert C.overall_from_statuses([C.STATUS_OK, C.STATUS_ERROR]) == C.STATUS_ERROR


class TestHealthGraph:
    def test_empty(self):
        from integrations.michi_ecosystem.health_graph import build_health_graph, summarize_health
        graph = build_health_graph({})
        summary = summarize_health(graph)
        assert summary["total"] == 0

    def test_with_player(self):
        from integrations.michi_ecosystem.health_graph import build_health_graph, summarize_health
        report = {"player": {"status": "ok", "service": "player"}}
        graph = build_health_graph(report)
        assert len(graph.nodes) >= 1
        summary = summarize_health(graph)
        assert "overall" in summary

    def test_no_sensitive_data(self):
        from integrations.michi_ecosystem.health_graph import build_health_graph
        report = {"player": {"status": "ok", "token": "secret", "service": "player"}}
        graph = build_health_graph(report)
        graph_str = str(graph)
        assert "secret" not in graph_str


class TestFixSuggester:
    def test_suggest_fix_known_issue(self):
        from integrations.michi_ecosystem.fix_suggester import suggest_next_steps
        fix = suggest_next_steps(C.MICRO_UNREACHABLE)
        assert "recommended_fix" in fix

    def test_suggest_fix_unknown_issue(self):
        from integrations.michi_ecosystem.fix_suggester import suggest_next_steps
        fix = suggest_next_steps("UNKNOWN")
        assert fix is not None

    def test_suggest_fix_from_report(self):
        from integrations.michi_ecosystem.fix_suggester import suggest_fix
        fix = suggest_fix({"micro_server": {"status": "error", "issue_code": C.MICRO_UNREACHABLE}})
        assert "recommended_fix" in fix

    def test_no_issues(self):
        from integrations.michi_ecosystem.fix_suggester import suggest_fix
        fix = suggest_fix({"player": {"status": "ok"}})
        assert "no se detectaron problemas" in fix.get("problem", "").lower()
