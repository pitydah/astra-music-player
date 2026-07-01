"""Tests: SongsStatusService batch badge loading."""

from unittest.mock import patch

from library.media_item import MediaItem


def _make_item(id: int, fp: str, ext="flac", sr=44100, bd=16):
    item = MediaItem()
    item.id = id
    item.filepath = fp
    item.ext = ext
    item.sample_rate = sr
    item.bit_depth = bd
    item.title = "t"
    item.artist = "artist"
    item.album = "album"
    item.genre = "genre"
    item.bitrate = 0
    return item


class TestBatchBadges:

    def test_compute_batch_calls_badges_for_paths_once(self):
        items = [_make_item(1, "/p1.flac"), _make_item(2, "/p2.wav")]
        fake = {"/p1.flac": {"label": "FLAC", "kind": "hires", "tooltip": ""},
                "/p2.wav": {"label": "WAV", "kind": "lossless", "tooltip": ""}}
        with patch("library.audio_lab_badges.get_audio_lab_badges_for_paths",
                   return_value=fake) as m:
            from library.songs_status_service import SongsStatusService
            svc = SongsStatusService()
            result = svc.compute_batch(items)
            m.assert_called_once()
            assert 1 in result and 2 in result

    def test_compute_batch_returns_quality_labels(self):
        items = [_make_item(1, "/p1.flac", sr=96000, bd=24),
                 _make_item(2, "/p2.mp3", ext="mp3")]
        fake = {"/p1.flac": {"label": "FLAC 24/96", "kind": "hires", "tooltip": ""},
                "/p2.mp3": {"label": "MP3", "kind": "lossy", "tooltip": ""}}
        with patch("library.audio_lab_badges.get_audio_lab_badges_for_paths",
                   return_value=fake):
            from library.songs_status_service import SongsStatusService
            svc = SongsStatusService()
            result = svc.compute_batch(items)
            assert result[1]["quality_category"] == "hires"
            assert result[2]["quality_category"] == "lossy"

    def test_invalidate_cache_for_paths_clears_specific(self):
        from library.songs_status_service import SongsStatusService
        svc = SongsStatusService()
        svc._quality_cache = {1: {"badges": ["/p1.flac"]}, 2: {"badges": ["/p2.wav"]}}
        svc.invalidate_cache_for_paths(["/p1.flac"])
        assert 1 not in svc._quality_cache
        assert 2 in svc._quality_cache

    def test_invalidate_cache_for_paths_none_clears_all(self):
        from library.songs_status_service import SongsStatusService
        svc = SongsStatusService()
        svc._quality_cache = {1: {}, 2: {}}
        svc.invalidate_cache_for_paths()
        assert svc._quality_cache == {}

    def test_compute_status_accepts_diag_badge_kwarg(self):
        from library.songs_status_service import SongsStatusService
        item = _make_item(1, "/p.flac")
        svc = SongsStatusService()
        badge = {"label": "FLAC 24/96", "kind": "hires", "tooltip": ""}
        result = svc.compute_status(item, diag_badge=badge)
        assert result["quality_category"] == "hires"

    def test_compute_batch_empty_no_crash(self):
        from library.songs_status_service import SongsStatusService
        svc = SongsStatusService()
        result = svc.compute_batch([])
        assert result == {}
