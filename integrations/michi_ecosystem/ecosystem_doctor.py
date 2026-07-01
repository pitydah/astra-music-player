"""MichiEcosystemDoctor — facade over existing Michi Link services.

Reuses DiagnosticsService, MicroServerService, PlayerMicroCompatibilityReport.
Does NOT duplicate those services.
"""

from __future__ import annotations

import contextlib
import logging
from typing import Any

from integrations.michi_ecosystem import constants as C
from integrations.michi_ecosystem.sanitizer import sanitize_for_diagnostic

logger = logging.getLogger("michi.ecosystem.doctor")


class MichiEcosystemDoctor:
    def __init__(
        self,
        diagnostics_service=None,
        micro_server_service=None,
        compatibility_report=None,
        sync_mgr=None,
        device_registry=None,
        settings_provider=None,
        michi_link_ctrl=None,
        remote_server_loader=None,
        snapcast_manager=None,
        ha_client=None,
    ):
        self._diag_svc = diagnostics_service
        self._micro_svc = micro_server_service
        self._compat_report = compatibility_report
        self._sync = sync_mgr
        self._registry = device_registry
        self._settings = settings_provider
        self._michi_link_ctrl = michi_link_ctrl
        self._remote_loader = remote_server_loader
        self._snapcast = snapcast_manager
        self._ha_client = ha_client

    def diagnose_home_summary(self) -> dict[str, Any]:
        return {"player": self._safe_diag("check_player_api"), "sync": self._safe_diag("check_sync_server"), "pairing": self._safe_diag("check_pairing"), "playback": self._safe_diag("check_playback"), "queue": self._safe_diag("check_queue")}

    def diagnose_ecosystem(self) -> dict[str, Any]:
        if self._diag_svc is not None:
            with contextlib.suppress(Exception):
                return self._diag_svc.generate_report(handler=None, registry=self._registry, micro_host="", player_service=None)
        return {"player": self.diagnose_player(), "mobile_sync": self.diagnose_mobile_sync(), "micro_server": self.diagnose_micro_server(), "home_audio": self.diagnose_home_audio(), "remote_music_servers": self.diagnose_remote_music_servers(), "assistant": self.diagnose_assistant_runtime()}

    def diagnose_player(self) -> dict[str, Any]:
        if self._diag_svc is not None:
            with contextlib.suppress(Exception):
                return self._diag_svc.check_player_api()
        return {"status": C.STATUS_OK, "service": "player"}

    def diagnose_mobile_sync(self) -> dict[str, Any]:
        result: dict[str, Any] = {"status": C.STATUS_NO_DEVICE, "service": "mobile_sync", "paired_devices": 0}
        if self._diag_svc is not None:
            with contextlib.suppress(Exception):
                pair_check = self._diag_svc.check_pairing(registry=self._registry)
                result["status"] = pair_check.get("status", C.STATUS_NO_DEVICE)
                result["paired_devices"] = pair_check.get("count", 0)
        if self._sync is not None:
            with contextlib.suppress(Exception):
                result["sync_active"] = self._sync.isRunning() if hasattr(self._sync, "isRunning") else getattr(self._sync, "is_active", False)
        if result.get("paired_devices", 0) == 0:
            result["issue_code"] = C.NO_PAIRED_DEVICES
        return sanitize_for_diagnostic(result)

    def diagnose_micro_server(self, host: str = "", port: int = 53318) -> dict[str, Any]:
        result: dict[str, Any] = {"service": "micro_server", "host": host, "port": port}
        if self._michi_link_ctrl is not None:
            with contextlib.suppress(Exception):
                state = self._michi_link_ctrl.get_connection_state() if hasattr(self._michi_link_ctrl, "get_connection_state") else ""
                if state:
                    result["state"] = state
                    return result
        if not host:
            with contextlib.suppress(Exception):
                from core.settings_manager import get_str
                host = get_str("michi_link/micro_host", "")
            if not host:
                result["state"] = C.STATUS_NOT_CONFIGURED
                result["issue_code"] = C.MICRO_NOT_CONFIGURED
                return sanitize_for_diagnostic(result)
            result["host"] = host
        if self._micro_svc is not None:
            with contextlib.suppress(Exception):
                info = self._micro_svc.discover(host, port)
                if info and getattr(info, "ok", False):
                    data = info.data if hasattr(info, "data") else {}
                    if data and getattr(data, "requires_pairing", False):
                        result["state"] = C.STATUS_REQUIRES_PAIRING
                        result["issue_code"] = C.MICRO_REQUIRES_PAIRING
                    else:
                        result["state"] = C.STATUS_CONNECTED
                    return sanitize_for_diagnostic(result)
        elif self._diag_svc is not None:
            with contextlib.suppress(Exception):
                check = self._diag_svc.check_remote_micro(host, port)
                if check.get("status") == C.STATUS_OK:
                    result["state"] = C.STATUS_CONNECTED
                    return sanitize_for_diagnostic(result)
        result["state"] = C.STATUS_UNREACHABLE
        result["issue_code"] = C.MICRO_UNREACHABLE
        return sanitize_for_diagnostic(result)

    def diagnose_micro_contract(self, host: str = "", port: int = 53318) -> dict[str, Any]:
        if not host:
            return {"status": C.STATUS_NOT_CONFIGURED, "service": "micro_contract", "issue_code": C.MICRO_NOT_CONFIGURED}
        if self._compat_report is not None:
            with contextlib.suppress(Exception):
                report = self._compat_report.generate({"host": host, "port": port})
                if report.get("status") != C.STATUS_OK:
                    report["issue_code"] = C.MICRO_CONTRACT_MISMATCH
                return sanitize_for_diagnostic(report)
        return {"status": C.STATUS_UNKNOWN, "service": "micro_contract"}

    def diagnose_remote_music_servers(self) -> dict[str, Any]:
        result: dict[str, Any] = {"configured": False, "count": 0, "servers": []}
        loader = self._remote_loader
        if loader is None:
            with contextlib.suppress(Exception):
                from streaming.subsonic_client import load_servers as _loader
                loader = _loader
        if loader is not None:
            with contextlib.suppress(Exception):
                servers = loader()
                if servers:
                    safe = [{"name": getattr(s, "name", ""), "type": getattr(s, "server_type", "")} for s in servers]
                    result["configured"] = True
                    result["count"] = len(safe)
                    result["servers"] = safe
        return result

    def diagnose_home_audio(self) -> dict[str, Any]:
        result: dict[str, Any] = {"status": C.STATUS_DISABLED, "service": "home_audio"}
        ha_reachable = False
        snapcast_active = False
        if self._ha_client is not None:
            with contextlib.suppress(Exception):
                conn = self._ha_client.check_connection() if hasattr(self._ha_client, "check_connection") else None
                ha_reachable = bool(conn)
        if self._snapcast is not None:
            with contextlib.suppress(Exception):
                snapcast_active = self._snapcast.is_running() if hasattr(self._snapcast, "is_running") else False
        with contextlib.suppress(Exception):
            from core.settings_manager import get_bool, get_str
            ha_url = get_str("home_audio/ha_base_url", "")
            ha_enabled = get_bool("home_audio/enabled")
            snap_enabled = get_bool("home_audio/snapserver_enabled")
            michi_api = get_bool("home_audio/michi_api_enabled")
            mdns = get_bool("home_audio/mdns_enabled")
            if ha_reachable or snapcast_active:
                result["status"] = C.STATUS_ACTIVE if C.STATUS_ACTIVE else "active"
                result["ha_reachable"] = ha_reachable
                result["snapcast_active"] = snapcast_active
                result["michi_api_enabled"] = michi_api
            elif ha_url and ha_enabled:
                result["status"] = C.STATUS_CONFIGURED
            elif ha_enabled or snap_enabled or michi_api:
                result["status"] = C.STATUS_PARTIAL
        return sanitize_for_diagnostic(result)

    def diagnose_assistant_runtime(self) -> dict[str, Any]:
        result: dict[str, Any] = {"status": C.STATUS_DISABLED, "service": "assistant"}
        with contextlib.suppress(Exception):
            from core.settings_manager import get_bool, get_str
            enabled = get_bool("ai_assistant/enabled")
            offline = get_bool("ai_assistant/offline_strict")
            model = get_str("ai_assistant/model", "")
            url = get_str("ai_assistant/base_url", "http://127.0.0.1:11434")
            if enabled:
                result["status"] = C.STATUS_CONFIGURED
                result["model"] = model
                result["offline_strict"] = offline
                result["localhost"] = "127.0.0.1" in url or "localhost" in url or "::1" in url
        return sanitize_for_diagnostic(result)

    def _safe_diag(self, method_name: str) -> dict[str, Any]:
        if self._diag_svc is None:
            return {"status": C.STATUS_UNKNOWN}
        method = getattr(self._diag_svc, method_name, None)
        if method is None:
            return {"status": C.STATUS_UNKNOWN}
        with contextlib.suppress(Exception):
            return method()
        return {"status": C.STATUS_ERROR}
