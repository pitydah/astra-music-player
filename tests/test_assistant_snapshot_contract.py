"""Tests: Assistant snapshot contract — route, selection, capabilities, no filepaths."""

import os
from core.context import context_repository as repo
from core.context.context_service import ContextService


class DummyTrack:
    uri = "/home/user/music/secret_song.flac"
    title = "Song"
    artist = "Artist"
    album = "Album"
    genre = "Rock"


class TestAssistantSnapshotContract:

    def teardown_method(self):
        repo.close()
        repo.override_db_path(None)

    def _svc(self, tmp_path):
        repo.override_db_path(os.path.join(str(tmp_path), "ctx.sqlite"))
        return ContextService()

    def test_contains_route_selection_playback_health(self, tmp_path):
        svc = self._svc(tmp_path)
        snap = svc.get_assistant_snapshot()
        assert "route" in snap
        assert "selection" in snap
        assert "playback" in snap
        assert "library_health" in snap

    def test_contains_capabilities_and_legacy(self, tmp_path):
        svc = self._svc(tmp_path)
        snap = svc.get_assistant_snapshot()
        assert "assistant_capabilities" in snap
        assert "selected_track" in snap
        assert "selected_album" in snap
        assert "current_section" in snap
        assert "selection_scope" in snap
        assert "now_playing" in snap
        assert "queue_length" in snap

    def test_sanitizes_absolute_paths_from_selection(self, tmp_path):
        svc = self._svc(tmp_path)
        svc.update_selection(
            scope="track",
            track=DummyTrack(),
            folder_name="/home/user/Music/Rock",
            search_query="/tmp/private/song.flac",
        )
        snap = svc.get_assistant_snapshot()
        raw = str(snap)
        assert "/home/" not in raw
        assert "/tmp/" not in raw
        assert "filepath" not in raw
        assert "uri" not in raw

    def test_recent_events_max_10(self, tmp_path):
        svc = self._svc(tmp_path)
        for i in range(20):
            svc.record_event("test_event", {"i": i})
        snap = svc.get_assistant_snapshot()
        assert len(snap.get("recent_events", [])) <= 10

    def test_suggested_actions_max_5(self, tmp_path):
        from core.context.context_snapshot import _suggested_actions
        health = {
            "track_count": 1000,
            "missing_metadata_count": 999,
            "missing_cover_count": 999,
            "tracks_without_audio_features": 999,
            "index_error_count": 99,
        }
        playback = {"now_playing": None, "recently_played_count": 0, "favorites_count": 0}
        actions = _suggested_actions(health, playback)
        assert len(actions) <= 5
