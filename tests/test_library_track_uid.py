"""Tests: track_uid stability — LibraryDB._compute_track_uid."""

import sqlite3
from unittest.mock import MagicMock


class TestLibraryTrackUid:

    def setup_method(self):
        self.conn = sqlite3.connect(":memory:")

    def teardown_method(self):
        self.conn.close()

    def _db(self):
        from library.library_db import LibraryDB
        db = MagicMock(spec=LibraryDB)
        db._conn = self.conn
        return db

    def test_musicbrainz_id_produces_mb_prefix(self):
        from library.library_db import LibraryDB
        uid = LibraryDB._compute_track_uid(
            "/music/a.flac", "Artist", "Album", "Title", 180.0,
            "550e8400-e29b-41d4-a716-446655440000",
        )
        assert uid.startswith("mb:")
        assert "550e8400" in uid

    def test_no_musicbrainz_produces_fp_prefix(self):
        from library.library_db import LibraryDB
        uid = LibraryDB._compute_track_uid(
            "/music/a.flac", "Artist", "Album", "Title", 180.0,
            None,
        )
        assert uid.startswith("fp:")

    def test_same_path_produces_same_uid(self):
        from library.library_db import LibraryDB
        uid1 = LibraryDB._compute_track_uid(
            "/music/a.flac", "A", "B", "C", 180.0, None,
        )
        uid2 = LibraryDB._compute_track_uid(
            "/music/a.flac", "A", "B", "C", 180.0, None,
        )
        assert uid1 == uid2

    def test_different_path_different_uid_without_mb(self):
        from library.library_db import LibraryDB
        uid1 = LibraryDB._compute_track_uid(
            "/music/a.flac", "A", "B", "C", 180.0, None,
        )
        uid2 = LibraryDB._compute_track_uid(
            "/music/b.flac", "A", "B", "C", 180.0, None,
        )
        assert uid1 != uid2

    def test_same_path_same_uid_even_with_different_metadata_with_mb(self):
        from library.library_db import LibraryDB
        uid1 = LibraryDB._compute_track_uid(
            "/music/a.flac", "A", "B", "C", 180.0,
            "550e8400-e29b-41d4-a716-446655440000",
        )
        uid2 = LibraryDB._compute_track_uid(
            "/music/a.flac", "X", "Y", "Z", 200.0,
            "550e8400-e29b-41d4-a716-446655440000",
        )
        assert uid1 == uid2

    def test_only_one_definition(self):
        from library.library_db import LibraryDB
        members = [m for m in dir(LibraryDB) if "_compute_track_uid" in m]
        assert len(members) == 1, f"Found {len(members)} definitions: {members}"
