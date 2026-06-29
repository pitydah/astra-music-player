"""Tests for ContextSnapshot — deterministic snapshot builders."""

from unittest.mock import MagicMock

from core.context.context_snapshot import (
    build_library_health_snapshot,
    build_playback_snapshot,
    build_assistant_snapshot,
    build_home_snapshot,
    build_mix_snapshot,
    _suggested_actions,
)


def _make_db(**overrides):
    db = MagicMock()
    db.get_dashboard_stats.return_value = {
        "total_songs": 1000,
        "total_albums": 50,
        "total_artists": 30,
        "missing_metadata": 10,
        **overrides,
    }
    conn = MagicMock()
    conn.execute.return_value.fetchone.return_value = (12,)
    db.conn = conn
    return db


def _make_empty_db():
    db = MagicMock()
    db.get_dashboard_stats.return_value = {
        "total_songs": 0, "total_albums": 0, "total_artists": 0, "missing_metadata": 0,
    }
    conn = MagicMock()
    conn.execute.return_value.fetchone.return_value = (0,)
    db.conn = conn
    return db


def _make_playback(**overrides):
    pb = MagicMock()
    pb.current_track = None
    pb.queue_length = 0
    pb.recent_count = 0
    pb.favorites_count = 0
    pb.source_type = "local"
    for k, v in overrides.items():
        setattr(pb, k, v)
    return pb


class TestLibraryHealthSnapshot:

    def test_with_full_data(self):
        db = _make_db()
        health = build_library_health_snapshot(db)
        assert health["track_count"] == 1000
        assert health["album_count"] == 50
        assert health["artist_count"] == 30
        assert health["genre_count"] == 12

    def test_with_empty_db(self):
        db = _make_empty_db()
        health = build_library_health_snapshot(db)
        assert health["track_count"] == 0

    def test_with_no_db(self):
        health = build_library_health_snapshot(None)
        assert health["track_count"] == 0
        assert health["missing_metadata_count"] == 0

    def test_safe_without_dashboard_stats(self):
        db = MagicMock()
        del db.get_dashboard_stats
        db.get_stats.return_value = {"total": 500}
        conn = MagicMock()
        conn.execute.return_value.fetchone.return_value = (5,)
        db.conn = conn
        health = build_library_health_snapshot(db)
        assert health["track_count"] == 500

    def test_missing_cover_count_included(self):
        db = _make_db()
        health = build_library_health_snapshot(db)
        assert "missing_cover_count" in health


class TestPlaybackSnapshot:

    def test_with_no_playback(self):
        snap = build_playback_snapshot(None)
        assert snap["now_playing"] is None
        assert snap["queue_length"] == 0

    def test_with_playback(self):
        track = MagicMock()
        track.title = "Test Song"
        track.artist = "Test Artist"
        track.album = "Test Album"
        pb = _make_playback(current_track=track, queue_length=5)
        snap = build_playback_snapshot(pb)
        assert snap["now_playing"]["title"] == "Test Song"
        assert snap["queue_length"] == 5

    def test_no_current_track(self):
        pb = _make_playback(queue_length=3)
        snap = build_playback_snapshot(pb)
        assert snap["now_playing"] is None
        assert snap["queue_length"] == 3


class TestAssistantSnapshot:

    def test_basic_assistant_snapshot(self):
        db = _make_db()
        pb = _make_playback()
        snap = build_assistant_snapshot(db, pb, current_section="albums")
        assert snap["current_section"] == "albums"
        assert snap["library_health"]["track_count"] == 1000
        assert isinstance(snap["suggested_actions"], list)

    def test_empty_assistant_snapshot(self):
        snap = build_assistant_snapshot(None)
        assert snap["current_section"] == ""
        assert snap["library_health"]["track_count"] == 0


class TestHomeSnapshot:

    def test_home_snapshot_no_sync(self):
        db = _make_db()
        snap = build_home_snapshot(db)
        assert snap["library_health"]["track_count"] == 1000
        assert "sync_peers" in snap

    def test_home_snapshot_with_sync(self):
        sync = MagicMock()
        sync.peer_count = 3
        snap = build_home_snapshot(_make_db(), sync=sync)
        assert snap["sync_peers"] == 3


class TestMixSnapshot:

    def test_mix_snapshot(self):
        db = _make_db()
        snap = build_mix_snapshot(db)
        assert snap["total_tracks"] == 1000
        assert snap["total_albums"] == 50


class TestSuggestedActions:

    def test_no_actions_when_healthy(self):
        health = {
            "track_count": 1000, "missing_metadata_count": 0,
            "missing_cover_count": 0, "tracks_without_audio_features": 0,
            "index_error_count": 0,
        }
        playback = {
            "now_playing": {"title": "Song"},
            "recently_played_count": 20,
            "favorites_count": 10,
        }
        actions = _suggested_actions(health, playback)
        assert len(actions) == 0

    def test_suggest_metadata_repair(self):
        health = {
            "track_count": 100, "missing_metadata_count": 60,
            "missing_cover_count": 0, "tracks_without_audio_features": 0,
            "index_error_count": 0,
        }
        playback = {"now_playing": None, "recently_played_count": 0, "favorites_count": 0}
        actions = _suggested_actions(health, playback)
        titles = [a["title"] for a in actions]
        assert "Revisar metadatos pendientes" in titles

    def test_suggest_play_something(self):
        health = {
            "track_count": 100, "missing_metadata_count": 0,
            "missing_cover_count": 0, "tracks_without_audio_features": 0,
            "index_error_count": 0,
        }
        playback = {"now_playing": None, "recently_played_count": 0, "favorites_count": 0}
        actions = _suggested_actions(health, playback)
        titles = [a["title"] for a in actions]
        assert "Reproducir algo ahora" in titles

    def test_suggest_favorites(self):
        health = {
            "track_count": 100, "missing_metadata_count": 0,
            "missing_cover_count": 0, "tracks_without_audio_features": 0,
            "index_error_count": 0,
        }
        playback = {"now_playing": {"title": "S"}, "recently_played_count": 10, "favorites_count": 0}
        actions = _suggested_actions(health, playback)
        titles = [a["title"] for a in actions]
        assert "Marcar favoritos" in titles
