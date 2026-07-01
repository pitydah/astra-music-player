"""SectionContextProvider — abstract base for per-section context providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class SectionContextProvider(ABC):
    section_key: str = ""

    @abstractmethod
    def get_context(self) -> dict[str, Any]:
        ...

    @abstractmethod
    def get_suggestions(self) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    def get_allowed_actions(self) -> list[str]:
        ...
