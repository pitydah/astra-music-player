"""Tests for MediaRecordBuilder."""
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from library.media_record_builder import MediaRecordBuilder


def _dummy(**kw):
    d = {"title": "Test", "artist": "A", "album": "Al", "duration": 240.0,
         "genre": "Rock", "year": 2024, "track_number": 1, "bitrate": 960000,
         "sample_rate": 96000, "bit_depth": 24, "channels": 2, "compilation": 0}
    d.update(kw)
    return d


def _tmp_file(suffix=".flac", data=b"fLaC" + b"\x00" * 100):
    f = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    f.write(data)
    f.close()
    return f.name


class TestBuild:
    def test_build_success(self):
        builder = MediaRecordBuilder()
        path = _tmp_file()
        try:
            with patch("library.media_record_builder.extract_metadata_combined",
                       return_value=_dummy()):
                r = builder.build(path)
            assert r.record is not None
            assert r.record["title"] == "Test"
        finally:
            Path(path).unlink(missing_ok=True)

    def test_build_nonexistent(self):
        assert MediaRecordBuilder().build("/nope.flac").record is None

    def test_build_unknown_ext(self):
        path = _tmp_file(".txt", b"hello")
        try:
            assert MediaRecordBuilder().build(path).record is None
        finally:
            Path(path).unlink(missing_ok=True)

    def test_build_track_uid(self):
        builder = MediaRecordBuilder()
        path = _tmp_file()
        try:
            with patch("library.media_record_builder.extract_metadata_combined",
                       return_value=_dummy(mb_track_id="abc12345-1234-5678-abcd-123456789abc")):
                r = builder.build(path)
            assert r.record["track_uid"].startswith("mb:")
        finally:
            Path(path).unlink(missing_ok=True)

    def test_build_preserves(self):
        builder = MediaRecordBuilder()
        path = _tmp_file()
        try:
            with patch("library.media_record_builder.extract_metadata_combined",
                       return_value=_dummy()):
                r = builder.build(path, preserve={"play_count": 5, "track_uid": "mb:abc"})
            assert r.record["play_count"] == 5
            assert r.record["track_uid"] == "mb:abc"
        finally:
            Path(path).unlink(missing_ok=True)

    def test_build_hash(self):
        builder = MediaRecordBuilder()
        path = _tmp_file(data=b"x" * 200000)
        try:
            with patch("library.media_record_builder.extract_metadata_combined",
                       return_value=_dummy()):
                r = builder.build(path, compute_hashes=True)
            assert len(r.record.get("content_hash", "")) == 32
        finally:
            Path(path).unlink(missing_ok=True)

    def test_build_skip_hash(self):
        builder = MediaRecordBuilder()
        path = _tmp_file()
        try:
            with patch("library.media_record_builder.extract_metadata_combined",
                       return_value=_dummy()):
                r = builder.build(path, compute_hashes=False)
            assert r.record.get("content_hash", "") == ""
        finally:
            Path(path).unlink(missing_ok=True)

    def test_cover_cache(self):
        mock_db = MagicMock()
        builder = MediaRecordBuilder(db=mock_db)
        path = _tmp_file()
        try:
            with patch("library.media_record_builder.extract_metadata_combined",
                       return_value=_dummy(cover_data=b"\x89PNG\r\n\x1a\n")):
                r = builder.build(path)
            assert r.record is not None
            mock_db.conn.execute.assert_called()
        finally:
            Path(path).unlink(missing_ok=True)
