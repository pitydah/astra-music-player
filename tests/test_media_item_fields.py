"""Tests for MediaItem extended fields."""
from library.media_item import MediaItem


class TestNewFields:
    def test_defaults(self):
        item = MediaItem()
        assert item.comment == ""
        assert item.content_hash == ""
        assert item.file_hash == ""
        assert item.metadata_hash == ""
        assert item.scan_status == ""
        assert item.quality == ""
        assert item.analysis_status == ""
        assert item.spectral_verdict == ""

    def test_from_dict(self):
        item = MediaItem.from_dict({
            "filepath": "/t.flac", "comment": "Great",
            "quality": "Hi-Res", "analysis_status": "done",
            "content_hash": "ch_abc"})
        assert item.comment == "Great"
        assert item.quality == "Hi-Res"
        assert item.content_hash == "ch_abc"

    def test_from_row(self):
        row = (1, "/t.flac", "t.flac", "/t", "flac", "audio",
               1000, 100.0, 240.0, 2, 44100, 320000,
               "T", "A", "Al", 2024, "Rock", 1, "C", "AA",
               1, 1, 10, "mb-t", "mb-a", "mb-aa",
               24, 120, "ISRC", "L", "Cond", 0, "Album", "Enc",
               "Cop", "2024-01-01", "Rem", "Grp", "Mood",
               0.5, 0.6, 0.7, 5, 100.0, 4,  # play count, last, rating
               100.0, 200.0, 300.0, "mb:abc",  # timestamps, uid
               # new fields:
               "Nice", "Lyric", 0.98, -8.5, -6.0,
               "mb-art-2", "mb-rel-1", "ac-id", "ac-fp",
               "ch_h", "fh_h", "mh_h",
               0.0, "ok", "", "Cm", "Hi-Res", "done", "genuine")
        item = MediaItem.from_row(row)
        assert item.comment == "Nice"
        assert item.lyricist == "Lyric"
        assert item.replaygain_album_peak == 0.98
        assert item.r128_track_gain == -8.5
        assert item.content_hash == "ch_h"
        assert item.file_hash == "fh_h"
        assert item.metadata_hash == "mh_h"
        assert item.scan_status == "ok"
        assert item.key == "Cm"
        assert item.quality == "Hi-Res"
        assert item.analysis_status == "done"
        assert item.spectral_verdict == "genuine"

    def test_to_dict(self):
        item = MediaItem(id=1, comment="Nice", quality="Hi-Res")
        d = item.to_dict()
        assert d["comment"] == "Nice"
        assert d["quality"] == "Hi-Res"
        assert "content_hash" in d
