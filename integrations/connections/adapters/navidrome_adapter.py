"""Navidrome adapter — Subsonic/OpenSubsonic API over HTTP."""

from __future__ import annotations

import hashlib
import json
import urllib.request
import urllib.error
import logging

from integrations.connections.adapters.base_adapter import BaseServerAdapter

logger = logging.getLogger("michi.connections.navidrome")


class NavidromeAdapter(BaseServerAdapter):
    def __init__(self, host: str, port: int = 4533, username: str = "",
                 password: str = "", ssl: bool = False):
        super().__init__(host, port, username, password, ssl)

    def _params(self, extra: str = "") -> str:
        import random
        import string
        salt = "".join(random.choices(string.ascii_letters + string.digits, k=12))
        token = hashlib.md5((self._password + salt).encode()).hexdigest()
        base = (f"u={urllib.request.quote(self._username)}"
                f"&t={token}&s={salt}&v=1.16.1&c=michi&f=json")
        if extra:
            base += f"&{extra}"
        return base

    def _get(self, endpoint: str, params: str = "") -> dict:
        url = f"{self.base_url}/rest/{endpoint}"
        if params:
            url += f"?{params}"
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            logger.debug("Navidrome API error: %s", e)
            return {}

    def ping(self) -> bool:
        result = self._get("ping", self._params())
        return result.get("subsonic-response", {}).get("status") == "ok"

    def get_capabilities(self) -> list[str]:
        caps = ["streaming", "search", "artists", "albums"]
        result = self._get("ping", self._params())
        resp = result.get("subsonic-response", {})
        if resp.get("status") == "ok":
            caps.append("cover_art")
        return caps

    def get_library_summary(self) -> dict:
        result = self._get("getIndexes", self._params())
        resp = result.get("subsonic-response", {}).get("indexes", {})
        artists = len(resp.get("index", [])) * 10 if resp.get("index") else 0
        return {"artists": artists, "albums": 0, "tracks": 0}

    def get_stream_url(self, item_id: str) -> str:
        params = self._params(f"id={item_id}")
        return f"{self.base_url}/rest/stream?{params}"
