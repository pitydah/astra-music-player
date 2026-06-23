"""Jellyfin adapter — Jellyfin REST API."""

from __future__ import annotations

import json
import urllib.request
import urllib.error
import logging

from integrations.connections.adapters.base_adapter import BaseServerAdapter

logger = logging.getLogger("michi.connections.jellyfin")


class JellyfinAdapter(BaseServerAdapter):
    def __init__(self, host: str, port: int = 8096, username: str = "",
                 password: str = "", ssl: bool = False,
                 api_key: str = ""):
        super().__init__(host, port, username, password, ssl)
        self._api_key = api_key

    def _get(self, endpoint: str) -> dict:
        url = f"{self.base_url}{endpoint}"
        headers = {}
        if self._api_key:
            headers["X-Emby-Token"] = self._api_key
        try:
            req = urllib.request.Request(url, method="GET", headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            logger.debug("Jellyfin API error: %s", e)
            return {}

    def ping(self) -> bool:
        result = self._get("/System/Info/Public")
        return bool(result.get("ServerName"))

    def get_capabilities(self) -> list[str]:
        caps = ["streaming", "search", "artists", "albums"]
        result = self._get("/System/Info/Public")
        if result.get("ServerName"):
            caps.append("cover_art")
        return caps

    def get_library_summary(self) -> dict:
        result = self._get("/Items/Counts")
        return {
            "artists": result.get("ArtistCount", 0),
            "albums": result.get("AlbumCount", 0),
            "tracks": result.get("SongCount", 0),
        }

    def get_stream_url(self, item_id: str) -> str:
        suffix = f"?api_key={self._api_key}" if self._api_key else ""
        return f"{self.base_url}/Audio/{item_id}/stream{suffix}"
