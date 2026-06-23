"""Consent manager — gates all online access for the Knowledge Broker."""

from __future__ import annotations

import logging
import os
from typing import Any

from core.settings_manager import (
    get_bool, get_int, get_str,
)
from integrations.knowledge_broker.schemas import ConsentState

logger = logging.getLogger("michi.knowledge_broker.consent")


class ConsentManager:
    def __init__(self):
        self._safe_mode = os.environ.get("MICHI_SAFE_MODE") == "1"
        self._enabled: bool = self._read_bool("knowledge_broker/enabled", False)
        self._offline_strict: bool = self._read_bool("knowledge_broker/offline_strict", True)
        self._cache_only: bool = self._read_bool("knowledge_broker/cache_only", True)
        self._allow_mb: bool = self._read_bool("knowledge_broker/allow_musicbrainz", False)
        self._allow_ca: bool = self._read_bool("knowledge_broker/allow_coverart", False)
        self._allow_wd: bool = self._read_bool("knowledge_broker/allow_wikidata", False)
        self._allow_wp: bool = self._read_bool("knowledge_broker/allow_wikipedia", False)

        if self._safe_mode:
            self._enabled = False
            self._offline_strict = True
            self._cache_only = True
        self._auto_refresh: bool = self._read_bool("knowledge_broker/auto_refresh", False)
        self._refresh_days: int = get_int("knowledge_broker/refresh_interval_days") or 30
        self._wiki_lang: str = get_str("knowledge_broker/wiki_language") or "es"

    @staticmethod
    def _read_bool(key: str, default: bool) -> bool:
        val = get_bool(key)
        return default if val is None else val

    def can_query_online(self) -> ConsentState:
        if not self._enabled:
            return ConsentState.DENIED
        if self._offline_strict:
            return ConsentState.OFFLINE_STRICT
        return ConsentState.ALLOWED

    def can_use_musicbrainz(self) -> ConsentState:
        base = self.can_query_online()
        if base != ConsentState.ALLOWED:
            return base
        if self._cache_only:
            return ConsentState.CACHE_ONLY
        if not self._allow_mb:
            return ConsentState.SOURCE_DISABLED
        return ConsentState.ALLOWED

    def can_use_coverart(self) -> ConsentState:
        base = self.can_query_online()
        if base != ConsentState.ALLOWED:
            return base
        if self._cache_only:
            return ConsentState.CACHE_ONLY
        if not self._allow_ca:
            return ConsentState.SOURCE_DISABLED
        return ConsentState.ALLOWED

    def can_use_wikidata(self) -> ConsentState:
        base = self.can_query_online()
        if base != ConsentState.ALLOWED:
            return base
        if self._cache_only:
            return ConsentState.CACHE_ONLY
        if not self._allow_wd:
            return ConsentState.SOURCE_DISABLED
        return ConsentState.ALLOWED

    def can_use_wikipedia(self) -> ConsentState:
        base = self.can_query_online()
        if base != ConsentState.ALLOWED:
            return base
        if self._cache_only:
            return ConsentState.CACHE_ONLY
        if not self._allow_wp:
            return ConsentState.SOURCE_DISABLED
        return ConsentState.ALLOWED

    def state_summary(self) -> dict[str, Any]:
        return {
            "enabled": self._enabled,
            "offline_strict": self._offline_strict,
            "cache_only": self._cache_only,
            "musicbrainz": self._allow_mb,
            "coverart": self._allow_ca,
            "wikidata": self._allow_wd,
            "wikipedia": self._allow_wp,
        }

    @property
    def auto_refresh(self) -> bool:
        return self._auto_refresh

    @property
    def refresh_interval_days(self) -> int:
        return self._refresh_days

    @property
    def wiki_language(self) -> str:
        return self._wiki_lang
