"""Tests: TrackRefTableModel uses batch badge loading."""

from unittest.mock import patch

from sources.base_source import TrackRef


class TestTrackRefTableModelBatch:
    def test_populate_calls_badges_for_paths_once(self):
        from library.trackref_model import TrackRefTableModel
        items = [
            TrackRef(uri="/path/1.flac", title="a", artist="x"),
            TrackRef(uri="/path/2.wav", title="b", artist="y"),
        ]
        fake = {"/path/1.flac": {"label": "FLAC", "kind": "hires", "tooltip": ""},
                "/path/2.wav": {"label": "WAV", "kind": "lossless", "tooltip": ""}}
        with patch("library.audio_lab_badges.get_audio_lab_badges_for_paths",
                   return_value=fake) as m:
            model = TrackRefTableModel()
            model.populate(items)
            m.assert_called_once_with(["/path/1.flac", "/path/2.wav"])

    def test_quality_column_shows_badge_label(self):
        from library.trackref_model import TrackRefTableModel
        items = [TrackRef(uri="/a.flac", title="a", artist="x", duration=100)]
        fake = {"/a.flac": {"label": "FLAC 24/96", "kind": "hires", "tooltip": "Hi-Res"}}
        with patch("library.audio_lab_badges.get_audio_lab_badges_for_paths",
                   return_value=fake):
            model = TrackRefTableModel()
            model.populate(items)
            idx = model.index(0, model.COL_QUALITY)
            assert idx.data() == "FLAC 24/96"

    def test_populate_fallback_if_batch_empty(self):
        from library.trackref_model import TrackRefTableModel
        items = [TrackRef(uri="/new.flac", title="a", artist="x", duration=100)]
        with patch("library.audio_lab_badges.get_audio_lab_badges_for_paths",
                   return_value={}):
            model = TrackRefTableModel()
            with patch.object(model, "_get_badge",
                              return_value={"label": "FLAC", "kind": "lossless"}):
                model.populate(items)
                idx = model.index(0, model.COL_QUALITY)
                assert idx.data() == "FLAC"

    def test_invalidate_quality_cache_clears_all(self):
        from library.trackref_model import TrackRefTableModel
        model = TrackRefTableModel()
        model._quality_cache = {"/a": {}, "/b": {}}
        model.invalidate_quality_cache()
        assert model._quality_cache == {}

    def test_invalidate_quality_cache_clears_specific(self):
        from library.trackref_model import TrackRefTableModel
        model = TrackRefTableModel()
        model._quality_cache = {"/a": {}, "/b": {}}
        model.invalidate_quality_cache(["/a"])
        assert "/a" not in model._quality_cache
        assert "/b" in model._quality_cache
