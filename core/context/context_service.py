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

_SNAPSHOT_TTL = 120


class ContextService:
    def __init__(self, db=None, playback=None, sync=None):
        self._db = db
        self._playback = playback
        self._sync = sync
        self._current_section = ""
        self._current_tab = ""

    # ── Helpers ──

    @staticmethod
    def _track_payload(track) -> dict:
        if track is None:
            return {}
        return {
            "title": getattr(track, "title", None) or getattr(track, "name", None),
            "artist": getattr(track, "artist", None),
            "album": getattr(track, "album", None),
        }

    # ── Events ──

    def record_event(self, event_type: str, payload: dict | None = None) -> None:
        repo.record_event(event_type, payload)
        invalidate_for_event(event_type)

    def record_scan_finished(self, summary: dict | None = None) -> None:
        self.record_event(AppEvent.SCAN_FINISHED, summary or {})

    def record_library_reloaded(self, reason: str = "", count: int = 0) -> None:
        self.record_event(AppEvent.LIBRARY_RELOADED, {"reason": reason, "tracks": count})

    def record_import_finished(self, reason: str = "", count: int = 0) -> None:
        self.record_event(AppEvent.IMPORT_FINISHED, {"reason": reason, "tracks": count})

    def record_metadata_saved(self, count: int = 0) -> None:
        self.record_event(AppEvent.METADATA_SAVED, {"count": count})

    def record_playback_stopped(self, reason: str = "") -> None:
        self.record_event(AppEvent.PLAYBACK_STOPPED, {"reason": reason})

    def record_quality_updated(self, quality: str = "", category: str = "") -> None:
        self.record_event(AppEvent.QUALITY_UPDATED, {"quality": quality, "quality_category": category})

    def record_now_playing_updated(self, title: str = "", artist: str = "", album: str = "") -> None:
        self.record_event(AppEvent.NOW_PLAYING_UPDATED, {"title": title, "artist": artist, "album": album})

    def record_assistant_action_confirmed(self, tool_name: str = "", affected_count: int = 0) -> None:
        self.record_event(AppEvent.ASSISTANT_ACTION_CONFIRMED, {"tool_name": tool_name, "affected_count": affected_count})

    def record_favorite_changed(self, track=None, favorite: bool = True) -> None:
        self.record_event(
            AppEvent.TRACK_FAVORITED if favorite else AppEvent.TRACK_UNFAVORITED,
            self._track_payload(track),
        )

    def record_sync_finished(self, payload: dict | None = None) -> None:
        self.record_event(AppEvent.SYNC_FINISHED, payload or {})

    def record_audio_analysis_finished(self, payload: dict | None = None) -> None:
        self.record_event(AppEvent.AUDIO_ANALYSIS_FINISHED, payload or {})

    def record_track_played(self, track=None) -> None:
        self.record_event(AppEvent.TRACK_PLAYED, self._track_payload(track))

    # ── Navigation & state ──

    def update_navigation(self, section: str, tab: str = "",
                          extra: dict | None = None) -> None:
        self._current_section = section
        self._current_tab = tab
        repo.set_state("navigation", {"section": section, "tab": tab, **(extra or {})})
        self.record_event(AppEvent.SECTION_CHANGED, {"section": section, "tab": tab})

    def get_navigation_state(self) -> dict:
        return repo.get_state("navigation", {"section": "", "tab": ""})

    def update_selection(self, track=None,
                          album: str | None = None,
                          artist: str | None = None,
                          genre: str | None = None,
                          playlist_id: int | None = None,
                          playlist_name: str | None = None,
                          folder_name: str | None = None,
                          mix_key: str | None = None,
                          search_query: str | None = None,
                          scope: str | None = None) -> None:
        current = repo.get_state("selection", {})
        payload = dict(current)

        inferred_scope = scope
        if inferred_scope is None:
            if track is not None:
                inferred_scope = "track"
            elif album is not None:
                inferred_scope = "album"
            elif artist is not None:
                inferred_scope = "artist"
            elif genre is not None:
                inferred_scope = "genre"
            elif playlist_id is not None or playlist_name is not None:
                inferred_scope = "playlist"
            elif folder_name is not None:
                inferred_scope = "folder"
            elif mix_key is not None:
                inferred_scope = "mix"
            elif search_query is not None:
                inferred_scope = "search"

        if inferred_scope is not None:
            payload["selection_scope"] = inferred_scope

        if album is not None:
            payload["album"] = album
        if artist is not None:
            payload["artist"] = artist
        if genre is not None:
            payload["genre"] = genre
        if playlist_id is not None:
            payload["playlist_id"] = playlist_id
        if playlist_name is not None:
            payload["playlist_name"] = playlist_name
        if folder_name is not None:
            payload["folder_name"] = folder_name
        if mix_key is not None:
            payload["mix_key"] = mix_key
        if search_query is not None:
            payload["search_query"] = search_query[:80] if search_query else ""
        if track is not None:
            payload["track"] = getattr(track, "title", None) or getattr(track, "name", None)
            payload["track_artist"] = getattr(track, "artist", None)
            payload["track_album"] = getattr(track, "album", None)

        repo.set_state("selection", payload)
        self.record_event(AppEvent.TRACK_SELECTED, payload)

    def clear_selection_for_scope(self, scope: str) -> dict:
        base = {
            "selection_scope": scope,
            "track": None,
            "track_artist": None,
            "track_album": None,
            "album": "",
            "artist": "",
            "genre": "",
            "playlist_id": None,
            "playlist_name": "",
            "folder_name": "",
            "mix_key": "",
            "search_query": "",
        }
        repo.set_state("selection", base)
        return base

    def get_selection_state(self) -> dict:
        return repo.get_state("selection", {})

    # ── Snapshots ──

    def _rebuild_if_dirty(self, key: str, builder, ttl: int = _SNAPSHOT_TTL):
        if is_dirty(key) or repo.get_summary(key) is None:
            snapshot = builder()
            repo.set_summary(key, snapshot, ttl_seconds=ttl)
            clear_dirty(key)
        return repo.get_summary(key) or {}

    def get_library_health(self) -> dict:
        return self._rebuild_if_dirty(
            "library_health", lambda: build_library_health_snapshot(self._db))

    def get_home_snapshot(self) -> dict:
        return self._rebuild_if_dirty(
            "home_snapshot", lambda: build_home_snapshot(self._db, self._playback, self._sync))

    def get_assistant_snapshot(self) -> dict:
        def _build():
            nav = repo.get_state("navigation", {})
            sel = repo.get_state("selection", {})
            section = nav.get("section", self._current_section)
            tab = nav.get("tab", self._current_tab)
            snap = build_assistant_snapshot(
                self._db, self._playback,
                current_section=section, current_tab=tab,
                recent_events=repo.recent_events(limit=10),
            )

            scope = sel.get("selection_scope")
            selection = {
                "scope": scope,
                "track": sel.get("track"),
                "track_artist": sel.get("track_artist"),
                "track_album": sel.get("track_album"),
                "album": sel.get("album"),
                "artist": sel.get("artist"),
                "genre": sel.get("genre"),
                "playlist_id": sel.get("playlist_id"),
                "playlist_name": sel.get("playlist_name"),
                "folder_name": sel.get("folder_name"),
                "mix_key": sel.get("mix_key"),
                "search_query": sel.get("search_query"),
            }
            snap["route"] = {"current_section": section, "current_tab": tab}
            snap["selection"] = selection
            snap["selection_scope"] = scope
            snap["selected_track"] = selection["track"]
            snap["selected_album"] = selection["album"]
            snap["selected_artist"] = selection["artist"]
            snap["selected_genre"] = selection["genre"]

            snap["assistant_capabilities"] = {
                "can_search_library": True,
                "can_create_playlist_from_selection": scope in {
                    "track", "album", "artist", "genre", "playlist",
                    "mix", "folder", "search",
                },
                "can_queue_selection": scope in {
                    "track", "album", "artist", "genre", "playlist",
                    "mix", "folder", "search",
                },
                "can_edit_metadata": scope in {"track", "album", "artist", "genre"},
                "can_analyze_selected_tracks": scope in {
                    "track", "album", "artist", "genre", "playlist",
                    "mix", "search",
                },
            }
            return snap
        return self._rebuild_if_dirty("assistant_snapshot", _build)

    def get_mix_snapshot(self) -> dict:
        return self._rebuild_if_dirty(
            "mix_preview", lambda: build_mix_snapshot(self._db))

    def get_playback_context(self) -> dict:
        return self._rebuild_if_dirty(
            "playback_context", lambda: build_playback_snapshot(self._playback), ttl=60)

    def invalidate(self, key: str) -> None:
        repo.mark_dirty(key)

    def recent_events(self, limit: int = 20) -> list[dict]:
        return repo.recent_events(limit=limit)
