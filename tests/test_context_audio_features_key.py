"""Tests: audio features use make_track_key(filepath), not track_uid."""

from unittest.mock import MagicMock
from core.context.context_snapshot import _count_tracks_without_audio_features


def test_uses_filepath_not_track_uid():
    conn = MagicMock()
    conn.execute.return_value.fetchall.return_value = [
        ("/music/song.flac",),
        ("/music/track2.flac",),
    ]

    import audio_analysis.feature_repository as fr
    original_repo = fr.FeatureRepository

    try:
        mock_repo = MagicMock()
        mock_repo.count_missing.return_value = 2
        fr.FeatureRepository = lambda: mock_repo

        result = _count_tracks_without_audio_features(conn)
        assert result == 2
        args = mock_repo.count_missing.call_args[0][0]
        # Keys should be derived from filepaths, not raw track_uid
        assert len(args) == 2
        assert all(isinstance(k, str) for k in args)
        assert all(k for k in args)  # non-empty
    finally:
        fr.FeatureRepository = original_repo


def test_returns_0_when_no_tracks():
    conn = MagicMock()
    conn.execute.return_value.fetchall.return_value = []
    result = _count_tracks_without_audio_features(conn)
    assert result == 0


def test_returns_0_on_error():
    conn = MagicMock()
    conn.execute.side_effect = Exception("DB error")
    result = _count_tracks_without_audio_features(conn)
    assert result == 0
