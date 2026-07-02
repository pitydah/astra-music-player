"""Tests for LibraryMutationService."""
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from library.library_mutation_service import LibraryMutationService, LibraryMutationResult


@pytest.fixture
def db():
    conn = sqlite3.connect(":memory:")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS media_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filepath TEXT UNIQUE NOT NULL,
            filename TEXT DEFAULT '', directory TEXT DEFAULT '',
            ext TEXT DEFAULT '', kind TEXT DEFAULT '', size INTEGER DEFAULT 0,
            mtime REAL DEFAULT 0.0, duration REAL DEFAULT 0.0,
            channels INTEGER DEFAULT 0, sample_rate INTEGER DEFAULT 0,
            bitrate INTEGER DEFAULT 0, title TEXT DEFAULT '',
            artist TEXT DEFAULT '', album TEXT DEFAULT '', year INTEGER DEFAULT 0,
            genre TEXT DEFAULT '', track_number INTEGER DEFAULT 0,
            track_total INTEGER DEFAULT 0, disc_number INTEGER DEFAULT 0,
            disc_total INTEGER DEFAULT 0, composer TEXT DEFAULT '',
            albumartist TEXT DEFAULT '', mb_track_id TEXT DEFAULT '',
            mb_album_id TEXT DEFAULT '', mb_albumartist_id TEXT DEFAULT '',
            bit_depth INTEGER DEFAULT 0, bpm INTEGER DEFAULT 0,
            replaygain_track REAL DEFAULT 0.0, replaygain_album REAL DEFAULT 0.0,
            replaygain_track_peak REAL DEFAULT 0.0,
            replaygain_album_peak REAL DEFAULT 0.0,
            r128_track_gain REAL DEFAULT 0.0, r128_album_gain REAL DEFAULT 0.0,
            isrc TEXT DEFAULT '', label TEXT DEFAULT '', conductor TEXT DEFAULT '',
            compilation INTEGER DEFAULT 0, media_type TEXT DEFAULT '',
            encoder TEXT DEFAULT '', copyright TEXT DEFAULT '',
            originaldate TEXT DEFAULT '', remixer TEXT DEFAULT '',
            grouping TEXT DEFAULT '', mood TEXT DEFAULT '',
            comment TEXT DEFAULT '', lyricist TEXT DEFAULT '',
            mb_artist_id TEXT DEFAULT '', mb_releasegroup_id TEXT DEFAULT '',
            acoustid_id TEXT DEFAULT '', acoustid_fingerprint TEXT DEFAULT '',
            content_hash TEXT DEFAULT '', file_hash TEXT DEFAULT '',
            metadata_hash TEXT DEFAULT '', track_uid TEXT DEFAULT '',
            play_count INTEGER DEFAULT 0, rating INTEGER DEFAULT 0,
            last_played REAL DEFAULT 0.0, created_at REAL DEFAULT 0.0,
            updated_at REAL DEFAULT 0.0, last_scanned REAL DEFAULT 0.0,
            deleted_at REAL DEFAULT NULL, scan_status TEXT DEFAULT '',
            scan_error TEXT DEFAULT ''
        )
    """)
    conn.execute("CREATE TABLE IF NOT EXISTS track_genres (track_id INTEGER, genre TEXT)")
    mock = MagicMock()
    mock.conn = conn
    return mock


@pytest.fixture
def svc(db):
    return LibraryMutationService(db)


def _tmp(suffix=".flac"):
    f = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    f.write(b"fLaC" + b"\x00" * 100)
    f.close()
    return f.name


class TestAddFile:
    def test_success(self, svc):
        path = _tmp()
        try:
            with patch("library.media_record_builder.extract_metadata_combined",
                       return_value={"title": "T", "artist": "A", "duration": 240.0}):
                r = svc.add_file(path)
            assert r.added == 1
        finally:
            Path(path).unlink(missing_ok=True)

    def test_nonexistent(self, svc):
        assert svc.add_file("/nope.flac").errors

    def test_unknown_ext(self, svc):
        path = _tmp(".txt")
        try:
            assert svc.add_file(path).skipped == 1
        finally:
            Path(path).unlink(missing_ok=True)


class TestRemove:
    def test_remove(self, svc, db):
        db.conn.execute(
            "INSERT INTO media_items (filepath,filename,directory,ext,kind) "
            "VALUES (?,?,?,?,?)", ("/t.flac", "t.flac", "/t", "flac", "audio"))
        db.conn.commit()
        r = svc.remove_paths(["/t.flac"])
        assert r.removed == 1

    def test_remove_empty(self, svc):
        assert svc.remove_paths([]).removed == 0


class TestResultMerge:
    def test_merge(self):
        r1 = LibraryMutationResult(added=2, removed=1)
        r2 = LibraryMutationResult(added=1, errors=["e"])
        r3 = r1.merge(r2)
        assert r3.added == 3
        assert r3.errors == ["e"]
