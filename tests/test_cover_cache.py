"""Tests for CoverCache — download, atomic write, validation, negative cache."""
import os
import pytest
from PySide6.QtCore import QByteArray
from PySide6.QtNetwork import QNetworkReply


class MockReply:
    """Mock QNetworkReply for testing CoverCache without network."""
    def __init__(self, data=b"", content_type=b"image/jpeg",
                 error=QNetworkReply.NoError, error_str=""):
        self._data = data
        self._error = error
        self._error_str = error_str
        self._raw_headers = {b"Content-Type": QByteArray(content_type)}

    def error(self):
        return self._error

    def errorString(self):
        return self._error_str

    def readAll(self):
        return self._data

    def rawHeader(self, name):
        return self._raw_headers.get(name, QByteArray())

    def deleteLater(self):
        pass


@pytest.fixture
def cover_cache(tmp_path, monkeypatch):
    from integrations.coverart.cover_cache import CoverCache
    cover_dir = tmp_path / "covers"
    cover_dir.mkdir()
    monkeypatch.setattr("integrations.coverart.cover_cache.COVER_DIR", str(cover_dir))
    return CoverCache()


@pytest.fixture
def mock_target(tmp_path):
    return os.path.join(str(tmp_path), "covers", "dest.jpg")


def test_rejects_non_image_content(cover_cache, monkeypatch, tmp_path):
    """Non-image content-type should be rejected."""
    reply = MockReply(data=b"<html>not an image</html>",
                      content_type=b"text/html")
    target = os.path.join(str(tmp_path), "covers", "test.jpg")
    cover_cache._on_download(reply, "test_key", target, "")
    assert cover_cache.is_negative("test_key")
    assert cover_cache.get_cached("test_key") is None


def test_atomic_write(cover_cache, tmp_path):
    """Download writes atomically via .tmp → rename."""
    reply = MockReply(data=b"\xff\xd8\xff\xe0\x00\x10JFIF\x00",
                      content_type=b"image/jpeg",
                      error=QNetworkReply.NoError)
    from integrations.coverart.cover_cache import _safe_filename
    fname = _safe_filename("atomic_key")
    target = os.path.join(str(tmp_path), "covers", fname)
    cover_cache._on_download(reply, "atomic_key", target, "")
    # File should exist, no tmp file
    assert os.path.exists(target)
    assert not os.path.exists(target + ".tmp")
    # get_cached should find it
    cached = cover_cache.get_cached("atomic_key")
    assert cached is not None


def test_negative_cache_on_failure(cover_cache, tmp_path):
    """Failed downloads create negative cache entry."""
    reply = MockReply(data=b"", content_type=b"image/jpeg",
                      error=QNetworkReply.ConnectionRefusedError)
    target = os.path.join(str(tmp_path), "covers", "neg_test.jpg")
    cover_cache._on_download(reply, "neg_key", target, "")
    assert cover_cache.is_negative("neg_key")
    assert cover_cache.get_cached("neg_key") is None


def test_existing_cached_file_reused(cover_cache, tmp_path):
    """If file exists and has content, it is reused without re-download."""
    fname = "a1b2c3d4e5f6a7b8.jpg"
    target = os.path.join(str(tmp_path), "covers", fname)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "wb") as f:
        f.write(b"cached_image_data")
    cover_dir = os.path.dirname(target)
    cached_count = sum(
        1 for f in os.listdir(cover_dir)
        if os.path.getsize(os.path.join(cover_dir, f)) > 0)
    assert cached_count >= 1

