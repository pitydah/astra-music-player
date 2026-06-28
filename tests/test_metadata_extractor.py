"""Tests for metadata_extractor — parsing, merging, and ID3v1 utilities."""

import os
import tempfile


class TestParseTrackNumber:
    def test_none(self):
        from library.metadata_extractor import parse_track_number
        assert parse_track_number(None) == (0, 0)

    def test_empty(self):
        from library.metadata_extractor import parse_track_number
        assert parse_track_number("") == (0, 0)

    def test_single(self):
        from library.metadata_extractor import parse_track_number
        assert parse_track_number("3") == (3, 0)

    def test_with_total(self):
        from library.metadata_extractor import parse_track_number
        assert parse_track_number("3/12") == (3, 12)



    def test_float_string(self):
        from library.metadata_extractor import parse_track_number
        assert parse_track_number("3.0") == (3, 0)

    def test_zero(self):
        from library.metadata_extractor import parse_track_number
        assert parse_track_number(0) == (0, 0)


class TestParseDiscNumber:
    def test_delegates(self):
        from library.metadata_extractor import parse_disc_number
        assert parse_disc_number("1/2") == (1, 2)


class TestParseYear:
    def test_none(self):
        from library.metadata_extractor import parse_year
        assert parse_year(None) == 0

    def test_empty(self):
        from library.metadata_extractor import parse_year
        assert parse_year("") == 0

    def test_int(self):
        from library.metadata_extractor import parse_year
        assert parse_year(1999) == 1999

    def test_string(self):
        from library.metadata_extractor import parse_year
        assert parse_year("1999") == 1999

    def test_date_string(self):
        from library.metadata_extractor import parse_year
        assert parse_year("2024-01-15") == 2024

    def test_short_string(self):
        from library.metadata_extractor import parse_year
        assert parse_year("99") == 99


class TestMergeMetadataByPriority:
    def test_empty(self):
        from library.metadata_extractor import merge_metadata_by_priority
        assert merge_metadata_by_priority() == {}

    def test_first_wins(self):
        from library.metadata_extractor import merge_metadata_by_priority
        result = merge_metadata_by_priority(
            {"title": "first", "artist": ""},
            {"title": "second", "artist": "Artist B"},
        )
        assert result["title"] == "first"
        assert result["artist"] == "Artist B"

    def test_none_values_skipped(self):
        from library.metadata_extractor import merge_metadata_by_priority
        result = merge_metadata_by_priority(
            {"title": None, "artist": "A"},
            {"title": "Real Title"},
        )
        assert result["title"] == "Real Title"

    def test_zero_values_skipped(self):
        from library.metadata_extractor import merge_metadata_by_priority
        result = merge_metadata_by_priority(
            {"year": 0},
            {"year": 2024},
        )
        assert result["year"] == 2024

    def test_empty_bytes_skipped(self):
        from library.metadata_extractor import merge_metadata_by_priority
        result = merge_metadata_by_priority(
            {"cover_data": b""},
            {"cover_data": b"real_data"},
        )
        assert result["cover_data"] == b"real_data"


class TestExtractId3V1:
    def test_no_tag(self):
        from library.metadata_extractor import extract_id3v1
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            f.write(b"\x00" * 128)
            path = f.name
        try:
            info = extract_id3v1(path)
            assert info["title"] == ""
        finally:
            os.unlink(path)

    def test_valid_tag(self):
        from library.metadata_extractor import extract_id3v1
        data = bytearray(128)
        data[0:3] = b"TAG"
        data[3:33] = b"Test Title\x00" + b"\x00" * 19
        data[33:63] = b"Test Artist\x00" + b"\x00" * 18
        data[63:93] = b"Test Album\x00" + b"\x00" * 19
        data[93:97] = b"1999"
        data[97:127] = b"\x00" * 30
        data[125] = 0
        data[126] = 5
        data[127] = 10
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            f.write(b"\x00" * 100)
            f.write(bytes(data))
            path = f.name
        try:
            info = extract_id3v1(path)
            assert info["title"] == "Test Title"
            assert info["artist"] == "Test Artist"
            assert info["album"] == "Test Album"
            assert info["year"] == 1999
            assert info["track_number"] == 5
            assert info["genre"] == "New Age"
        finally:
            os.unlink(path)

    def test_short_file(self):
        from library.metadata_extractor import extract_id3v1
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            f.write(b"x" * 50)
            path = f.name
        try:
            info = extract_id3v1(path)
            assert info["title"] == ""
        finally:
            os.unlink(path)


class TestSafeUri:
    def test_file_uri(self):
        from library.metadata_extractor import _safe_uri
        uri = _safe_uri("/tmp/test.mp3")
        assert uri.startswith("file://")


class TestAUDIO_EXTS:
    def test_extensions(self):
        from library.metadata_extractor import AUDIO_EXTS
        assert ".mp3" in AUDIO_EXTS
        assert ".flac" in AUDIO_EXTS
        assert ".ogg" in AUDIO_EXTS
        assert ".opus" in AUDIO_EXTS
        assert ".wav" in AUDIO_EXTS
        assert ".m4a" in AUDIO_EXTS
        assert ".dsf" in AUDIO_EXTS
        assert ".dff" in AUDIO_EXTS

    def test_all_exts_same(self):
        from library.metadata_extractor import AUDIO_EXTS, ALL_EXTS
        assert AUDIO_EXTS == ALL_EXTS
