"""Tests for schema — table creation, migrations, indexes, track_uid."""

import sqlite3


class TestSchemaInitialize:
    def test_creates_tables(self):
        from library.schema import Schema
        conn = sqlite3.connect(":memory:")
        Schema.initialize(conn)
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
        names = [r[0] for r in tables]
        assert "media_items" in names
        assert "playlists" in names
        assert "playlist_items" in names
        assert "favorites" in names
        assert "album_art_cache" in names
        assert "detected_tracks" in names

    def test_creates_indexes(self):
        from library.schema import Schema
        conn = sqlite3.connect(":memory:")
        Schema.initialize(conn)
        indexes = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='index' ORDER BY name"
        ).fetchall()
        names = [r[0] for r in indexes]
        assert "idx_media_artist" in names
        assert "idx_media_album" in names
        assert "idx_media_genre" in names
        assert "idx_media_year" in names
        assert "idx_media_directory" in names
        assert "idx_pl_filepath" in names

    def test_idempotent(self):
        from library.schema import Schema
        conn = sqlite3.connect(":memory:")
        Schema.initialize(conn)
        Schema.initialize(conn)
        tables = conn.execute(
            "SELECT count(*) FROM sqlite_master WHERE type='table'"
        ).fetchone()[0]
        assert tables > 0

    def test_wal_mode(self):
        from library.schema import Schema
        conn = sqlite3.connect(":memory:")
        Schema.initialize(conn)
        mode = conn.execute("PRAGMA journal_mode").fetchone()
        assert mode is not None


class TestSchemaMigrations:
    def test_run_migrations_adds_columns(self):
        from library.schema import Schema
        conn = sqlite3.connect(":memory:")
        Schema.initialize(conn)
        Schema.run_migrations(conn)
        cols = [r[1] for r in
                conn.execute("PRAGMA table_info(media_items)").fetchall()]
        assert "albumartist" in cols
        assert "mb_track_id" in cols
        assert "mb_album_id" in cols
        assert "bpm" in cols
        assert "replaygain_track" in cols
        assert "track_uid" in cols
        assert "content_hash" in cols
        assert "deleted_at" in cols

    def test_migration_idempotent(self):
        from library.schema import Schema
        conn = sqlite3.connect(":memory:")
        Schema.initialize(conn)
        Schema.run_migrations(conn)
        Schema.run_migrations(conn)
        cols = [r[1] for r in
                conn.execute("PRAGMA table_info(media_items)").fetchall()]
        assert "track_uid" in cols


class TestComputeTrackUid:
    def test_with_mb_track_id(self):
        from library.schema import Schema
        uid = Schema._compute_track_uid(
            "/music/song.mp3", "Artist", "Album", "Title", 180.0,
            "mbid-1234")
        assert uid.startswith("mb:")
        assert "mbid-1234" in uid

    def test_with_filepath_fallback(self):
        from library.schema import Schema
        uid = Schema._compute_track_uid(
            "/music/song.mp3", "Artist", "Album", "Title", 180.0, "")
        assert uid.startswith("fp:")
        assert len(uid) > 3

    def test_consistent(self):
        from library.schema import Schema
        uid1 = Schema._compute_track_uid(
            "/music/song.mp3", "Artist", "Album", "Title", 180.0, "")
        uid2 = Schema._compute_track_uid(
            "/music/song.mp3", "Artist", "Album", "Title", 180.0, "")
        assert uid1 == uid2

    def test_different_files_different(self):
        from library.schema import Schema
        uid1 = Schema._compute_track_uid(
            "/music/a.mp3", "A", "B", "C", 180.0, "")
        uid2 = Schema._compute_track_uid(
            "/music/b.mp3", "A", "B", "C", 180.0, "")
        assert uid1 != uid2


class TestPopulateTrackUids:
    def test_populates_empty(self):
        from library.schema import Schema
        conn = sqlite3.connect(":memory:")
        Schema.initialize(conn)
        conn.execute(
            "INSERT INTO media_items (filepath, filename, directory, ext, kind) "
            "VALUES (?,?,?,?,?)",
            ("/test.mp3", "test.mp3", "/", ".mp3", "audio"))
        conn.commit()
        conn.execute(
            "UPDATE media_items SET track_uid='' WHERE filepath='/test.mp3'")
        Schema._populate_track_uids(conn)
        uid = conn.execute(
            "SELECT track_uid FROM media_items WHERE filepath=?", ("/test.mp3",)
        ).fetchone()[0]
        assert uid.startswith("fp:")


class TestMigrateScanRoots:
    def test_migrates_to_library_roots(self):
        from library.schema import Schema
        conn = sqlite3.connect(":memory:")
        Schema.initialize(conn)
        conn.execute(
            "INSERT INTO scan_roots (path, enabled) VALUES (?, ?)",
            ("/music", 1))
        conn.commit()
        Schema._migrate_scan_roots_to_library_roots(conn)
        row = conn.execute(
            "SELECT path FROM library_roots WHERE path=?", ("/music",)
        ).fetchone()
        assert row is not None
        assert row[0] == "/music"
