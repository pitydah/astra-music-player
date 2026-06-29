"""Tests for ContextService — public facade."""

import os

from core.context import context_repository as repo
from core.context.context_service import ContextService
from core.context.context_events import AppEvent


def _init_db(tmp_path):
    db_path = os.path.join(str(tmp_path), "ctx.sqlite")
    repo.override_db_path(db_path)
    svc = ContextService(db=None, playback=None, sync=None)
    return svc, db_path


class TestContextService:

    def teardown_method(self):
        repo.close()
        repo.override_db_path(None)

    def test_record_event(self, tmp_path):
        svc, _ = _init_db(tmp_path)
        svc.record_event("test_event", {"key": "value"})
        events = svc.recent_events(5)
        assert any(e["event_type"] == "test_event" for e in events)

    def test_update_navigation_sets_state(self, tmp_path):
        svc, _ = _init_db(tmp_path)
        svc.update_navigation("albums", tab="all", extra={"filter": "active"})
        state = repo.get_state("navigation")
        assert state["section"] == "albums"
        assert state["tab"] == "all"
        assert state["filter"] == "active"

    def test_update_selection(self, tmp_path):
        svc, _ = _init_db(tmp_path)
        track = type("Track", (), {"title": "Song", "artist": "Artist", "name": "Song"})()
        svc.update_selection(track=track, album="Album", artist="Artist")
        state = repo.get_state("selection")
        assert state["album"] == "Album"
        assert state["artist"] == "Artist"
        assert state["track"] == "Song"

    def test_record_track_played(self, tmp_path):
        svc, _ = _init_db(tmp_path)
        track = type("Track", (), {"title": "Song", "artist": "Artist", "album": "Album"})()
        svc.record_track_played(track)
        events = svc.recent_events(5)
        assert any(e["event_type"] == AppEvent.TRACK_PLAYED for e in events)

    def test_get_library_health_returns_dict(self, tmp_path):
        svc, _ = _init_db(tmp_path)
        health = svc.get_library_health()
        assert isinstance(health, dict)
        assert "track_count" in health

    def test_get_home_snapshot_returns_dict(self, tmp_path):
        svc, _ = _init_db(tmp_path)
        snap = svc.get_home_snapshot()
        assert isinstance(snap, dict)
        assert "library_health" in snap

    def test_get_assistant_snapshot_returns_dict(self, tmp_path):
        svc, _ = _init_db(tmp_path)
        snap = svc.get_assistant_snapshot()
        assert isinstance(snap, dict)
        assert "current_section" in snap
        assert "suggested_actions" in snap

    def test_get_mix_snapshot_returns_dict(self, tmp_path):
        svc, _ = _init_db(tmp_path)
        snap = svc.get_mix_snapshot()
        assert isinstance(snap, dict)
        assert "total_tracks" in snap

    def test_invalidate_marks_dirty(self, tmp_path):
        svc, _ = _init_db(tmp_path)
        svc.invalidate("home_snapshot")
        assert repo.is_dirty("home_snapshot")

    def test_snapshot_cached_after_fetch(self, tmp_path):
        svc, _ = _init_db(tmp_path)
        svc.get_home_snapshot()
        assert not repo.is_dirty("home_snapshot")

    def test_snapshot_regenerated_after_invalidation(self, tmp_path):
        svc, _ = _init_db(tmp_path)
        svc.get_home_snapshot()
        svc.invalidate("home_snapshot")
        assert repo.is_dirty("home_snapshot")

    def test_no_crash_without_db(self, tmp_path):
        svc, _ = _init_db(tmp_path)
        snap = svc.get_assistant_snapshot()
        assert snap["library_health"]["track_count"] == 0

    def test_selection_with_all_params(self, tmp_path):
        svc, _ = _init_db(tmp_path)
        svc.update_selection(album="Album1", artist="Artist1", genre="Rock")
        snap = svc.get_assistant_snapshot()
        assert snap.get("selected_album") == "Album1"
        assert snap.get("selected_artist") == "Artist1"
        assert snap.get("selected_genre") == "Rock"

    def test_selection_roundtrip(self, tmp_path):
        svc, _ = _init_db(tmp_path)
        svc.update_selection(genre="Jazz")
        sel = svc.get_selection_state()
        assert sel.get("genre") == "Jazz"

    def test_update_selection_is_partial(self, tmp_path):
        svc, _ = _init_db(tmp_path)
        svc.update_selection(album="Album A", artist="Artist A")
        svc.update_selection(genre="Rock")

        sel = svc.get_selection_state()
        assert sel["album"] == "Album A"
        assert sel["artist"] == "Artist A"
        assert sel["genre"] == "Rock"

    def test_update_selection_can_clear_explicitly(self, tmp_path):
        svc, _ = _init_db(tmp_path)
        svc.update_selection(album="Album A", artist="Artist A", genre="Rock")
        svc.update_selection(album="")

        sel = svc.get_selection_state()
        assert sel["album"] == ""
        assert sel["artist"] == "Artist A"
        assert sel["genre"] == "Rock"
