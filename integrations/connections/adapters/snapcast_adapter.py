"""Snapcast adapter — Snapcast JSON-RPC protocol."""

from __future__ import annotations

import json
import urllib.request
import urllib.error
import logging

from integrations.connections.adapters.base_adapter import BaseServerAdapter

logger = logging.getLogger("michi.connections.snapcast")


class SnapcastAdapter(BaseServerAdapter):
    def __init__(self, host: str, port: int = 1705,
                 ssl: bool = False):
        super().__init__(host, port, "", "", ssl)

    def _rpc(self, method: str, params: dict | None = None) -> dict:
        url = f"{self.base_url}/jsonrpc"
        payload = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
        }
        req = urllib.request.Request(
            url, data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            logger.debug("Snapcast RPC error: %s", e)
            return {}

    def ping(self) -> bool:
        result = self._rpc("Server.GetStatus")
        return "result" in result

    def get_capabilities(self) -> list[str]:
        caps = ["snapcast", "multiroom"]
        result = self._rpc("Server.GetStatus")
        server = result.get("result", {}).get("server", {})
        groups = server.get("groups", [])
        clients = sum(len(g.get("clients", [])) for g in groups)
        if clients > 0:
            caps.append("clients")
        return caps

    def get_library_summary(self) -> dict:
        result = self._rpc("Server.GetStatus")
        server = result.get("result", {}).get("server", {})
        groups = server.get("groups", [])
        clients = sum(len(g.get("clients", [])) for g in groups)
        return {"artists": 0, "albums": 0, "tracks": 0, "groups": len(groups), "clients": clients}
