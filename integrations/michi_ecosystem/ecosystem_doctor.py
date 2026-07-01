"""MichiEcosystemDoctor — facade over existing Michi Link services.

Reuses DiagnosticsService, MicroServerService, PlayerMicroCompatibilityReport, etc.
Does NOT duplicate those services.
"""

from __future__ import annotations

import logging
from typing import Any

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
        settings=None,
    ):
        self._diag_svc = diagnostics_service
        self._micro_svc = micro_server_service
        self._compat_report = compatibility_report
        self._sync = sync_mgr
        self._registry = device_registry
        self._settings = settings

    def diagnose_home_summary(self) -> dict[str, Any]:
        return {
            "player": self._safe_diag("check_player_api"),
            "sync": self._safe_diag("check_sync_server"),
            "pairing": self._safe_diag("check_pairing"),
            "playback": self._safe_diag("check_playback"),
            "queue": self._safe_diag("check_queue"),
        }

    def diagnose_ecosystem(self) -> dict[str, Any]:
        if self._diag_svc is not None:
            try:
                return self._diag_svc.generate_report(
                    handler=None,
                    registry=self._registry,
                    micro_host="",
                    player_service=None,
                )
            except Exception:
                pass
        return self._fallback_ecosystem()

    def diagnose_player(self) -> dict[str, Any]:
        if self._diag_svc is not None:
            try:
                return self._diag_svc.check_player_api()
            except Exception:
                pass
        return {"status": "unknown", "service": "player"}

    def diagnose_mobile_sync(self) -> dict[str, Any]:
        result: dict[str, Any] = {"status": "unknown", "service": "mobile_sync", "paired_devices": 0}
        if self._diag_svc is not None:
            try:
                pair_check = self._diag_svc.check_pairing(registry=self._registry)
                result["status"] = pair_check.get("status", "unknown")
                result["paired_devices"] = pair_check.get("count", 0)
                result["pairing_detail"] = pair_check
            except Exception:
                pass
        if self._sync is not None:
            import contextlib
            with contextlib.suppress(Exception):
                result["sync_active"] = self._sync.isRunning() if hasattr(self._sync, "isRunning") else getattr(self._sync, "is_active", False)
        if result.get("paired_devices", 0) == 0:
            result["issue_code"] = "NO_PAIRED_DEVICES"
        return sanitize_for_diagnostic(result)

    def diagnose_micro_server(self, host: str = "", port: int = 53318) -> dict[str, Any]:
        result: dict[str, Any] = {"service": "micro_server", "host": host, "port": port}
        if not host:
            result["state"] = "not_configured"
            result["issue_code"] = "MICRO_NOT_CONFIGURED"
            return result
        if self._micro_svc is not None:
            try:
                info = self._micro_svc.discover(host, port)
                if info and getattr(info, "ok", False):
                    result["state"] = "connected"
                    data = info.data if hasattr(info, "data") else {}
                    if data and getattr(data, "requires_pairing", False):
                        result["state"] = "requires_pairing"
                        result["issue_code"] = "MICRO_REQUIRES_PAIRING"
                elif host:
                    result["state"] = "unreachable"
                    result["issue_code"] = "MICRO_UNREACHABLE"
            except Exception:
                result["state"] = "unreachable"
                result["issue_code"] = "MICRO_UNREACHABLE"
        elif self._diag_svc is not None:
            try:
                micro_check = self._diag_svc.check_remote_micro(host, port)
                status = micro_check.get("status", "unknown")
                result["state"] = "connected" if status == "ok" else "unreachable"
                if result["state"] == "unreachable":
                    result["issue_code"] = "MICRO_UNREACHABLE"
            except Exception:
                result["state"] = "unreachable"
                result["issue_code"] = "MICRO_UNREACHABLE"
        else:
            result["state"] = "unknown"
        return sanitize_for_diagnostic(result)

    def diagnose_micro_contract(self, host: str = "", port: int = 53318) -> dict[str, Any]:
        if not host:
            return {"status": "not_configured", "service": "micro_contract"}
        if self._compat_report is not None:
            try:
                report = self._compat_report.generate({"host": host, "port": port})
                return sanitize_for_diagnostic(report)
            except Exception:
                pass
        return {"status": "unknown", "service": "micro_contract"}

    def diagnose_remote_music_servers(self) -> dict[str, Any]:
        result: dict[str, Any] = {"configured": False, "count": 0, "servers": []}
        try:
            from streaming.subsonic_client import load_servers
            servers = load_servers()
            if servers:
                safe = []
                for s in servers:
                    safe.append({"name": getattr(s, "name", ""), "type": getattr(s, "server_type", "")})
                result["configured"] = True
                result["count"] = len(safe)
                result["servers"] = safe
        except Exception:
            pass
        return result

    def diagnose_home_audio(self) -> dict[str, Any]:
        result: dict[str, Any] = {"status": "disabled", "service": "home_audio"}
        try:
            from core.settings_manager import get_bool
            if get_bool("home_audio/enabled"):
                result["status"] = "configured"
                if get_bool("home_audio/ha_base_url"):
                    result["status"] = "active"
        except Exception:
            pass
        return result

    def diagnose_continue_on_server(self, host: str = "", port: int = 53318) -> dict[str, Any]:
        result: dict[str, Any] = {"status": "not_configured", "service": "continue_on_server"}
        if host:
            result["status"] = "unknown"
            import contextlib
            with contextlib.suppress(Exception):
                from integrations.michi_link.services.continue_on_server_service import ContinueOnServerService
                svc = ContinueOnServerService()
                res = svc.transfer_queue({"host": host, "port": port}, [], 0)
                if hasattr(res, "ok"):
                    result["status"] = "available" if res.ok else "unavailable"
        return result

    def _safe_diag(self, method_name: str) -> dict[str, Any]:
        if self._diag_svc is None:
            return {"status": "unknown"}
        try:
            method = getattr(self._diag_svc, method_name, None)
            if method is None:
                return {"status": "unknown"}
            return method()
        except Exception:
            return {"status": "error"}

    def _fallback_ecosystem(self) -> dict[str, Any]:
        return {
            "player": self.diagnose_player(),
            "mobile_sync": self.diagnose_mobile_sync(),
            "micro_server": self.diagnose_micro_server(),
            "home_audio": self.diagnose_home_audio(),
            "remote_music_servers": self.diagnose_remote_music_servers(),
        }
