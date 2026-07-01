"""SectionContextRegistry — register and dispatch section context providers."""

from __future__ import annotations

from typing import Any

from core.context.section_context_provider import SectionContextProvider


class SectionContextRegistry:
    def __init__(self):
        self._providers: dict[str, SectionContextProvider] = {}

    def register(self, provider: SectionContextProvider) -> None:
        self._providers[provider.section_key] = provider

    def get_provider(self, section_key: str) -> SectionContextProvider | None:
        return self._providers.get(section_key)

    def get_context(self, section_key: str) -> dict[str, Any]:
        provider = self.get_provider(section_key)
        if provider is None:
            return {"section": section_key, "allowed_actions": []}
        return provider.get_context()

    def get_suggestions(self, section_key: str) -> list[dict[str, Any]]:
        provider = self.get_provider(section_key)
        if provider is None:
            return []
        return provider.get_suggestions()

    def get_allowed_actions(self, section_key: str) -> list[str]:
        provider = self.get_provider(section_key)
        if provider is None:
            return []
        return provider.get_allowed_actions()

    def list_registered(self) -> list[str]:
        return list(self._providers.keys())
