"""Tests for AlbumCache — schema migration, get/save, raw_json, negative cache."""
import pytest
from integrations.artist_metadata.album_cache import AlbumCache, _ensure_db


@pytest.fixture
def cache(tmp_path, monkeypatch):
    """AlbumCache with isolated DB path."""
    db_dir = tmp_path / "album_cache_test"
    db_dir.mkdir()
    db_path = db_dir / "index.sqlite"
    monkeypatch.setattr("integrations.artist_metadata.album_cache.DB_PATH", str(db_path))
    monkeypatch.setattr("integrations.artist_metadata.album_cache.CACHE_DIR", str(db_dir))
    _ensure_db()
    return AlbumCache()


def test_save_and_get_metadata(cache):
    data = {"album": "Test Album", "artist": "Test Artist",
            "genre": "Rock", "year": "2020"}
    cache.save_metadata("test_key", data)
    result = cache.get_metadata("test_key")
    assert result is not None
    assert result["album"] == "Test Album"
    assert result["artist"] == "Test Artist"


def test_raw_json_fusion(cache):
    """Fields not in explicit columns are recoverable via raw_json."""
    data = {"album": "Fusion Test", "artist": "Fusion Artist",
            "cover_url": "https://example.com/cover.jpg",
            "custom_field": "extra_value"}
    cache.save_metadata("fusion_key", data)
    result = cache.get_metadata("fusion_key")
    assert result is not None
    assert result["cover_url"] == "https://example.com/cover.jpg"
    assert result["custom_field"] == "extra_value"


def test_schema_migration_adds_cover_fields(cache):
    """New columns should exist after _ensure_db runs."""
    cache.save_metadata("mig_test", {"album": "Migration Test"})
    result = cache.get_metadata("mig_test")
    assert result is not None
    # New schema columns should have default empty values
    assert "cover_url" in result
    assert "cover_path" in result
    assert "cover_source" in result
    assert "musicbrainz_release_group_mbid" in result


def test_stale_cache(cache, monkeypatch):
    import time as _time
    cache.save_metadata("stale_key", {"album": "Old", "updated_at": "2020-01-01 00:00:00"})
    # Override time to make it appear 31 days old
    future = _time.time() + 32 * 86400
    monkeypatch.setattr(_time, "time", lambda: future)
    assert cache.is_stale("stale_key", days=30)


def test_cache_handles_missing_db(tmp_path, monkeypatch):
    bad_path = tmp_path / "nonexistent" / "index.sqlite"
    monkeypatch.setattr("integrations.artist_metadata.album_cache.DB_PATH", str(bad_path))
    monkeypatch.setattr("integrations.artist_metadata.album_cache.CACHE_DIR", str(tmp_path / "nonexistent"))
    c = AlbumCache()
    result = c.get_metadata("nonexistent_key")
    assert result is None  # Should not crash


def test_negative_cache(cache):
    cache.cache_not_found("no_match_key")
    assert cache.is_negative("no_match_key")
    # Should NOT be stale immediately
    assert not cache.is_stale("no_match_key", days=30)


def test_clear_album(cache):
    cache.save_metadata("to_clear", {"album": "Clear Me"})
    assert cache.get_metadata("to_clear") is not None
    cache.clear_album("to_clear")
    assert cache.get_metadata("to_clear") is None
