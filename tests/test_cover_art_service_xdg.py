"""Tests for CoverArtService — XDG path resolution."""



class TestCoverArtServiceXDG:
    def test_cache_dir_uses_xdg(self, monkeypatch):
        """CoverArtService CACHE_DIR should resolve via core.paths, not legacy ~/.cache/michi."""
        monkeypatch.setenv("MICHI_TEST_CACHE_DIR", "/tmp/michi-test-cache-svc")
        # Force reload of the module to pick up env var
        import importlib
        import library.cover_art_service
        importlib.reload(library.cover_art_service)
        cache_dir = library.cover_art_service.CACHE_DIR
        assert "/tmp/michi-test-cache-svc" in cache_dir, \
            f"CACHE_DIR should be under MICHI_TEST_CACHE_DIR, got {cache_dir}"
        assert "/.cache/michi/covers" not in cache_dir, \
            f"CACHE_DIR should not use legacy ~/.cache/michi, got {cache_dir}"

    def test_cache_dir_exists(self):
        """CACHE_DIR should be creatable."""
        import library.cover_art_service
        d = library.cover_art_service.CACHE_DIR
        assert "michi-music-player" in d or "michi" in d
        assert "covers" in d

    def test_find_cover_uses_xdg_cache(self, monkeypatch):
        """find_cover() should save embedded covers to XDG cache, not legacy."""
        monkeypatch.setenv("MICHI_TEST_CACHE_DIR", "/tmp/michi-test-cover-save")
        import importlib
        import library.cover_art_service
        importlib.reload(library.cover_art_service)
        # Verify the CACHE_DIR is correct
        cache_dir = library.cover_art_service.CACHE_DIR
        from core.paths import covers_cache_dir
        expected = covers_cache_dir()
        assert cache_dir == expected, \
            f"CACHE_DIR should match covers_cache_dir(), got {cache_dir} vs {expected}"
