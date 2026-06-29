"""Context invalidator — maps events to dirty flags for derived summaries."""

from __future__ import annotations

from core.context.context_events import AppEvent
from core.context import context_repository as repo

_EVENT_DIRTY_MAP: dict[str, set[str]] = {
    AppEvent.SCAN_FINISHED: {"home_snapshot", "assistant_snapshot", "mix_preview", "library_health"},
    AppEvent.TRACK_PLAYED: {"home_snapshot", "assistant_snapshot", "mix_preview", "playback_context"},
    AppEvent.TRACK_PAUSED: {"playback_context"},
    AppEvent.TRACK_FAVORITED: {"home_snapshot", "assistant_snapshot", "mix_preview"},
    AppEvent.TRACK_UNFAVORITED: {"home_snapshot", "assistant_snapshot", "mix_preview"},
    AppEvent.SYNC_FINISHED: {"home_snapshot", "assistant_snapshot", "sync_context"},
    AppEvent.DEVICE_CONNECTED: {"home_snapshot", "assistant_snapshot", "sync_context"},
    AppEvent.DEVICE_DISCONNECTED: {"home_snapshot", "assistant_snapshot", "sync_context"},
    AppEvent.AUDIO_ANALYSIS_FINISHED: {"assistant_snapshot", "mix_preview", "library_health"},
    AppEvent.SECTION_CHANGED: {"assistant_snapshot"},
    AppEvent.LIBRARY_TAB_CHANGED: {"assistant_snapshot"},
    AppEvent.TRACK_SELECTED: {"assistant_snapshot"},
    AppEvent.MIX_PREVIEW_GENERATED: {"mix_preview"},
    AppEvent.METADATA_REPAIR_FINISHED: {"home_snapshot", "assistant_snapshot", "library_health"},
    AppEvent.APP_STARTED: {"home_snapshot", "assistant_snapshot", "library_health", "playback_context", "sync_context"},
}

_DIRTY_FLAG_KEYS: set[str] = set()
for flags in _EVENT_DIRTY_MAP.values():
    _DIRTY_FLAG_KEYS.update(flags)


def invalidate_for_event(event_type: str) -> None:
    """Mark all dirty flags associated with an event type."""
    flags = _EVENT_DIRTY_MAP.get(event_type, set())
    for key in flags:
        repo.mark_dirty(key)


def invalidate_all() -> None:
    """Mark all known dirty flags."""
    for key in _DIRTY_FLAG_KEYS:
        repo.mark_dirty(key)


def clear_dirty(key: str) -> None:
    repo.clear_dirty(key)


def is_dirty(key: str) -> bool:
    return repo.is_dirty(key)


def all_dirty_flags() -> set[str]:
    return _DIRTY_FLAG_KEYS
