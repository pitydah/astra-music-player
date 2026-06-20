"""Tests for CoverArtService — cover art finding and quality labeling."""
import os
import tempfile

from library.cover_art_service import CoverArtService


class TestCoverArtService:
    def test_find_cover_existing(self):
        with tempfile.TemporaryDirectory() as tmp:
            # Create a cover.jpg
            cover = os.path.join(tmp, "cover.jpg")
            with open(cover, "wb") as f:
                f.write(b"\xff\xd8\xff\xe0")  # minimal JPEG header

            track = os.path.join(tmp, "song.flac")
            with open(track, "wb") as f:
                f.write(b"fake")

            result = CoverArtService.find_cover(track)
            assert result == cover

    def test_find_cover_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            track = os.path.join(tmp, "song.flac")
            with open(track, "wb") as f:
                f.write(b"fake")

            result = CoverArtService.find_cover(track)
            assert result == ""

    def test_find_cover_empty_path(self):
        assert CoverArtService.find_cover("") == ""
        assert CoverArtService.find_cover(None) == ""

    def test_quality_label_empty(self):
        qual, extra = CoverArtService.quality_label("")
        assert qual == ""
        assert extra == ""

    def test_quality_label_none(self):
        qual, extra = CoverArtService.quality_label(None)
        assert qual == ""
        assert extra == ""
