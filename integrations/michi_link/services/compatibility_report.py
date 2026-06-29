"""PlayerMicroCompatibilityReport — evaluates Player ↔ Micro Server contract alignment.

Tests each endpoint against expected contract format and returns structured results.
"""
from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request

from integrations.michi_link.client import MichiLinkClient, RemoteServerInfo

logger = logging.getLogger("michi.service.compatibility")

CONTRACT_OK = "CONTRACT_OK"
CONTRACT_PARTIAL = "CONTRACT_PARTIAL"
CONTRACT_MISMATCH = "CONTRACT_MISMATCH"
ENDPOINT_MISSING = "ENDPOINT_MISSING"
FALLBACK_AVAILABLE = "FALLBACK_AVAILABLE"


class PlayerMicroCompatibilityReport:
    """Analyzes contract compatibility between Player and a Micro Server."""

    def __init__(self):
        self._client = MichiLinkClient()

    def _get(self, url: str, headers: dict | None = None) -> tuple[int, dict | None]:
        try:
            req = urllib.request.Request(url, method="GET", headers=headers or {})
            with urllib.request.urlopen(req, timeout=5) as r:
                return r.status, json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            return e.code, None
        except Exception:
            return 0, None

    def _post(self, url: str, body: dict, headers: dict | None = None) -> tuple[int, dict | None]:
        try:
            data = json.dumps(body).encode()
            req = urllib.request.Request(
                url, data=data, method="POST",
                headers=headers or {"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=10) as r:
                return r.status, json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            return e.code, None
        except Exception:
            return 0, None

    def _discover(self, server: RemoteServerInfo) -> dict | None:
        info = self._client.discover(server.host, server.port)
        if info:
            return {"alias": info.alias, "features": info.features}
        return None

    def check_preflight(self, server: RemoteServerInfo) -> dict:
        status, data = self._post(
            f"http://{server.host}:{server.port}/api/v1/import/preflight",
            {"tracks": []},
        )
        if status == 404:
            return {"status": ENDPOINT_MISSING, "http_status": 404,
                    "fallback": "create_session without identities"}
        if status != 200 or not data:
            return {"status": CONTRACT_MISMATCH, "http_status": status}
        results = data.get("results", [])
        if isinstance(results, list):
            if results and "michi_track_id" in results[0]:
                return {"status": CONTRACT_OK, "format": "new"}
            if results and "local_track_id" in results[0]:
                return {"status": CONTRACT_OK, "format": "legacy"}
        return {"status": CONTRACT_PARTIAL, "format": "unknown"}

    def check_upload_mapping(self, server: RemoteServerInfo) -> dict:
        status, data = self._post(
            f"http://{server.host}:{server.port}/api/v1/import/track/upload",
            {"tracks": []},
        )
        if status == 404:
            return {"status": ENDPOINT_MISSING}
        if status != 200 or not data:
            return {"status": CONTRACT_MISMATCH, "http_status": status}
        if "server_track_id" in data:
            return {"status": CONTRACT_OK, "returns_mapping": True}
        if "remote_track_id" in data:
            return {"status": CONTRACT_PARTIAL, "returns_mapping": True,
                    "field_name": "remote_track_id (legacy)"}
        return {"status": CONTRACT_PARTIAL, "returns_mapping": False}

    def check_commit_mapping(self, server: RemoteServerInfo) -> dict:
        status, data = self._post(
            f"http://{server.host}:{server.port}/api/v1/import/session/commit",
            {"session_id": "test"},
        )
        if status == 404:
            return {"status": ENDPOINT_MISSING, "fallback": "local commit only"}
        if status != 200 or not data:
            return {"status": CONTRACT_MISMATCH, "http_status": status}
        mapping = data.get("mapping", [])
        if isinstance(mapping, list) and len(mapping) > 0:
            if "server_track_id" in mapping[0]:
                return {"status": CONTRACT_OK, "format": "new"}
            if "remote_track_id" in mapping[0]:
                return {"status": CONTRACT_PARTIAL, "format": "legacy"}
        return {"status": CONTRACT_PARTIAL, "mapping_count": len(mapping)}

    def check_queue_transfer(self, server: RemoteServerInfo) -> dict:
        status, data = self._post(
            f"http://{server.host}:{server.port}/api/v1/queue/transfer",
            {"track_ids": []},
        )
        if status == 404:
            return {"status": FALLBACK_AVAILABLE,
                    "fallback": "queue/items + jump + control"}
        if status == 200:
            return {"status": CONTRACT_OK}
        return {"status": CONTRACT_PARTIAL, "http_status": status}

    def check_remote_playback_confirmation(self, server: RemoteServerInfo) -> dict:
        status, data = self._get(
            f"http://{server.host}:{server.port}/api/v1/playback/state",
        )
        if status == 200 and data:
            if "state" in data:
                return {"status": CONTRACT_OK, "state_field": "state"}
            return {"status": CONTRACT_PARTIAL, "fields": list(data.keys())}
        return {"status": ENDPOINT_MISSING if status == 404 else CONTRACT_MISMATCH}

    def generate(self, server: RemoteServerInfo) -> dict:
        server_info = self._discover(server)
        return {
            "server_info": server_info or {"status": "unreachable"},
            "preflight": self.check_preflight(server),
            "upload_mapping": self.check_upload_mapping(server),
            "commit_mapping": self.check_commit_mapping(server),
            "queue_transfer": self.check_queue_transfer(server),
            "remote_playback_confirmation": self.check_remote_playback_confirmation(server),
        }
