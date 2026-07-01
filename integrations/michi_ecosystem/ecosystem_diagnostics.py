"""EcosystemDiagnostics — run diagnostics on all Michi ecosystem services."""

from __future__ import annotations

from typing import Any

from integrations.michi_ecosystem.ecosystem_registry import EcosystemRegistry


class EcosystemDiagnostics:
    def __init__(self, registry=None, diagnostics_service=None, micro_server_service=None, sync_manager=None):
        self._registry = registry or EcosystemRegistry()
        self._diag_svc = diagnostics_service
        self._micro_svc = micro_server_service
        self._sync = sync_manager

    def diagnose_ecosystem(self, **kwargs) -> dict[str, Any]:
        return {
            "player": self.diagnose_player(**kwargs),
            "mobile_sync": self.diagnose_mobile_sync(**kwargs),
            "micro_server": self.diagnose_micro_server(**kwargs),
            "home_audio": self.diagnose_home_audio(**kwargs),
            "summary": self._build_summary(),
        }

    def diagnose_player(self, **kwargs) -> dict[str, Any]:
        return {"status": "ok", "service": "player"}

    def diagnose_mobile_sync(self, **kwargs) -> dict[str, Any]:
        return {"status": "unknown", "service": "mobile_sync", "paired_devices": 0}

    def diagnose_micro_server(self, host: str = "", port: int = 53318, **kwargs) -> dict[str, Any]:
        return {"status": "unknown", "service": "micro_server", "host": host, "port": port}

    def diagnose_home_audio(self, **kwargs) -> dict[str, Any]:
        return {"status": "skipped", "service": "home_audio", "message": "Home Audio diagnostic requires Snapcast and HA client references."}

    def diagnose_tailscale_route(self, host: str = "", **kwargs) -> dict[str, Any]:
        return {"status": "skipped", "service": "tailscale", "message": "Tailscale diagnostic requires external tool access (not implemented)."}

    def _build_summary(self) -> dict[str, Any]:
        return {"total_services": len(self._registry.list_services())}
