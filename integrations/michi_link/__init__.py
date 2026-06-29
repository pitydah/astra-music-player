"""Michi Link API v1 — unified protocol for the Michi ecosystem.

Michi Music Player acts as both server (desktop_player, library_master, sync_host,
remote_control_target, cast_controller) and client (discover/pair with Micro Server,
discover Michi Music Stream).

This module provides:
  - MichiLinkServer: mounts /api/v1/ routes on the existing SyncServer
  - MichiLinkClient: discovers, pairs, and consumes remote services
  - Models and permissions for the v1 protocol
"""
from __future__ import annotations

from integrations.michi_link.server import MichiLinkServer
from integrations.michi_link.client import MichiLinkClient
from integrations.michi_link.models import (
    ServerInfo, PlaybackStateDto, QueueDto, TrackDto,
)
from integrations.michi_link.permissions import V1_PERMISSIONS

__all__ = [
    "MichiLinkServer",
    "MichiLinkClient",
    "ServerInfo",
    "PlaybackStateDto",
    "QueueDto",
    "TrackDto",
    "V1_PERMISSIONS",
]
