"""ImportToServerService — import tracks/playlists from Player to Micro Server.

Phase 3: Player sends selected tracks or playlists to a paired Micro Server.
Supports session-based import with commit or rollback.
"""
from __future__ import annotations

import logging
import urllib.request
from dataclasses import dataclass

from integrations.michi_link.client import RemoteServerInfo
from integrations.michi_link.services.micro_server_service import ServiceResult

logger = logging.getLogger("michi.service.import_to_server")


@dataclass
class ImportSession:
    session_id: str = ""
    server: RemoteServerInfo | None = None
    uploaded: int = 0
    total: int = 0
    errors: list[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class ImportToServerService:
    """Manages importing tracks from the Player library to a Micro Server."""

    def __init__(self):
        self._sessions: dict[str, ImportSession] = {}

    def create_session(self, server: RemoteServerInfo,
                       track_ids: list[str]) -> ServiceResult:
        import uuid
        session = ImportSession(
            session_id=str(uuid.uuid4())[:12],
            server=server,
            total=len(track_ids),
        )
        self._sessions[session.session_id] = session
        return ServiceResult.ok({
            "session_id": session.session_id,
            "total_tracks": session.total,
        })

    def upload_track(self, session_id: str, track_id: str,
                     download_path: str) -> ServiceResult:
        session = self._sessions.get(session_id)
        if not session or not session.server:
            return ServiceResult.fail("INVALID_SESSION", "Session not found")

        try:
            # Stream from the remote source: Micro Server downloads from Player
            stream_url = f"http://{session.server.host}:{session.server.port}{download_path}"
            headers = {"Content-Type": "application/json"}
            if session.server.device_token:
                headers["Authorization"] = f"Bearer {session.server.device_token}"
                headers["X-Michi-Device-Id"] = session.server.device_id

            req = urllib.request.Request(
                url=stream_url, method="GET", headers=headers,
            )
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
        except Exception as e:
            logger.warning("Upload track %s failed: %s", track_id, e)
            session.errors.append(f"track {track_id}: {e}")
            return ServiceResult.fail("UPLOAD_FAILED", str(e))

        session.uploaded += 1
        return ServiceResult.ok({"track_id": track_id, "bytes": len(data)})

    def commit_session(self, session_id: str) -> ServiceResult:
        session = self._sessions.get(session_id)
        if not session:
            return ServiceResult.fail("INVALID_SESSION", "Session not found")
        if session.errors:
            return ServiceResult.fail("HAS_ERRORS",
                                      f"{len(session.errors)} tracks failed")
        logger.info("Import session %s committed: %d/%d tracks",
                    session_id, session.uploaded, session.total)
        return ServiceResult.ok({
            "session_id": session_id,
            "uploaded": session.uploaded,
            "total": session.total,
        })

    def rollback_session(self, session_id: str) -> ServiceResult:
        session = self._sessions.pop(session_id, None)
        if session:
            logger.info("Import session %s rolled back (%d uploaded)",
                        session_id, session.uploaded)
        return ServiceResult.ok({"rolled_back": True})

    def get_session(self, session_id: str) -> ImportSession | None:
        return self._sessions.get(session_id)
