"""Michi Link API v1 — client for discovering and consuming remote services.

The desktop player acts as client when connecting to:
  - Michi Micro Server (lightweight headless server)
  - Michi Music Stream (audio output device)
  - Michi Big Server (future)
"""
from __future__ import annotations

import json
import logging
import urllib.request
from dataclasses import dataclass, field

logger = logging.getLogger("michi.link.client")


@dataclass
class RemoteServerInfo:
    host: str = ""
    port: int = 53318
    alias: str = ""
    server_device_id: str = ""
    requires_pairing: bool = False
    auth_methods: list[str] = field(default_factory=list)
    roles: list[str] = field(default_factory=list)
    features: dict[str, bool] = field(default_factory=dict)
    device_token: str = ""
    device_id: str = ""


class MichiLinkClient:
    """Discovers, pairs, and consumes remote Michi services via HTTP."""

    def __init__(self):
        self._servers: dict[str, RemoteServerInfo] = {}  # host:port → info

    def discover(self, host: str, port: int = 53318) -> RemoteServerInfo | None:
        """Discover a Michi service at host:port by querying /api/v1/server/info."""
        try:
            req = urllib.request.Request(
                f"http://{host}:{port}/api/v1/server/info", method="GET",
            )
            with urllib.request.urlopen(req, timeout=5) as r:
                data = json.loads(r.read().decode())
        except Exception as e:
            logger.debug("Discovery failed for %s:%d: %s", host, port, e)
            return None

        info = RemoteServerInfo(
            host=host, port=port,
            alias=data.get("name", ""),
            server_device_id=data.get("server_device_id", ""),
            requires_pairing=data.get("requires_pairing", False),
            auth_methods=data.get("auth_methods", []),
            roles=data.get("roles", []),
            features=data.get("features", {}),
        )
        key = f"{host}:{port}"
        self._servers[key] = info
        return info

    def pair(self, server: RemoteServerInfo, username: str = "",
             password: str = "", device_id: str = "") -> bool:
        """Pair with a remote Michi service."""
        import secrets as _secrets
        client_id = device_id or f"desktop_{_secrets.token_hex(4)}"
        body = json.dumps({
            "client_device_id": client_id,
            "username": username,
            "password": password,
            "alias": "Michi Music Player",
            "device_model": "desktop",
            "client_version": "1.0",
        }).encode()
        try:
            req = urllib.request.Request(
                f"http://{server.host}:{server.port}/api/v1/pair/confirm",
                data=body, method="POST",
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=10) as r:
                resp = json.loads(r.read().decode())
        except Exception as e:
            logger.warning("Pairing failed with %s:%d: %s",
                           server.host, server.port, e)
            return False

        if resp.get("success"):
            server.device_token = resp.get("device_token", "")
            server.device_id = resp.get("device_id", client_id)
            key = f"{server.host}:{server.port}"
            self._servers[key] = server
            return True
        logger.warning("Pairing rejected by %s:%d: %s",
                       server.host, server.port, resp.get("error", ""))
        return False

    def _get(self, server: RemoteServerInfo, path: str) -> dict | None:
        try:
            headers = {"Content-Type": "application/json"}
            if server.device_token:
                headers["Authorization"] = f"Bearer {server.device_token}"
                headers["X-Michi-Device-Id"] = server.device_id
            req = urllib.request.Request(
                f"http://{server.host}:{server.port}{path}",
                method="GET", headers=headers,
            )
            with urllib.request.urlopen(req, timeout=10) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            logger.debug("GET %s failed: %s", path, e)
            return None

    def get_library(self, server: RemoteServerInfo) -> list[dict] | None:
        data = self._get(server, "/api/v1/tracks")
        if data:
            return data.get("tracks", [])
        return None

    def search(self, server: RemoteServerInfo, query: str) -> list[dict] | None:
        from urllib.parse import quote
        data = self._get(server, f"/api/v1/search?q={quote(query)}")
        if data:
            return data.get("results", [])
        return None

    def get_playback_state(self, server: RemoteServerInfo) -> dict | None:
        return self._get(server, "/api/v1/playback/state")

    def get_queue(self, server: RemoteServerInfo) -> dict | None:
        return self._get(server, "/api/v1/queue")

    def control(self, server: RemoteServerInfo, action: str, **kwargs) -> bool:
        body = json.dumps({"action": action, **kwargs}).encode()
        try:
            headers = {"Content-Type": "application/json"}
            if server.device_token:
                headers["Authorization"] = f"Bearer {server.device_token}"
                headers["X-Michi-Device-Id"] = server.device_id
            req = urllib.request.Request(
                f"http://{server.host}:{server.port}/api/v1/playback/control",
                data=body, method="POST", headers=headers,
            )
            with urllib.request.urlopen(req, timeout=10) as r:
                return r.status == 200
        except Exception as e:
            logger.warning("Control action '%s' failed: %s", action, e)
            return False
