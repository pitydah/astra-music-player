"""Tests for change_detector — hashing, caching, hierarchical detection."""

import os
import tempfile
from unittest.mock import MagicMock


class TestComputeQuickHash:
    def test_empty_file(self):
        from library.change_detector import compute_quick_hash
        with tempfile.NamedTemporaryFile(delete=False) as f:
            path = f.name
        try:
            h = compute_quick_hash(path)
            assert h != ""
            assert len(h) == 64
        finally:
            os.unlink(path)

    def test_small_file(self):
        from library.change_detector import compute_quick_hash
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"x" * 100)
            path = f.name
        try:
            h = compute_quick_hash(path)
            assert h != ""
        finally:
            os.unlink(path)

    def test_large_file(self):
        from library.change_detector import compute_quick_hash
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"x" * 200000)
            path = f.name
        try:
            h = compute_quick_hash(path)
            assert h != ""
        finally:
            os.unlink(path)

    def test_different_files_different_hash(self):
        from library.change_detector import compute_quick_hash
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"AAAA")
            p1 = f.name
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"BBBB")
            p2 = f.name
        try:
            h1 = compute_quick_hash(p1)
            h2 = compute_quick_hash(p2)
            assert h1 != h2
        finally:
            os.unlink(p1)
            os.unlink(p2)

    def test_missing_file(self):
        from library.change_detector import compute_quick_hash
        assert compute_quick_hash("/nonexistent/file.mp3") == ""


class TestComputeFullHash:
    def test_full_hash(self):
        from library.change_detector import compute_full_hash
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"hello world")
            path = f.name
        try:
            h = compute_full_hash(path)
            assert h != ""
            assert len(h) == 64
        finally:
            os.unlink(path)


class TestIsFileUnchanged:
    def test_not_in_db(self):
        from library.change_detector import is_file_unchanged
        db = MagicMock()
        db.get_file_signature.return_value = None
        stat = os.stat_result([0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        assert is_file_unchanged(db, "/test.mp3", stat) is False

    def test_size_changed(self):
        from library.change_detector import is_file_unchanged
        db = MagicMock()
        db.get_file_signature.return_value = (100, 1000, "")
        stat = os.stat_result([0, 0, 0, 0, 0, 0, 200, 0, 0, 0])
        assert is_file_unchanged(db, "/test.mp3", stat) is False

    def test_size_same_mtime_same_hash_match(self):
        from library.change_detector import is_file_unchanged, _HASH_CACHE
        _HASH_CACHE.clear()
        db = MagicMock()
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test")
            path = f.name
        try:
            from library.change_detector import compute_quick_hash
            h = compute_quick_hash(path)
            sz = os.path.getsize(path)
            db.get_file_signature.return_value = (sz, 1000, h)
            stat = os.stat_result([0, 0, 0, 0, 0, 0, sz, 0, 1000, 0])
            result = is_file_unchanged(db, path, stat)
            assert result is True
        finally:
            os.unlink(path)

    def test_size_same_mtime_same_no_hash(self):
        from library.change_detector import is_file_unchanged, _HASH_CACHE
        _HASH_CACHE.clear()
        db = MagicMock()
        db.get_file_signature.return_value = (100, 1000, "")
        stat = os.stat_result([0, 0, 0, 0, 0, 0, 100, 0, 1000, 0])
        assert is_file_unchanged(db, "/test.mp3", stat) is True


class TestHashCache:
    def test_cache_hit(self):
        from library.change_detector import _HASH_CACHE, clear_cache
        clear_cache()
        from library.change_detector import _cache_set
        _cache_set("/test.mp3", "abc123")
        assert _HASH_CACHE.get("/test.mp3") == "abc123"

    def test_cache_miss(self):
        from library.change_detector import _HASH_CACHE, clear_cache
        clear_cache()
        assert _HASH_CACHE.get("/nonexistent.mp3") is None

    def test_cache_clear(self):
        from library.change_detector import _HASH_CACHE, _cache_set, clear_cache
        _cache_set("/test.mp3", "abc")
        clear_cache()
        assert _HASH_CACHE.get("/test.mp3") is None
