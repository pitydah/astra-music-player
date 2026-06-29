"""MicroServerService — manages Player ↔ Micro Server interactions.

Full lifecycle: discover, pair, read library, read stats.
Returns ServiceResult for every operation — never raises to caller.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from integrations.michi_link.client import MichiLinkClient, RemoteServerInfo

logger = logging.getLogger("michi.service.micro_server")


@dataclass
class ServiceResult:
    success: bool = False
    data: Any = None
    error_code: str = ""
    error_message: str = ""

    @classmethod
    def ok(cls, data: Any = None) -> ServiceResult:
        return cls(success=True, data=data)

    @classmethod
    def fail(cls, code: str = "UNKNOWN", message: str = "") -> ServiceResult:
        return cls(success=False, error_code=code, error_message=message)


class MicroServerService:
    """High-level service for interacting with a remote Michi Micro Server."""

    def __init__(self, client: MichiLinkClient | None = None):
        self._client = client or MichiLinkClient()
        self._servers: dict[str, RemoteServerInfo] = {}

    def discover(self, host: str, port: int = 53318) -> ServiceResult:
        info = self._client.discover(host, port)
        if info is None:
            return ServiceResult.fail("DISCOVERY_FAILED",
                                      f"Cannot reach server at {host}:{port}")
        key = f"{host}:{port}"
        self._servers[key] = info
        return ServiceResult.ok(info)

    def pair(self, server: RemoteServerInfo, username: str = "",
             password: str = "") -> ServiceResult:
        ok = self._client.pair(server, username=username, password=password)
        if not ok:
            return ServiceResult.fail("PAIR_FAILED",
                                      "Pairing rejected by server")
        return ServiceResult.ok({"device_id": server.device_id,
                                 "device_token": server.device_token[:8] + "..."})

    def get_tracks(self, server: RemoteServerInfo) -> ServiceResult:
        tracks = self._client.get_library(server)
        if tracks is None:
            return ServiceResult.fail("LIBRARY_FAILED",
                                      "Cannot fetch library from server")
        return ServiceResult.ok(tracks)

    def get_library_stats(self, server: RemoteServerInfo) -> ServiceResult:
        stats = self._client._get(server, "/api/v1/library/stats")
        if stats is None:
            return ServiceResult.fail("STATS_FAILED",
                                      "Cannot fetch library stats")
        return ServiceResult.ok(stats)

    def search(self, server: RemoteServerInfo, query: str) -> ServiceResult:
        results = self._client.search(server, query)
        if results is None:
            return ServiceResult.fail("SEARCH_FAILED",
                                      "Search request failed")
        return ServiceResult.ok(results)

    def get_playback_state(self, server: RemoteServerInfo) -> ServiceResult:
        state = self._client.get_playback_state(server)
        if state is None:
            return ServiceResult.fail("STATE_FAILED",
                                      "Cannot fetch playback state")
        return ServiceResult.ok(state)

    def get_queue(self, server: RemoteServerInfo) -> ServiceResult:
        queue = self._client.get_queue(server)
        if queue is None:
            return ServiceResult.fail("QUEUE_FAILED",
                                      "Cannot fetch queue")
        return ServiceResult.ok(queue)

    def control(self, server: RemoteServerInfo, command: str,
                **kwargs) -> ServiceResult:
        ok = self._client.control(server, command, **kwargs)
        if not ok:
            return ServiceResult.fail("CONTROL_FAILED",
                                      f"Command '{command}' failed")
        return ServiceResult.ok({"command": command})
