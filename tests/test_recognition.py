"""Tests for recognition module — models, deduplication, provider_manager, base."""
import time
from unittest.mock import MagicMock, patch

import pytest
from recognition.base_recognizer import BaseRecognizer
from recognition.models import DetectedTrack
from recognition.deduplication import is_duplicate_detection
from recognition.null_recognizer import NullRecognizer
from recognition.provider_manager import ProviderManager


class TestDetectedTrack:
    def test_default_detected_at(self):
        t = DetectedTrack(title="Song", artist="Artist")
        assert t.detected_at > 0
        assert t.title == "Song"
        assert t.artist == "Artist"

    def test_to_dict(self):
        t = DetectedTrack(title="T", artist="A", album="Al", confidence=0.9,
                          provider="shazamio")
        d = t.to_dict()
        assert d["title"] == "T"
        assert d["artist"] == "A"
        assert d["album"] == "Al"
        assert d["confidence"] == 0.9
        assert d["provider"] == "shazamio"

    def test_to_dict_with_none(self):
        t = DetectedTrack(title="T", artist="A")
        d = t.to_dict()
        assert d["confidence"] is None
        assert d["isrc"] is None
        assert d["raw_json"] is None


class TestBaseRecognizer:
    def test_abstract_cannot_instantiate(self):
        with pytest.raises(TypeError):
            BaseRecognizer()  # noqa: E1120

    def test_concrete_implementation(self):
        class TestProvider(BaseRecognizer):
            name = "test"
            requires_api_key = False

            def identify(self, sample_bytes=None, source="", filepath=""):
                return {"title": "Test"}

        p = TestProvider()
        assert p.name == "test"
        assert p.is_configured() is True
        assert p.identify() == {"title": "Test"}
        ok, msg = p.test_connection()
        assert ok is True

    def test_requires_api_key(self):
        class KeyedProvider(BaseRecognizer):
            name = "keyed"
            requires_api_key = True

            def identify(self, sample_bytes=None, source="", filepath=""):
                return None

        p = KeyedProvider()
        assert p.is_configured() is False
        p.configure("abc123")
        assert p.is_configured() is True
        assert p.api_key == "abc123"


class TestNullRecognizer:
    def test_identify_returns_none(self):
        n = NullRecognizer()
        assert n.identify() is None
        assert n.identify(b"data") is None

    def test_is_configured(self):
        n = NullRecognizer()
        assert n.is_configured() is True

    def test_test_connection(self):
        n = NullRecognizer()
        ok, _ = n.test_connection()
        assert ok is True  # base class returns True by default


class TestDeduplication:
    def test_duplicate_found_via_db_method(self):
        db = MagicMock()
        db.find_detected_track_recent.return_value = {"title": "Song", "artist": "A"}
        assert is_duplicate_detection(db, "Song", "A") is True
        db.find_detected_track_recent.assert_called_once_with("Song", "A")

    def test_no_db_method_returns_false(self):
        db = MagicMock(spec=[])  # no methods
        assert is_duplicate_detection(db, "Song", "A") is False

    def test_duplicate_via_in_memory_fallback(self):
        db = MagicMock()
        db.find_detected_track_recent.return_value = None
        now = time.time()
        db.get_detected_tracks.return_value = [
            {"title": " Song ", "artist": " Artist ",
             "detected_at": now - 60},
            {"title": "Other", "artist": "Other", "detected_at": now - 60},
        ]
        assert is_duplicate_detection(db, "Song", "Artist") is True

    def test_not_duplicate_outside_window(self):
        db = MagicMock()
        db.find_detected_track_recent.return_value = None
        now = time.time()
        db.get_detected_tracks.return_value = [
            {"title": "Song", "artist": "Artist",
             "detected_at": now - 6000},
        ]
        assert is_duplicate_detection(db, "Song", "Artist") is False


class TestProviderManager:
    def test_initial_state(self):
        pm = ProviderManager()
        assert pm.current_provider == "none"
        assert isinstance(pm.recognizer, NullRecognizer)

    def test_select_null_provider(self):
        pm = ProviderManager()
        pm.select_provider("none")
        assert isinstance(pm.recognizer, NullRecognizer)

    def test_set_api_key_before_select(self):
        pm = ProviderManager()
        pm.set_api_key("audd", "test-key")
        assert pm._api_keys["audd"] == "test-key"

    def test_set_api_key_updates_current(self):
        pm = ProviderManager()
        pm.select_provider("none")
        pm.set_api_key("none", "")
        assert isinstance(pm.recognizer, NullRecognizer)

    def test_test_current_with_null(self):
        pm = ProviderManager()
        ok, _ = pm.test_current()
        assert ok is True  # NullRecognizer inherits base test_connection

    def test_select_unknown_provider_falls_back_to_null(self):
        pm = ProviderManager()
        pm.select_provider("nonexistent_provider")
        assert isinstance(pm.recognizer, NullRecognizer)

    def test_provider_changed_signal(self):
        pm = ProviderManager()
        results = []
        pm.provider_changed.connect(lambda n, c: results.append((n, c)))
        pm.select_provider("none")
        assert len(results) == 1
        assert results[0] == ("none", True)

    @patch("recognition.provider_manager._get_provider")
    def test_select_real_provider(self, mock_get):
        mock_provider = MagicMock(spec=BaseRecognizer)
        mock_provider.is_configured.return_value = True
        mock_provider.name = "mock_shazam"
        mock_get.return_value = mock_provider

        pm = ProviderManager()
        pm._api_keys["shazamio"] = "key"
        pm.select_provider("shazamio")

        mock_get.assert_called_once_with("shazamio")
        mock_provider.configure.assert_called_once_with("key")
        assert pm.recognizer is mock_provider
