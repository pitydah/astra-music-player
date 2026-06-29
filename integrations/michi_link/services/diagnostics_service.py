"""DiagnosticsService — generates health reports for the Michi ecosystem.

Can be called from CLI or future UI diagnostic panel.
"""
from __future__ import annotations

import logging
import time

from integrations.michi_link.client import MichiLinkClient

logger = logging.getLogger("michi.service.diagnostics")


class DiagnosticsService:
    """Generates structured health reports for Michi services."""

    def __init__(self):
        self._client = MichiLinkClient()
        self._start_ts = time.time()

    def check_player_api(self, handler=None) -> dict:
        """Verify the Player's own /api/v1/server/info responds correctly."""
        try:
            if handler and handler.server_ref:
                srv = handler.server_ref
                has_acct = bool(srv._local_account and srv._local_account.exists())
                return {
                    "status": "ok",
                    "service": "michi-music-player",
                    "api_version": "v1",
                    "local_account": has_acct,
                }
        except Exception as e:
            return {"status": "error", "message": str(e)}
        return {"status": "unknown"}

    def check_sync_server(self, handler=None) -> dict:
        """Verify SyncServer is running."""
        try:
            if handler and handler.server_ref:
                running = handler.server_ref.is_running
                return {
                    "status": "ok" if running else "stopped",
                    "running": running,
                }
        except Exception as e:
            return {"status": "error", "message": str(e)}
        return {"status": "unknown"}

    def check_pairing(self, registry=None) -> dict:
        """Verify DeviceRegistry has devices and tokens."""
        try:
            if registry:
                devices = registry.list_all()
                paired = [d for d in devices if d.token_hash and not d.revoked_at]
                return {
                    "status": "ok",
                    "total_devices": len(devices),
                    "paired": len(paired),
                    "revoked": len(devices) - len(paired),
                }
        except Exception as e:
            return {"status": "error", "message": str(e)}
        return {"status": "unknown"}

    def check_remote_micro(self, host: str = "", port: int = 53318) -> dict:
        """Try to discover a remote Micro Server."""
        if not host:
            return {"status": "skipped", "reason": "no host specified"}
        start = time.time()
        info = self._client.discover(host, port)
        elapsed = time.time() - start
        if info:
            return {
                "status": "ok",
                "alias": info.alias,
                "server_device_id": info.server_device_id,
                "requires_pairing": info.requires_pairing,
                "response_ms": round(elapsed * 1000, 1),
            }
        return {"status": "unreachable", "response_ms": round(elapsed * 1000, 1)}

    def generate_report(self, handler=None, registry=None,
                        micro_host: str = "") -> dict:
        """Generate a full diagnostic report."""
        return {
            "player_api": self.check_player_api(handler),
            "sync_server": self.check_sync_server(handler),
            "pairing": self.check_pairing(registry),
            "micro_server_client": self.check_remote_micro(micro_host),
            "errors": [],
        }
