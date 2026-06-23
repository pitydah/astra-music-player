"""Home Assistant adapter — Bearer token authentication."""

from __future__ import annotations

import json
import urllib.request
import urllib.error
import logging

from integrations.connections.adapters.base_adapter import BaseServerAdapter

logger = logging.getLogger("michi.connections.ha")


class HomeAssistantAdapter(BaseServerAdapter):
    def __init__(self, host: str, port: int = 8123, token: str = "",
                 ssl: bool = False):
        super().__init__(host, port, "", "", ssl)
        self._token = token

    def _get(self, endpoint: str) -> dict:
        url = f"{self.base_url}/api/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }
        try:
            req = urllib.request.Request(url, method="GET", headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            logger.debug("HA API error: %s", e)
            return {}

    def ping(self) -> bool:
        result = self._get("")
        return bool(result.get("message"))

    def get_capabilities(self) -> list[str]:
        caps = ["home_assistant", "media_player"]
        result = self._get("states")
        if result:
            entities = [e for e in result if e.get("entity_id", "").startswith("media_player.")]
            if entities:
                caps.append("media_players")
        return caps

    def get_library_summary(self) -> dict:
        result = self._get("states")
        devices = 0
        if result:
            devices = len([e for e in result if e.get("entity_id", "").startswith("media_player.")])
        return {"artists": 0, "albums": 0, "tracks": 0, "media_players": devices}
