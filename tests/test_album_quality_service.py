"""Tests for AlbumQualityService — fast and full analysis."""
from unittest.mock import MagicMock, patch


def _make_track(filepath="/m/s.flac", album="A", artist="X",
                ext="flac", sample_rate=44100, bit_depth=16, bitrate=1411):
    t = MagicMock()
    t.filepath = filepath
    t.album = album
    t.artist = artist
    t.ext = ext
    t.sample_rate = sample_rate
    t.bit_depth = bit_depth
    t.bitrate = bitrate
    t.duration = 200.0
    t.year = 2024
    t.title = "Song"
    return t


class TestAlbumQualityService:
    def test_summarize_fast_flac(self):
        from library.album_quality_service import AlbumQualityService
        svc = AlbumQualityService()
        result = svc.summarize_fast([_make_track()])
        assert result.has_lossless is True
        assert result.dominant_quality in ("lossless", "hires")

    def test_summarize_fast_empty(self):
        from library.album_quality_service import AlbumQualityService
        svc = AlbumQualityService()
        result = svc.summarize_fast([])
        assert result.dominant_format == ""

    def test_analyze_album_with_mocks(self):
        import tempfile, os
        from library.album_quality_service import AlbumQualityService
        svc = AlbumQualityService()
        with tempfile.NamedTemporaryFile(suffix=".flac", delete=False) as f:
            f.write(b"x" * 1024)
            real_path = f.name
        try:
            tracks = [_make_track(filepath=real_path)]
            with patch("core.audio_lab.diagnostics_service.analyse_file",
                       return_value={
                           "format_info": {"container": "FLAC", "sample_rate": 44100,
                                           "bit_depth": 16, "bitrate": 1411},
                           "quality": {"category": "lossless"},
                       }):
                result = svc.analyze_album(tracks)
                assert result.tracks_analyzed == 1
                assert result.has_lossless is True
        finally:
            os.unlink(real_path)

    def test_analyze_album_progress(self):
        from library.album_quality_service import AlbumQualityService
        svc = AlbumQualityService()
        calls = []

        def cb(c, t):
            calls.append((c, t))

        with patch("core.audio_lab.diagnostics_service.analyse_file",
                   return_value={
                       "format_info": {"container": "FLAC"},
                       "quality": {"category": "lossless"},
                   }):
            svc.analyze_album([_make_track(), _make_track(filepath="/m/s2.flac")],
                              progress_cb=cb)
            assert len(calls) == 2
