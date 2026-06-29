"""ContextService — public facade for the context system.

Controllers and UI use this service, not repository or snapshot builders directly.
"""

from __future__ import annotations

import logging

from core.context import context_repository as repo
from core.context.context_events import AppEvent
from core.context.context_invalidator import invalidate_for_event, clear_dirty, is_dirty
from core.context.context_snapshot import (
    build_assistant_snapshot,
    build_home_snapshot,
    build_library_health_snapshot,
    build_mix_snapshot,
    build_playback_snapshot,
)

logger = logging.getLogger("michi.context_service")

_SNAPSHOT_TTL = 120  # seconds


class ContextService:
    def __init__(self, db=None, playback=None, sync=None):
        self._db = db
        self._playback = playback
        self._sync = sync
        self._current_section = ""
        self._current_tab = ""

    def record_event(self, event_type: str, payload: dict | None = None) -> None:
        repo.record_event(event_type, payload)
        invalidate_for_event(event_type)

    def update_navigation(self, section: str, tab: str = "",
                          extra: dict | None = None) -> None:
        self._current_section = section
        self._current_tab = tab
        repo.set_state("navigation", {
            "section": section,
            "tab": tab,
            **(extra or {}),
        })
        self.record_event(AppEvent.SECTION_CHANGED, {"section": section, "tab": tab})

    def update_selection(self, track=None, album: str = "",
                         artist: str = "") -> None:
        payload = {"album": album, "artist": artist}
        if track is not None:
            payload["track"] = getattr(track, "title", None) or getattr(track, "name", None)
            payload["track_artist"] = getattr(track, "artist", None)
        repo.set_state("selection", payload)
        self.record_event(AppEvent.TRACK_SELECTED, payload)

    def record_track_played(self, track=None) -> None:
        payload = {}
        if track is not None:
            payload["title"] = getattr(track, "title", None) or getattr(track, "name", None)
            payload["artist"] = getattr(track, "artist", None)
            payload["album"] = getattr(track, "album", None)
        self.record_event(AppEvent.TRACK_PLAYED, payload)

    def get_library_health(self) -> dict:
        if is_dirty("library_health") or repo.get_summary("library_health") is None:
            snapshot = build_library_health_snapshot(self._db)
            repo.set_summary("library_health", snapshot, ttl_seconds=_SNAPSHOT_TTL)
            clear_dirty("library_health")
        return repo.get_summary("library_health") or {}

    def get_home_snapshot(self) -> dict:
        if is_dirty("home_snapshot") or repo.get_summary("home_snapshot") is None:
            snapshot = build_home_snapshot(self._db, self._playback, self._sync)
            repo.set_summary("home_snapshot", snapshot, ttl_seconds=_SNAPSHOT_TTL)
            clear_dirty("home_snapshot")
        return repo.get_summary("home_snapshot") or {}

    def get_assistant_snapshot(self) -> dict:
        if is_dirty("assistant_snapshot") or repo.get_summary("assistant_snapshot") is None:
            events = repo.recent_events(limit=10)
            snapshot = build_assistant_snapshot(
                self._db, self._playback,
                current_section=self._current_section,
                current_tab=self._current_tab,
                recent_events=events,
            )
            repo.set_summary("assistant_snapshot", snapshot, ttl_seconds=_SNAPSHOT_TTL)
            clear_dirty("assistant_snapshot")
        return repo.get_summary("assistant_snapshot") or {}

    def get_mix_snapshot(self) -> dict:
        if is_dirty("mix_preview") or repo.get_summary("mix_preview") is None:
            snapshot = build_mix_snapshot(self._db)
            repo.set_summary("mix_preview", snapshot, ttl_seconds=_SNAPSHOT_TTL)
            clear_dirty("mix_preview")
        return repo.get_summary("mix_preview") or {}

    def get_playback_context(self) -> dict:
        if is_dirty("playback_context") or repo.get_summary("playback_context") is None:
            snapshot = build_playback_snapshot(self._playback)
            repo.set_summary("playback_context", snapshot, ttl_seconds=60)
            clear_dirty("playback_context")
        return repo.get_summary("playback_context") or {}

    def invalidate(self, key: str) -> None:
        repo.mark_dirty(key)

    def recent_events(self, limit: int = 20) -> list[dict]:
        return repo.recent_events(limit=limit)
