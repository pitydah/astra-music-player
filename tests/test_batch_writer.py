"""Tests for BatchWriter — dynamic batch sizing, backoff, individual retry."""

import sqlite3
from library.schema import Schema


def _make_record(filepath: str, **overrides) -> dict:
    rec = {
        "filepath": filepath, "filename": "test.mp3",
        "directory": "/", "ext": ".mp3", "kind": "audio",
        "size": 0, "mtime": 0.0, "duration": 0.0,
        "channels": 0, "sample_rate": 0, "bitrate": 0,
        "title": "test", "artist": "", "album": "",
        "albumartist": "", "year": 0, "genre": "",
        "track_number": 0, "track_total": 0,
        "disc_number": 0, "disc_total": 0, "composer": "",
        "mb_track_id": "", "mb_album_id": "", "mb_albumartist_id": "",
        "bit_depth": 0, "bpm": 0,
        "replaygain_track": 0.0, "replaygain_album": 0.0,
        "replaygain_track_peak": 0.0,
        "isrc": "", "label": "", "conductor": "", "compilation": 0,
        "media_type": "", "encoder": "", "copyright": "",
        "originaldate": "", "remixer": "", "grouping": "", "mood": "",
        "comment": "", "lyricist": "",
        "replaygain_album_peak": 0.0, "r128_track_gain": 0.0,
        "r128_album_gain": 0.0, "mb_artist_id": "",
        "mb_releasegroup_id": "", "acoustid_id": "",
        "acoustid_fingerprint": "", "content_hash": "",
        "track_uid": "test:1234", "created_at": 0.0,
        "updated_at": 0.0, "last_scanned": 0.0, "scan_status": "ok",
    }
    rec.update(overrides)
    return rec


class TestBatchWriterBasics:
    def test_init_empty(self):
        conn = sqlite3.connect(":memory:")
        Schema.initialize(conn)
        from library.batch_writer import BatchWriter
        writer = BatchWriter(conn)
        assert writer.buffered == 0
        assert writer.total_written == 0
        conn.close()

    def test_add_buffers(self):
        conn = sqlite3.connect(":memory:")
        Schema.initialize(conn)
        from library.batch_writer import BatchWriter
        writer = BatchWriter(conn, batch_size=5)
        writer.add(_make_record("/test1.mp3"))
        assert writer.buffered == 1
        conn.close()

    def test_flush_writes(self):
        conn = sqlite3.connect(":memory:")
        Schema.initialize(conn)
        from library.batch_writer import BatchWriter
        writer = BatchWriter(conn, batch_size=2)
        writer.add(_make_record("/test1.mp3"))
        writer.add(_make_record("/test2.mp3"))
        assert writer.buffered == 0
        assert writer.total_written == 2
        conn.close()

    def test_upsert_same_filepath(self):
        conn = sqlite3.connect(":memory:")
        Schema.initialize(conn)
        from library.batch_writer import BatchWriter
        writer = BatchWriter(conn)
        writer.add(_make_record("/test.mp3", title="original"))
        writer.flush()
        writer.add(_make_record("/test.mp3", title="updated"))
        writer.flush()
        row = conn.execute(
            "SELECT title FROM media_items WHERE filepath=?", ("/test.mp3",)).fetchone()
        assert row[0] == "updated"
        conn.close()

    def test_default_for_string(self):
        from library.batch_writer import BatchWriter
        assert BatchWriter._default_for({}, "title") == ""

    def test_default_for_numeric(self):
        from library.batch_writer import BatchWriter
        assert BatchWriter._default_for({}, "year") == 0

    def test_default_for_float(self):
        from library.batch_writer import BatchWriter
        assert BatchWriter._default_for({}, "replaygain_track") == 0.0

    def test_default_for_missing_column(self):
        from library.batch_writer import BatchWriter
        assert BatchWriter._default_for({}, "mb_track_id") == ""


class TestBatchWriterBackoff:
    def test_batch_size_default(self):
        conn = sqlite3.connect(":memory:")
        Schema.initialize(conn)
        from library.batch_writer import BatchWriter
        writer = BatchWriter(conn)
        assert writer.current_batch_size == 100
        conn.close()

    def test_batch_size_custom(self):
        conn = sqlite3.connect(":memory:")
        Schema.initialize(conn)
        from library.batch_writer import BatchWriter
        writer = BatchWriter(conn, batch_size=50)
        assert writer.current_batch_size == 50
        conn.close()

    def test_shrink_batch(self):
        conn = sqlite3.connect(":memory:")
        Schema.initialize(conn)
        from library.batch_writer import BatchWriter
        writer = BatchWriter(conn, batch_size=100)
        writer._shrink_batch_size()
        assert writer.current_batch_size == 50
        writer._shrink_batch_size()
        assert writer.current_batch_size == 25
        conn.close()

    def test_grow_batch(self):
        conn = sqlite3.connect(":memory:")
        Schema.initialize(conn)
        from library.batch_writer import BatchWriter
        writer = BatchWriter(conn, batch_size=100)
        writer._current_batch = 50
        writer._grow_batch_size()
        assert writer.current_batch_size == 75
        conn.close()

    def test_grow_does_not_exceed_target(self):
        conn = sqlite3.connect(":memory:")
        Schema.initialize(conn)
        from library.batch_writer import BatchWriter
        writer = BatchWriter(conn, batch_size=100)
        writer._current_batch = 90
        writer._grow_batch_size()
        assert writer.current_batch_size == 100
        conn.close()

    def test_reset_batch_size(self):
        conn = sqlite3.connect(":memory:")
        Schema.initialize(conn)
        from library.batch_writer import BatchWriter
        writer = BatchWriter(conn, batch_size=100)
        writer._current_batch = 10
        writer.reset_batch_size()
        assert writer.current_batch_size == 100
        conn.close()

    def test_batch_auto_flush_at_current_size(self):
        conn = sqlite3.connect(":memory:")
        Schema.initialize(conn)
        from library.batch_writer import BatchWriter
        writer = BatchWriter(conn, batch_size=3)
        for i in range(3):
            writer.add(_make_record(f"/test{i}.mp3"))
        assert writer.buffered == 0
        assert writer.total_written == 3
        conn.close()


class TestBatchWriterEdgeCases:
    def test_flush_empty_buffer(self):
        conn = sqlite3.connect(":memory:")
        Schema.initialize(conn)
        from library.batch_writer import BatchWriter
        writer = BatchWriter(conn)
        writer.flush()
        assert writer.total_written == 0
        conn.close()

    def test_many_records(self):
        conn = sqlite3.connect(":memory:")
        Schema.initialize(conn)
        from library.batch_writer import BatchWriter
        writer = BatchWriter(conn, batch_size=10)
        for i in range(25):
            writer.add(_make_record(f"/test{i}.mp3", title=f"Song {i}"))
        writer.flush()
        assert writer.total_written == 25
        count = conn.execute(
            "SELECT COUNT(*) FROM media_items").fetchone()[0]
        assert count == 25
        conn.close()
