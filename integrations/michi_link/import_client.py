"""Michi import client — future import from Micro Server.

Phase 3: Player imports tracks/playlists from a remote Micro Server into
the local library. This is a stub for future implementation.
"""
from __future__ import annotations

import logging

logger = logging.getLogger("michi.link.import_client")


class ImportClient:
    """Client for importing tracks and playlists from a remote server.

    Usage (future):
        client = ImportClient(remote_server)
        tracks = client.fetch_tracks()
        playlists = client.fetch_playlists()
        client.import_to_local(tracks)
    """
    def __init__(self):
        pass
