"""Base server adapter — abstract interface for music server connections."""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseServerAdapter(ABC):
    def __init__(self, host: str, port: int, username: str = "",
                 password: str = "", ssl: bool = False):
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._ssl = ssl

    @property
    def base_url(self) -> str:
        protocol = "https" if self._ssl else "http"
        return f"{protocol}://{self._host}:{self._port}"

    @abstractmethod
    def ping(self) -> bool:
        ...

    @abstractmethod
    def get_capabilities(self) -> list[str]:
        ...

    def get_library_summary(self) -> dict:
        return {"artists": 0, "albums": 0, "tracks": 0}

    def get_stream_url(self, item_id: str) -> str:
        return ""
