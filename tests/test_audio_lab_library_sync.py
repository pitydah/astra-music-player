"""Tests for Audio Lab — library sync, search filters, end-to-end integration."""

from __future__ import annotations

import sqlite3


def _make_db():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS media_items (
            id INTEGER PRIMARY KEY,
            filepath TEXT UNIQUE,
            title TEXT,
            artist TEXT,
            album TEXT,
            year INTEGER,
            genre TEXT,
            ext TEXT,
            quality TEXT DEFAULT '',
            analysis_status TEXT DEFAULT '',
            spectral_verdict TEXT DEFAULT ''
        )
    """)
    conn.execute("CREATE TABLE IF NOT EXISTS library_roots (path TEXT PRIMARY KEY, enabled INTEGER DEFAULT 1)")
    conn.execute("CREATE TABLE IF NOT EXISTS scan_roots (path TEXT PRIMARY KEY, enabled INTEGER DEFAULT 1)")
    conn.commit()
    return conn


class TestAudioLabLibrarySync:

    def test_sync_existing_path_returns_true(self):
        from core.audio_lab.audio_lab_sync import sync_audio_lab_result_to_media_item
        conn = _make_db()
        conn.execute("INSERT INTO media_items (filepath) VALUES (?)", ("/test/a.flac",))
        conn.commit()
        result = {"quality": {"category": "lossless"}, "error": "",
                  "format_info": {"container": "FLAC"}}
        assert sync_audio_lab_result_to_media_item(conn, "/test/a.flac", result) is True

    def test_sync_nonexistent_path_returns_false(self):
        from core.audio_lab.audio_lab_sync import sync_audio_lab_result_to_media_item
        conn = _make_db()
        result = {"quality": {"category": "lossless"}, "error": ""}
        assert sync_audio_lab_result_to_media_item(conn, "/test/nonexistent.flac", result) is False

    def test_sync_result_updates_columns(self):
        from core.audio_lab.audio_lab_sync import sync_audio_lab_result_to_media_item
        conn = _make_db()
        conn.execute("INSERT INTO media_items (filepath) VALUES (?)", ("/test/a.flac",))
        conn.commit()
        result = {"quality": {"category": "lossless"}, "error": "",
                  "format_info": {"container": "FLAC"}}
        sync_audio_lab_result_to_media_item(conn, "/test/a.flac", result)
        row = conn.execute("SELECT quality, analysis_status FROM media_items WHERE filepath=?", ("/test/a.flac",)).fetchone()
        assert row["quality"] == "lossless"
        assert row["analysis_status"] == "done"

    def test_sync_error_result(self):
        from core.audio_lab.audio_lab_sync import sync_audio_lab_result_to_media_item
        conn = _make_db()
        conn.execute("INSERT INTO media_items (filepath) VALUES (?)", ("/test/b.mp3",))
        conn.commit()
        result = {"quality": {}, "error": "formato corrupto"}
        sync_audio_lab_result_to_media_item(conn, "/test/b.mp3", result)
        row = conn.execute("SELECT quality, analysis_status FROM media_items WHERE filepath=?", ("/test/b.mp3",)).fetchone()
        assert row["analysis_status"] == "error"

    def test_sync_spectral_suspicious(self):
        from core.audio_lab.audio_lab_sync import sync_audio_lab_result_to_media_item
        conn = _make_db()
        conn.execute("INSERT INTO media_items (filepath) VALUES (?)", ("/test/c.wav",))
        conn.commit()
        result = {"quality": {"category": "hires"}, "error": "",
                  "spectral": {"verdict": "SUSPICIOUS_UPSAMPLING"}}
        sync_audio_lab_result_to_media_item(conn, "/test/c.wav", result)
        row = conn.execute("SELECT quality, spectral_verdict FROM media_items WHERE filepath=?", ("/test/c.wav",)).fetchone()
        assert row["quality"] == "hires"
        assert row["spectral_verdict"] == "SUSPICIOUS_UPSAMPLING"

    def test_mark_pending(self):
        from core.audio_lab.audio_lab_sync import mark_audio_lab_pending
        conn = _make_db()
        conn.execute("INSERT INTO media_items (filepath) VALUES (?)", ("/test/d.flac",))
        conn.commit()
        mark_audio_lab_pending(conn, "/test/d.flac")
        row = conn.execute("SELECT analysis_status FROM media_items WHERE filepath=?", ("/test/d.flac",)).fetchone()
        assert row["analysis_status"] == "pending"

    def test_mark_error(self):
        from core.audio_lab.audio_lab_sync import mark_audio_lab_error
        conn = _make_db()
        conn.execute("INSERT INTO media_items (filepath) VALUES (?)", ("/test/e.mp3",))
        conn.commit()
        mark_audio_lab_error(conn, "/test/e.mp3", "error!")
        row = conn.execute("SELECT analysis_status FROM media_items WHERE filepath=?", ("/test/e.mp3",)).fetchone()
        assert row["analysis_status"] == "error"

    def test_sync_three_paths_returns_exact_count(self):
        from core.audio_lab.audio_lab_sync import sync_audio_lab_cache_to_media_items
        from core.audio_lab.diagnostics_service import (
            reset_global_cache_for_tests, close_global_cache, _get_cache,
        )
        conn = _make_db()
        paths = []
        import os, tempfile
        for _ in range(3):
            with tempfile.NamedTemporaryFile(suffix=".flac", delete=False) as f:
                paths.append(f.name)
        try:
            reset_global_cache_for_tests(":memory:")
            cache = _get_cache()
            for p in paths:
                cache.put(p, {
                    "filepath": p,
                    "format_info": {"container": "FLAC", "sample_rate": 44100},
                    "quality": {"category": "lossless"},
                })
                conn.execute("INSERT INTO media_items (filepath) VALUES (?)", (p,))
            conn.commit()
            updated = sync_audio_lab_cache_to_media_items(conn, paths)
            assert updated == 3
        finally:
            for p in paths:
                os.unlink(p)
            close_global_cache()

    def test_consecutive_syncs_do_not_inflate_count(self):
        from core.audio_lab.audio_lab_sync import sync_audio_lab_cache_to_media_items
        from core.audio_lab.diagnostics_service import (
            reset_global_cache_for_tests, close_global_cache, _get_cache,
        )
        conn = _make_db()
        import os, tempfile
        with tempfile.NamedTemporaryFile(suffix=".flac", delete=False) as f:
            p = f.name
        try:
            reset_global_cache_for_tests(":memory:")
            cache = _get_cache()
            cache.put(p, {
                "filepath": p,
                "format_info": {"container": "FLAC"},
                "quality": {"category": "lossless"},
            })
            conn.execute("INSERT INTO media_items (filepath) VALUES (?)", (p,))
            conn.commit()
            r1 = sync_audio_lab_cache_to_media_items(conn, [p])
            r2 = sync_audio_lab_cache_to_media_items(conn, [p])
            assert r1 == 1
            assert r2 == 1  # not inflated
        finally:
            os.unlink(p)
            close_global_cache()


def _get_cache():
    from core.audio_lab.diagnostics_service import _get_cache
    return _get_cache()


class TestAudioLabSearchFilters:

    def test_quality_hires_filter(self):
        from library.search_engine import _build_field_clause
        from library.query_parser import FieldTerm, FieldOp
        clause, params = _build_field_clause(
            FieldTerm(field="quality", op=FieldOp.EQ, value="hires")
        )
        assert "quality" in clause
        assert "hires" in params

    def test_analysis_pending_filter(self):
        from library.search_engine import _build_field_clause
        from library.query_parser import FieldTerm, FieldOp
        clause, params = _build_field_clause(
            FieldTerm(field="analysis_status", op=FieldOp.EQ, value="pending")
        )
        assert "pending" in clause or "analysis_status" in clause

    def test_analysis_error_filter(self):
        from library.search_engine import _build_field_clause
        from library.query_parser import FieldTerm, FieldOp
        clause, params = _build_field_clause(
            FieldTerm(field="analysis_status", op=FieldOp.EQ, value="error")
        )
        assert "error" in params

    def test_spectral_suspicious_filter(self):
        from library.search_engine import _build_field_clause
        from library.query_parser import FieldTerm, FieldOp
        clause, params = _build_field_clause(
            FieldTerm(field="spectral_verdict", op=FieldOp.EQ, value="suspicious")
        )
        assert "SUSPICIOUS_UPSAMPLING" in clause

    def test_spectral_inconclusive_filter(self):
        from library.search_engine import _build_field_clause
        from library.query_parser import FieldTerm, FieldOp
        clause, params = _build_field_clause(
            FieldTerm(field="spectral_verdict", op=FieldOp.EQ, value="inconclusive")
        )
        assert "INCONCLUSIVE" in params

    def test_combined_filter_artist_quality(self):
        from library.query_parser import parse_query
        from library.search_engine import _build_field_clause
        q = parse_query("artist:Genesis quality:lossless")
        assert len(q.terms) == 2
        for t in q.terms:
            clause, params = _build_field_clause(t)
            assert clause  # non-empty


class TestAudioLabBadgesBatch:

    def test_get_badges_for_files_returns_all(self):
        from core.audio_lab.diagnostics_service import get_badges_for_files
        paths = ["/a.flac", "/b.mp3", "/c.dsf"]
        result = get_badges_for_files(paths)
        assert len(result) == 3
        assert result["/a.flac"]["kind"] == "lossless"
        assert result["/b.mp3"]["kind"] == "lossy"
        assert result["/c.dsf"]["kind"] == "dsd"

    def test_get_badges_for_files_empty(self):
        from core.audio_lab.diagnostics_service import get_badges_for_files
        assert get_badges_for_files([]) == {}

    def test_get_badges_for_files_nonexistent(self):
        from core.audio_lab.diagnostics_service import get_badges_for_files
        result = get_badges_for_files(["/nonexistent.xyz"])
        assert len(result) == 1
        assert result["/nonexistent.xyz"]["kind"] in ("unknown",)
