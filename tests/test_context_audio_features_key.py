"""Tests: audio features use make_track_key(filepath), not track_uid."""

from unittest.mock import MagicMock


def test_uses_make_track_key(monkeypatch):
    captured_calls = []
    captured_keys = []
    captured_close = []

    def fake_make_track_key(fp):
        captured_calls.append(fp)
        return f"KEY::{fp}"

    class DummyRepo:
        def count_missing(self, keys):
            captured_keys.extend(keys)
            return len(keys)
        def close(self):
            captured_close.append(True)

    monkeypatch.setattr("audio_analysis.feature_extractor.make_track_key", fake_make_track_key)
    monkeypatch.setattr("audio_analysis.feature_repository.FeatureRepository", lambda: DummyRepo())

    conn = MagicMock()
    conn.execute.return_value.fetchall.return_value = [
        ("/music/a.flac",),
        ("/music/b.flac",),
    ]

    from core.context.context_snapshot import _count_tracks_without_audio_features
    result = _count_tracks_without_audio_features(conn)

    assert result == 2
    assert captured_calls == ["/music/a.flac", "/music/b.flac"]
    assert captured_keys == ["KEY::/music/a.flac", "KEY::/music/b.flac"]
    assert captured_close == [True]

    sql = conn.execute.call_args[0][0]
    assert "track_uid" not in sql
    assert "SELECT filepath" in sql


def test_returns_0_when_no_tracks():
    conn = MagicMock()
    conn.execute.return_value.fetchall.return_value = []
    from core.context.context_snapshot import _count_tracks_without_audio_features
    result = _count_tracks_without_audio_features(conn)
    assert result == 0


def test_returns_0_on_error():
    conn = MagicMock()
    conn.execute.side_effect = Exception("DB error")
    from core.context.context_snapshot import _count_tracks_without_audio_features
    result = _count_tracks_without_audio_features(conn)
    assert result == 0
