"""Tests for artwork_cache hybrid cleanup."""
import os
import tempfile
import pytest


class TestArtworkCacheCleanup:
    @pytest.fixture
    def cache_dir(self):
        with tempfile.TemporaryDirectory() as d:
            yield d

    def _make_files(self, cache_dir: str, sizes: list[int]) -> list:
        files = []
        for i, size in enumerate(sizes):
            fpath = os.path.join(cache_dir, f"cache_{i}.png")
            data = b"\x00" * size
            os.makedirs(cache_dir, exist_ok=True)
            with open(fpath, "wb") as f:
                f.write(data)
            os.utime(fpath, (1000 + i, 1000 + i))  # ordered mtimes
            files.append(fpath)
        return files

    def test_cleanup_by_count(self, cache_dir, monkeypatch):
        """Oldest files exceeding max_count should be removed."""
        from library import artwork_cache
        monkeypatch.setattr(artwork_cache, "_cache_dir", lambda: cache_dir)

        self._make_files(cache_dir, [100] * 10)  # 10 files, 100 bytes each
        artwork_cache.cleanup_cache(max_count=5, max_size_mb=999)

        remaining = [f for f in os.listdir(cache_dir) if f.endswith(".png")]
        assert len(remaining) == 5

    def test_cleanup_by_size(self, cache_dir, monkeypatch):
        """Exceeding max_size_mb should remove oldest until under limit."""
        from library import artwork_cache
        monkeypatch.setattr(artwork_cache, "_cache_dir", lambda: cache_dir)

        # 5 files × 500KB = 2.5MB total
        self._make_files(cache_dir, [500000] * 5)
        artwork_cache.cleanup_cache(max_count=999, max_size_mb=1)

        remaining = [f for f in os.listdir(cache_dir) if f.endswith(".png")]
        total = sum(os.path.getsize(os.path.join(cache_dir, f)) for f in remaining)
        assert total <= 1 * 1024 * 1024

    def test_cleanup_missing_dir(self):
        """cleanup_cache on non-existent dir should not raise."""
        from library import artwork_cache
        artwork_cache.cleanup_cache()
        # Should not raise

    def test_cleanup_empty_dir(self, cache_dir, monkeypatch):
        """Empty dir should not raise."""
        from library import artwork_cache
        monkeypatch.setattr(artwork_cache, "_cache_dir", lambda: cache_dir)
        artwork_cache.cleanup_cache()
        assert os.listdir(cache_dir) == []

    def test_cleanup_skips_non_png(self, cache_dir, monkeypatch):
        """Non-PNG files should be left alone by cleanup."""
        from library import artwork_cache
        monkeypatch.setattr(artwork_cache, "_cache_dir", lambda: cache_dir)

        self._make_files(cache_dir, [100] * 3)
        # Add a non-PNG file
        txt_path = os.path.join(cache_dir, "readme.txt")
        with open(txt_path, "w") as f:
            f.write("hello")

        artwork_cache.cleanup_cache(max_count=1)

        # The txt file should still exist
        assert os.path.exists(txt_path)
