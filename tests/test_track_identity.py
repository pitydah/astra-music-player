"""Tests for TrackIdentityService."""
import hashlib
import tempfile
from pathlib import Path

from library.track_identity import (
    TrackIdentityService, FP_PREFIX, MB_PREFIX, ACOUSTID_PREFIX,
)


def _make(**kw):
    d = {"filepath": "/m/test.flac", "title": "T", "artist": "A", "album": "Al",
         "duration": 240.0, "size": 1000, "mb_track_id": "", "acoustid_id": "",
         "content_hash": "", "file_hash": ""}
    d.update(kw)
    return d


class TestPriority:
    def test_mb_wins(self):
        assert TrackIdentityService.compute_track_uid(
            _make(mb_track_id="abc-def-123")).startswith(MB_PREFIX)

    def test_acoustid_second(self):
        assert TrackIdentityService.compute_track_uid(
            _make(acoustid_id="ac-xyz")).startswith(ACOUSTID_PREFIX)

    def test_fp_fallback(self):
        assert TrackIdentityService.compute_track_uid(
            _make(title="", artist="")).startswith(FP_PREFIX)


class TestStability:
    def test_mb_stable_across_move(self):
        r1 = _make(filepath="/old.flac", mb_track_id="abc")
        r2 = _make(filepath="/new.flac", mb_track_id="abc")
        assert TrackIdentityService.compute_track_uid(r1) == TrackIdentityService.compute_track_uid(r2)

    def test_diff_tracks_diff_uid(self):
        assert TrackIdentityService.compute_track_uid(
            _make(mb_track_id="a")) != TrackIdentityService.compute_track_uid(
            _make(mb_track_id="b"))


class TestIsPathBased:
    def test_mb_not_path(self):
        assert not TrackIdentityService.is_path_based_uid(f"{MB_PREFIX}abc")

    def test_fp_is_path(self):
        assert TrackIdentityService.is_path_based_uid(f"{FP_PREFIX}abc")


class TestNeedsUpgrade:
    def test_path_upgradable(self):
        assert TrackIdentityService.needs_identity_upgrade(
            f"{FP_PREFIX}dead", _make(mb_track_id="abc"))

    def test_mb_not_needed(self):
        assert not TrackIdentityService.needs_identity_upgrade(
            f"{MB_PREFIX}abc", _make(mb_track_id="abc"))


class TestDuplicates:
    def test_no_dups(self):
        assert TrackIdentityService.find_duplicates(
            [_make(mb_track_id="a"), _make(mb_track_id="b")]) == []

    def test_dups(self):
        assert len(TrackIdentityService.find_duplicates(
            [_make(mb_track_id="a"), _make(mb_track_id="a")])) == 1


class TestHashes:
    def test_quick_hash(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"x" * 200000)
            p = f.name
        try:
            h = TrackIdentityService.compute_quick_hash(p)
            assert len(h) == 32
        finally:
            Path(p).unlink(missing_ok=True)

    def test_file_hash(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"hello")
            p = f.name
        try:
            h = TrackIdentityService.compute_file_hash(p)
            assert h == hashlib.sha256(b"hello").hexdigest()
        finally:
            Path(p).unlink(missing_ok=True)

    def test_quick_hash_not_found(self):
        assert TrackIdentityService.compute_quick_hash("/nope.flac") == ""

    def test_metadata_hash(self):
        r = _make(title="S", artist="A")
        assert TrackIdentityService.compute_metadata_hash(r)
