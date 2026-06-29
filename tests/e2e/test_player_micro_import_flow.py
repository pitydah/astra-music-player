"""E2E: Player → Micro Server import flow — full lifecycle with mocks.

Tests: discover → pair → create session → upload tracks → commit → rollback.
Also tests continue_on_server transfer_queue and remote playback control.
"""
from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from integrations.michi_link.client import RemoteServerInfo


def _make_server() -> RemoteServerInfo:
    return RemoteServerInfo(
        host="10.0.0.100",
        port=53318,
        alias="MicroTest",
        server_device_id="micro_001",
        requires_pairing=True,
        device_token="tok_abc123",
        device_id="player_d1",
    )


class TestPlayerMicroImportFlow:
    def test_discover_micro_server(self):
        from integrations.michi_link.services.micro_server_service import (
            MicroServerService,
        )
        svc = MicroServerService()
        with patch.object(svc._client, "discover", return_value=_make_server()):
            result = svc.discover("10.0.0.100")
            assert result.success
            assert result.data.alias == "MicroTest"

    def test_discover_micro_server_fails(self):
        from integrations.michi_link.services.micro_server_service import (
            MicroServerService,
        )
        svc = MicroServerService()
        with patch.object(svc._client, "discover", return_value=None):
            result = svc.discover("10.0.0.200")
            assert not result.success
            assert result.error_code == "DISCOVERY_FAILED"

    def test_pair_with_micro_server(self):
        from integrations.michi_link.services.micro_server_service import (
            MicroServerService,
        )
        svc = MicroServerService()
        server = _make_server()
        with patch.object(svc._client, "pair", return_value=True):
            result = svc.pair(server, username="admin", password="pass")
            assert result.success
            assert "device_token" in str(result.data)

    def test_pair_with_micro_server_rejected(self):
        from integrations.michi_link.services.micro_server_service import (
            MicroServerService,
        )
        svc = MicroServerService()
        with patch.object(svc._client, "pair", return_value=False):
            result = svc.pair(_make_server())
            assert not result.success
            assert result.error_code == "PAIR_FAILED"

    def test_create_import_session(self):
        from integrations.michi_link.services.import_to_server_service import (
            ImportToServerService,
        )
        svc = ImportToServerService()
        server = _make_server()
        result = svc.create_session(server, ["t1", "t2", "t3"])
        assert result.success
        assert result.data["total_tracks"] == 3
        assert result.data["session_id"] != ""

    def test_upload_track_success(self):
        from integrations.michi_link.services.import_to_server_service import (
            ImportToServerService,
        )
        svc = ImportToServerService()
        result = svc.create_session(_make_server(), ["t1"])
        sid = result.data["session_id"]

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.read.return_value = b"fake_audio_data"
            mock_urlopen.return_value.__enter__.return_value = mock_resp

            result2 = svc.upload_track(sid, "t1", "/api/v1/stream/t1")
            assert result2.success
            assert result2.data["bytes"] > 0

    def test_upload_track_session_not_found(self):
        from integrations.michi_link.services.import_to_server_service import (
            ImportToServerService,
        )
        svc = ImportToServerService()
        result = svc.upload_track("invalid_session", "t1", "/stream/t1")
        assert not result.success
        assert result.error_code == "INVALID_SESSION"

    def test_commit_session_success(self):
        from integrations.michi_link.services.import_to_server_service import (
            ImportToServerService,
        )
        svc = ImportToServerService()
        r1 = svc.create_session(_make_server(), ["t1"])
        sid = r1.data["session_id"]

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.read.return_value = b"d"
            mock_urlopen.return_value.__enter__.return_value = mock_resp
            svc.upload_track(sid, "t1", "/api/v1/stream/t1")

        r2 = svc.commit_session(sid)
        assert r2.success
        assert r2.data["uploaded"] == 1

    def test_rollback_session(self):
        from integrations.michi_link.services.import_to_server_service import (
            ImportToServerService,
        )
        svc = ImportToServerService()
        r1 = svc.create_session(_make_server(), ["t1"])
        sid = r1.data["session_id"]
        result = svc.rollback_session(sid)
        assert result.success
        assert svc.get_session(sid) is None

    def test_continue_on_server_transfer_queue(self):
        from integrations.michi_link.services.continue_on_server_service import (
            ContinueOnServerService,
        )
        svc = ContinueOnServerService()
        server = _make_server()

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.read.return_value.decode.return_value = json.dumps({"ok": True})
            mock_urlopen.return_value.__enter__.return_value = mock_resp
            result = svc.transfer_queue(server, ["t1", "t2"], position_ms=30000)
            assert result.success

    def test_continue_on_server_start_remote(self):
        from integrations.michi_link.services.continue_on_server_service import (
            ContinueOnServerService,
        )
        svc = ContinueOnServerService()

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.status = 200
            mock_urlopen.return_value.__enter__.return_value = mock_resp
            result = svc.start_remote_playback(_make_server())
            assert result.success

    def test_continue_on_server_stop_remote(self):
        from integrations.michi_link.services.continue_on_server_service import (
            ContinueOnServerService,
        )
        svc = ContinueOnServerService()

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.status = 200
            mock_urlopen.return_value.__enter__.return_value = mock_resp
            result = svc.stop_remote_playback(_make_server())
            assert result.success

    def test_remote_library_get_tracks(self):
        from integrations.michi_link.services.remote_library_service import (
            RemoteLibraryService,
        )
        svc = RemoteLibraryService()
        with patch.object(svc._micro, "get_tracks") as mock_gt:
            mock_gt.return_value = type("R", (), {"success": True, "data": [{"id": 1}]})()
            result = svc.get_tracks(_make_server())
            assert result.success

class TestDiagnosticsService:
    def test_diagnostics_generates_report(self):
        from integrations.michi_link.services.diagnostics_service import (
            DiagnosticsService,
        )
        svc = DiagnosticsService()
        report = svc.generate_report(registry=MagicMock())
        assert "player_api" in report
        assert "sync_server" in report
        assert "pairing" in report
        assert "micro_server_client" in report
        assert "errors" in report

    def test_diagnostics_pairing_with_devices(self):
        from integrations.michi_link.services.diagnostics_service import (
            DiagnosticsService,
        )
        svc = DiagnosticsService()
        registry = MagicMock()
        dev1 = MagicMock()
        dev1.token_hash = "abc"
        dev1.revoked_at = ""
        dev2 = MagicMock()
        dev2.token_hash = "def"
        dev2.revoked_at = "2025-01-01"
        registry.list_all.return_value = [dev1, dev2]
        result = svc.check_pairing(registry)
        assert result["status"] == "ok"
        assert result["paired"] == 1
        assert result["revoked"] == 1

    def test_diagnostics_remote_micro_unreachable(self):
        from integrations.michi_link.services.diagnostics_service import (
            DiagnosticsService,
        )
        svc = DiagnosticsService()
        result = svc.check_remote_micro("10.0.0.99")
        assert result["status"] in ("unreachable", "skipped")


    def test_remote_library_get_track_count(self):
        from integrations.michi_link.services.remote_library_service import (
            RemoteLibraryService,
        )
        svc = RemoteLibraryService()
        with patch.object(svc._micro, "get_library_stats") as mock_stats:
            mock_stats.return_value = type("R", (), {"success": True, "data": {"audio": 42}})()
            count = svc.get_track_count(_make_server())
            assert count == 42
