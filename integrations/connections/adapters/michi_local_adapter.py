"""Michi Local adapter — local API connection stub."""

from __future__ import annotations

import logging

from integrations.connections.adapters.base_adapter import BaseServerAdapter

logger = logging.getLogger("michi.connections.local")


class MichiLocalAdapter(BaseServerAdapter):
    def __init__(self, host: str = "127.0.0.1", port: int = 8124,
                 token: str = ""):
        super().__init__(host, port, "", "", False)
        self._token = token

    def ping(self) -> bool:
        return True

    def get_capabilities(self) -> list[str]:
        return ["local_playback", "library_access", "metadata"]

    def get_library_summary(self) -> dict:
        return {"artists": 0, "albums": 0, "tracks": 0, "local": True}
