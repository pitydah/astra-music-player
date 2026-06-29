"""ContinueOnServerService — handoff playback from Player to Micro Server.

Phase 3: Player sends its current queue to a paired Micro Server and optionally
instructs it to start playing. The Micro Server streams tracks from the Player.
"""
from __future__ import annotations

import json
import logging
import urllib.request

from integrations.michi_link.client import RemoteServerInfo
from integrations.michi_link.services.micro_server_service import ServiceResult

logger = logging.getLogger("michi.service.continue_on_server")


class ContinueOnServerService:
    """Service for handing off playback queue to a remote Micro Server."""

    def __init__(self):
        pass

    def transfer_queue(self, server: RemoteServerInfo, track_ids: list[str],
                       position_ms: float = 0.0) -> ServiceResult:
        """Send queue to Micro Server for continued playback."""
        body = json.dumps({
            "track_ids": track_ids,
            "position_ms": position_ms,
            "source": "michi-music-player",
        }).encode()
        try:
            headers = {"Content-Type": "application/json"}
            if server.device_token:
                headers["Authorization"] = f"Bearer {server.device_token}"
                headers["X-Michi-Device-Id"] = server.device_id
            req = urllib.request.Request(
                f"http://{server.host}:{server.port}/api/v1/queue/transfer",
                data=body, method="POST", headers=headers,
            )
            with urllib.request.urlopen(req, timeout=15) as r:
                resp = json.loads(r.read().decode())
        except Exception as e:
            logger.warning("Queue transfer failed: %s", e)
            return ServiceResult.fail("TRANSFER_FAILED", str(e))
        return ServiceResult.ok(resp)

    def start_remote_playback(self, server: RemoteServerInfo) -> ServiceResult:
        """Tell the Micro Server to start playing."""
        try:
            headers = {"Content-Type": "application/json"}
            if server.device_token:
                headers["Authorization"] = f"Bearer {server.device_token}"
                headers["X-Michi-Device-Id"] = server.device_id
            req = urllib.request.Request(
                f"http://{server.host}:{server.port}/api/v1/playback/control",
                data=json.dumps({"command": "play"}).encode(),
                method="POST", headers=headers,
            )
            with urllib.request.urlopen(req, timeout=10) as r:
                ok = r.status == 200
        except Exception as e:
            logger.warning("Remote playback start failed: %s", e)
            return ServiceResult.fail("REMOTE_PLAY_FAILED", str(e))
        return ServiceResult.ok({"playing": ok})

    def stop_remote_playback(self, server: RemoteServerInfo) -> ServiceResult:
        """Tell the Micro Server to stop playing."""
        try:
            headers = {"Content-Type": "application/json"}
            if server.device_token:
                headers["Authorization"] = f"Bearer {server.device_token}"
                headers["X-Michi-Device-Id"] = server.device_id
            req = urllib.request.Request(
                f"http://{server.host}:{server.port}/api/v1/playback/control",
                data=json.dumps({"command": "stop"}).encode(),
                method="POST", headers=headers,
            )
            with urllib.request.urlopen(req, timeout=10) as r:
                ok = r.status == 200
        except Exception as e:
            logger.warning("Remote playback stop failed: %s", e)
            return ServiceResult.fail("REMOTE_STOP_FAILED", str(e))
        return ServiceResult.ok({"stopped": ok})
