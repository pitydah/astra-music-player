"""Michi import client — import tracks/playlists from a remote Micro Server.

Phase 3: Player imports tracks/playlists from a remote Micro Server into
the local library. This is a stub for Phase 3.
"""
from __future__ import annotations

import logging

from integrations.michi_link.client import RemoteServerInfo

logger = logging.getLogger("michi.link.import_client")


class ImportClient:
    """Client for importing tracks and playlists from a remote server.

    Usage (Phase 3):
        client = ImportClient(server_info)
        tracks = client.fetch_tracks()
        playlists = client.fetch_playlists()
        client.import_to_local(tracks)
    """
    def __init__(self, server: RemoteServerInfo | None = None):
        self._server = server

    def fetch_tracks(self) -> list[dict]:
        logger.info("fetch_tracks stub — not yet implemented")
        return []

    def fetch_playlists(self) -> list[dict]:
        logger.info("fetch_playlists stub — not yet implemented")
        return []

    def import_to_local(self, tracks: list[dict]) -> int:
        logger.info("import_to_local stub — not yet implemented")
        return 0
