"""Tests for tag_reader — frame maps, artwork extraction, read_tags."""

import os
import tempfile


class TestFrameMaps:
    def test_id3_frame_map(self):
        from metadata.tag_reader import _ID3_FRAME_MAP
        assert _ID3_FRAME_MAP["TIT2"] == "title"
        assert _ID3_FRAME_MAP["TPE1"] == "artist"
        assert _ID3_FRAME_MAP["TALB"] == "album"
        assert _ID3_FRAME_MAP["TRCK"] == "tracknumber"
        assert _ID3_FRAME_MAP["TDRC"] == "date"

    def test_mp4_read_map(self):
        from metadata.tag_reader import _MP4_READ_MAP
        assert "\xa9nam" in _MP4_READ_MAP
        assert "\xa9ART" in _MP4_READ_MAP

    def test_mp4_alt_map(self):
        from metadata.tag_reader import _MP4_READ_MAP_ALT
        assert "©nam" in _MP4_READ_MAP_ALT

    def test_audio_exts(self):
        from metadata.tag_reader import AUDIO_EXTS
        assert ".mp3" in AUDIO_EXTS
        assert ".flac" in AUDIO_EXTS
        assert ".ogg" in AUDIO_EXTS


class TestReadArtwork:
    def test_non_audio_file(self):
        from metadata.tag_reader import _read_artwork
        result = _read_artwork(None, "mp3")
        assert result == (False, "", None)

    def test_no_tags(self):
        from metadata.tag_reader import _read_artwork
        f = type("FakeFile", (), {"tags": None, "pictures": []})()
        result = _read_artwork(f, "mp3")
        assert result == (False, "", None)


class TestReadTags:
    def test_missing_file(self):
        from metadata.tag_reader import read_tags
        tags = read_tags("/nonexistent/file.mp3")
        assert tags is not None
        assert tags.error

    def test_empty_file(self):
        from metadata.tag_reader import read_tags
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            path = f.name
        try:
            tags = read_tags(path)
            assert tags is not None
        finally:
            os.unlink(path)

    def test_text_fields(self):
        from metadata.tag_reader import TrackTags
        assert "title" in TrackTags.TEXT_FIELDS
        assert "artist" in TrackTags.TEXT_FIELDS
        assert "album" in TrackTags.TEXT_FIELDS
        assert "genre" in TrackTags.TEXT_FIELDS

    def test_not_mutagen_available(self):
        import metadata.tag_reader as tr
        original = tr._mutagen_available
        tr._mutagen_available = False
        try:
            tags = tr.read_tags("/test.mp3")
            assert tags.error
        finally:
            tr._mutagen_available = original
