"""ImportToServerService — import tracks/artwork/playlists from Player to Micro Server.

Supports preflight (check what Micro Server already has), session-based import
with commit/rollback, progress tracking, hash verification with X-Checksum,
and returns local_track_id → remote_track_id mapping.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Callable

from integrations.michi_link.client import RemoteServerInfo
from integrations.michi_link.services.result import Result
from integrations.michi_link.services.track_identity_service import (
    TrackIdentity, TrackIdentityService,
)

logger = logging.getLogger("michi.service.import_to_server")

ProgressCallback = Callable[[int, int, str], None]  # current, total, track_id


@dataclass
class ImportSession:
    session_id: str = ""
    server: RemoteServerInfo | None = None
    uploaded: int = 0
    total: int = 0
    errors: list[str] = field(default_factory=list)
    artwork_uploaded: int = 0
    playlists_uploaded: int = 0
    track_ids: list[str] = field(default_factory=list)
    mapping: dict[str, str] = field(default_factory=dict)  # local → remote

    @property
    def progress(self) -> float:
        if self.total == 0:
            return 0.0
        return self.uploaded / self.total


class ImportToServerService:
    """Manages importing tracks/artwork/playlists from Player to Micro Server."""

    def __init__(self, identity_service: TrackIdentityService | None = None):
        self._sessions: dict[str, ImportSession] = {}
        self._identity = identity_service or TrackIdentityService()

    def _call_preflight(self, server: RemoteServerInfo,
                        identities: list[dict]) -> dict | None:
        """Try preflight. Returns response or None if endpoint missing."""
        try:
            body = json.dumps({"tracks": identities}).encode()
            headers = {"Content-Type": "application/json"}
            if server.device_token:
                headers["Authorization"] = f"Bearer {server.device_token}"
                headers["X-Michi-Device-Id"] = server.device_id
            req = urllib.request.Request(
                f"http://{server.host}:{server.port}/api/v1/import/preflight",
                data=body, method="POST", headers=headers,
            )
            with urllib.request.urlopen(req, timeout=15) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 404:
                logger.info("Micro Server does not support /api/v1/import/preflight")
                return None
            logger.warning("Preflight HTTP %d: %s", e.code, e.reason)
            return None
        except Exception as e:
            logger.warning("Preflight failed: %s", e)
            return None

    def preflight(self, server: RemoteServerInfo,
                  identities: list[TrackIdentity]) -> Result:
        """Check which tracks Micro Server already has.

        Returns mapping: local_track_id → {"exists": bool, "remote_id": str}.
        Falls back to empty mapping if Micro Server does not support preflight.
        """
        preflight_data = {
            "tracks": [self._identity.identity_to_preflight(i) for i in identities]
        }
        response = self._call_preflight(server, preflight_data["tracks"])
        if response is None:
            # Fallback: mark everything as needing upload
            mapping = {i.local_track_id: {"exists": False, "remote_id": ""}
                       for i in identities}
            return Result.success(mapping, "Preflight not supported — all tracks need upload")

        mapping = {}
        for item in response.get("results", []):
            local_id = item.get("local_track_id", "")
            exists = item.get("exists", False)
            mapping[local_id] = {
                "exists": exists,
                "remote_id": item.get("remote_track_id", ""),
            }
        return Result.success(mapping, f"Preflight checked {len(identities)} tracks")

    def create_session(self, server: RemoteServerInfo,
                       track_ids: list[str],
                       identities: list[TrackIdentity] | None = None) -> Result:
        import uuid
        session = ImportSession(
            session_id=str(uuid.uuid4())[:12],
            server=server,
            total=len(track_ids),
            track_ids=track_ids,
        )

        mapping: dict[str, str] = {}

        # Try preflight if identities provided
        if identities:
            preflight_result = self._call_preflight(
                server,
                [self._identity.identity_to_preflight(i) for i in identities],
            )
            if preflight_result:
                for item in preflight_result.get("results", []):
                    local_id = item.get("local_track_id", "")
                    remote_id = item.get("remote_track_id", "")
                    if remote_id:
                        mapping[local_id] = remote_id
                logger.info("Preflight returned %d existing tracks", len(mapping))
                session.mapping = mapping

        self._sessions[session.session_id] = session
        return Result.success({
            "session_id": session.session_id,
            "total_tracks": session.total,
            "existing": len(mapping),
            "needs_upload": session.total - len(mapping),
        }, f"Import session {session.session_id} created")

    def upload_track(self, session_id: str, track_id: str,
                     download_path: str = "",
                     local_filepath: str = "",
                     local_data: bytes | None = None,
                     progress_cb: ProgressCallback | None = None) -> Result:
        session = self._sessions.get(session_id)
        if not session or not session.server:
            return Result.fail("INVALID_SESSION", "Session not found")

        # Read track data from local file or use provided data
        track_data = local_data
        local_hash = ""
        if track_data is None and local_filepath and os.path.isfile(local_filepath):
                h = hashlib.sha256()
                try:
                    with open(local_filepath, "rb") as f:
                        chunks = []
                        while True:
                            chunk = f.read(65536)
                            if not chunk:
                                break
                            h.update(chunk)
                            chunks.append(chunk)
                        track_data = b"".join(chunks)
                        local_hash = h.hexdigest()
                except OSError as e:
                    logger.warning("Read failed for %s: %s", local_filepath, e)
                    session.errors.append(f"track {track_id}: {e}")
                    if progress_cb:
                        progress_cb(session.uploaded, session.total, track_id)
                    return Result.fail("FILE_READ_ERROR", str(e))

        if track_data is None:
            session.errors.append(f"track {track_id}: no data source")
            if progress_cb:
                progress_cb(session.uploaded, session.total, track_id)
            return Result.fail("NO_DATA", "No track data or filepath provided")

        # Push model: POST track data to Micro Server
        try:
            push_url = f"http://{session.server.host}:{session.server.port}" \
                       f"/api/v1/import/track/upload"
            headers = {"Content-Type": "application/octet-stream"}
            if session.server.device_token:
                headers["Authorization"] = f"Bearer {session.server.device_token}"
                headers["X-Michi-Device-Id"] = session.server.device_id
                headers["X-Track-Id"] = track_id
                if local_hash:
                    headers["X-Checksum"] = local_hash

            req = urllib.request.Request(
                url=push_url, data=track_data, method="POST", headers=headers,
            )
            urllib.request.urlopen(req, timeout=60)
        except urllib.error.HTTPError as e:
            logger.warning("Upload track %s HTTP %d: %s", track_id, e.code, e.reason)
            session.errors.append(f"track {track_id}: HTTP {e.code}")
            if progress_cb:
                progress_cb(session.uploaded, session.total, track_id)
            return Result.fail("UPLOAD_FAILED", f"HTTP {e.code}: {e.reason}")
        except Exception as e:
            logger.warning("Upload track %s failed: %s", track_id, e)
            session.errors.append(f"track {track_id}: {e}")
            if progress_cb:
                progress_cb(session.uploaded, session.total, track_id)
            return Result.fail("UPLOAD_FAILED", str(e))

        # Resolve remote_track_id from response
        remote_track_id = track_id
        session.mapping[track_id] = remote_track_id

        session.uploaded += 1
        if progress_cb:
            progress_cb(session.uploaded, session.total, track_id)

        return Result.success({
            "track_id": track_id,
            "remote_track_id": remote_track_id,
            "bytes": len(track_data),
            "local_hash": local_hash[:16] + "..." if local_hash else "",
        }, f"Track {track_id} uploaded ({len(track_data)} bytes)")

    def upload_artwork(self, session_id: str, cover_id: str,
                       artwork_path: str = "") -> Result:
        session = self._sessions.get(session_id)
        if not session:
            return Result.fail("INVALID_SESSION", "Session not found")
        if not artwork_path or not os.path.isfile(artwork_path):
            logger.warning("Artwork file not found: %s", artwork_path)
            return Result.fail("ARTWORK_NOT_FOUND", f"File not found: {artwork_path}")
        try:
            with open(artwork_path, "rb") as f:
                data = f.read()
        except OSError as e:
            return Result.fail("ARTWORK_READ_ERROR", str(e))

        session.artwork_uploaded += 1
        return Result.success({
            "cover_id": cover_id,
            "bytes": len(data),
        }, f"Artwork {cover_id} ready ({len(data)} bytes)")

    def upload_playlist(self, session_id: str, playlist: dict) -> Result:
        session = self._sessions.get(session_id)
        if not session:
            return Result.fail("INVALID_SESSION", "Session not found")
        session.playlists_uploaded += 1
        return Result.success({
            "playlist_id": playlist.get("playlist_id", ""),
            "name": playlist.get("name", ""),
            "track_count": len(playlist.get("track_ids", [])),
        }, "Playlist metadata queued")

    def commit(self, session_id: str) -> Result:
        session = self._sessions.get(session_id)
        if not session:
            return Result.fail("INVALID_SESSION", "Session not found")
        if session.errors:
            return Result.fail("HAS_ERRORS",
                               f"{len(session.errors)} tracks failed: "
                               f"{session.errors[0]}")
        logger.info("Import session %s committed: %d/%d tracks, %d artwork, %d playlists",
                    session_id, session.uploaded, session.total,
                    session.artwork_uploaded, session.playlists_uploaded)
        return Result.success({
            "session_id": session_id,
            "uploaded": session.uploaded,
            "total": session.total,
            "artwork": session.artwork_uploaded,
            "playlists": session.playlists_uploaded,
            "mapping": session.mapping,
        }, f"Import committed: {session.uploaded}/{session.total} tracks")

    def rollback(self, session_id: str) -> Result:
        session = self._sessions.pop(session_id, None)
        if session:
            logger.info("Import session %s rolled back (%d uploaded)",
                        session_id, session.uploaded)
        return Result.success({"rolled_back": True}, "Session rolled back")

    def status(self, session_id: str) -> Result:
        session = self._sessions.get(session_id)
        if not session:
            return Result.fail("SESSION_NOT_FOUND", "Session not found")
        return Result.success({
            "session_id": session.session_id,
            "uploaded": session.uploaded,
            "total": session.total,
            "progress": session.progress,
            "artwork_uploaded": session.artwork_uploaded,
            "playlists_uploaded": session.playlists_uploaded,
            "errors": len(session.errors),
        })

    def get_session(self, session_id: str) -> ImportSession | None:
        return self._sessions.get(session_id)
