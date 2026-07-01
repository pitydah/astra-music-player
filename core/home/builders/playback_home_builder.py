"""PlaybackHomeBuilder — builds PlaybackHomeStatus."""

from __future__ import annotations

import logging
from typing import Any

from core.home.home_status import PlaybackHomeStatus

logger = logging.getLogger("michi.home.builders.playback")


def normalize_playback_state(state: Any) -> str:
    if state is None:
        return "stopped"
    if hasattr(state, "name"):
        state = str(state.name)
    value = str(state).lower()
    if "." in value:
        value = value.rsplit(".", 1)[-1]
    if value in ("playing",):
        return "playing"
    if value in ("paused",):
        return "paused"
    return "stopped"


def build_playback_status(playback: Any = None, context_svc: Any = None) -> PlaybackHomeStatus:
    if playback is None:
        return PlaybackHomeStatus()

    try:
        raw = getattr(playback, "state", "stopped") or "stopped"
    except Exception:
        raw = "unknown"
    state = normalize_playback_state(raw)

    has_current = state in ("playing", "paused")
    title = ""
    artist = ""
    album = ""
    position = 0.0
    duration = 0.0

    if has_current:
        try:
            cur = playback.current if hasattr(playback, "current") else None
            if cur:
                title = getattr(cur, "title", "") or ""
                artist = getattr(cur, "artist", "") or ""
                album = getattr(cur, "album", "") or ""
        except Exception:
            pass
        try:
            if hasattr(playback, "_position"):
                position = getattr(playback, "_position", 0.0)
                duration = getattr(playback, "_duration", 0.0)
        except Exception:
            pass

    queue_active = False
    queue_count = 0
    try:
        qs = playback.get_queue_state() if hasattr(playback, "get_queue_state") else None
        if qs:
            queue_active = qs.get("active", False) or qs.get("count", 0) > 0
            queue_count = qs.get("count", 0)
    except Exception:
        pass

    last_title = ""
    last_artist = ""
    if context_svc is not None and not has_current:
        try:
            snap = context_svc.get_home_snapshot()
            if snap and "playback" in snap:
                pb_snap = snap["playback"]
                np = pb_snap.get("now_playing", {}) or {}
                last_title = np.get("title", "")
                last_artist = np.get("artist", "")
        except Exception:
            pass

    can_continue = has_current or bool(last_title)

    return PlaybackHomeStatus(
        has_current_track=has_current,
        current_title=title,
        current_artist=artist,
        current_album=album,
        current_position=position,
        current_duration=duration,
        queue_active=queue_active,
        queue_count=queue_count,
        last_track_title=last_title,
        last_track_artist=last_artist,
        can_continue=can_continue,
        state=state,
    )
