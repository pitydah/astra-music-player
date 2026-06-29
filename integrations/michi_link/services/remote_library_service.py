"""RemoteLibraryService — reads library from Micro Server as browsable source.

Future: provides tracks/search from a remote Micro Server so the Player can
display them alongside the local library. This is a stub ready for Phase 3.
"""
from __future__ import annotations

import logging

from integrations.michi_link.client import RemoteServerInfo
from integrations.michi_link.services.micro_server_service import (
    MicroServerService, ServiceResult,
)

logger = logging.getLogger("michi.service.remote_library")


class RemoteLibraryService:
    """Read-only access to a remote Micro Server library."""

    def __init__(self, micro_service: MicroServerService | None = None):
        self._micro = micro_service or MicroServerService()

    def get_tracks(self, server: RemoteServerInfo) -> ServiceResult:
        return self._micro.get_tracks(server)

    def search(self, server: RemoteServerInfo, query: str) -> ServiceResult:
        return self._micro.search(server, query)

    def get_track_count(self, server: RemoteServerInfo) -> int:
        result = self._micro.get_library_stats(server)
        if result.success and isinstance(result.data, dict):
            return result.data.get("audio", 0)
        return 0
