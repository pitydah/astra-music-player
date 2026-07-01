"""Tests for section context providers — sanitized, no paths, no secrets."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from core.context.providers.library_context_provider import (
    LibraryContextProvider,
    _build_library_context,
)
from core.context.providers.audio_lab_context_provider import AudioLabContextProvider
from core.context.providers.mix_context_provider import MixContextProvider
from core.context.providers.playlist_context_provider import PlaylistContextProvider
from core.context.providers.playback_context_provider import PlaybackContextProvider
from core.context.providers.connections_context_provider import ConnectionsContextProvider
from core.context.providers.devices_context_provider import DevicesContextProvider
from core.context.providers.metadata_context_provider import MetadataContextProvider
from core.context.providers.home_audio_context_provider import HomeAudioContextProvider
from core.context.providers.settings_context_provider import SettingsContextProvider
from core.context.section_context_registry import SectionContextRegistry


def _mock_db():
    db = MagicMock()
    db.get_dashboard_stats.return_value = {
        "total_songs": 100, "total_artists": 10,
        "total_albums": 15, "missing_metadata": 5,
    }
    conn = MagicMock()
    conn.execute.return_value.fetchone.return_value = [5]
    conn.execute.return_value.fetchall.return_value = [(1,)]
    db.conn = conn
    return db


class TestSectionContextSanitized:
    def test_library_context_no_filepaths(self):
        ctx = _build_library_context(_mock_db())
        summary = ctx.get("summary", {})
        assert "filepath" not in str(ctx)
        assert "filepaths" not in str(ctx)
        assert summary.get("track_count") == 100

    def test_library_context_no_absolute_paths(self):
        ctx = _build_library_context(_mock_db())
        assert "/home" not in str(ctx)
        assert "C:\\" not in str(ctx)

    def test_library_context_limits_lists(self):
        ctx = _build_library_context(_mock_db())
        assert isinstance(ctx, dict)

    def test_library_allowed_actions(self):
        provider = LibraryContextProvider(_mock_db())
        actions = provider.get_allowed_actions()
        assert "search_library" in actions
        assert "find_metadata_gaps" in actions
        assert "draft_playlist" in actions

    def test_audio_lab_allowed_actions(self):
        provider = AudioLabContextProvider(_mock_db())
        actions = provider.get_allowed_actions()
        assert "explain_audio_format" in actions
        assert "recommend_conversion_profile" in actions

    def test_mix_allowed_actions(self):
        provider = MixContextProvider(_mock_db())
        actions = provider.get_allowed_actions()
        assert "create_smart_mix" in actions

    def test_playlist_allowed_actions(self):
        provider = PlaylistContextProvider(_mock_db())
        actions = provider.get_allowed_actions()
        assert "create_playlist" in actions

    def test_playback_allowed_actions(self):
        provider = PlaybackContextProvider(_mock_db())
        actions = provider.get_allowed_actions()
        assert "add_tracks_to_queue" in actions

    def test_connections_allowed_actions(self):
        provider = ConnectionsContextProvider(_mock_db())
        actions = provider.get_allowed_actions()
        assert "diagnose_ecosystem" in actions
        assert "diagnose_mobile_sync" in actions

    def test_devices_allowed_actions(self):
        provider = DevicesContextProvider(_mock_db())
        actions = provider.get_allowed_actions()
        assert "diagnose_mobile_sync" in actions

    def test_metadata_allowed_actions(self):
        provider = MetadataContextProvider(_mock_db())
        actions = provider.get_allowed_actions()
        assert "find_metadata_gaps" in actions

    def test_home_audio_allowed_actions(self):
        provider = HomeAudioContextProvider(_mock_db())
        actions = provider.get_allowed_actions()
        assert "diagnose_home_audio" in actions

    def test_settings_allowed_actions(self):
        provider = SettingsContextProvider(_mock_db())
        actions = provider.get_allowed_actions()
        assert "open_section" in actions


class TestSectionContextRegistry:
    def test_register_and_get(self):
        registry = SectionContextRegistry()
        provider = LibraryContextProvider(_mock_db())
        registry.register(provider)
        assert registry.get_provider("library_hub") is provider

    def test_get_context_no_provider(self):
        registry = SectionContextRegistry()
        ctx = registry.get_context("nonexistent")
        assert ctx == {"section": "nonexistent", "allowed_actions": []}

    def test_get_suggestions_no_provider(self):
        registry = SectionContextRegistry()
        assert registry.get_suggestions("nonexistent") == []

    def test_list_registered(self):
        registry = SectionContextRegistry()
        registry.register(LibraryContextProvider(_mock_db()))
        registry.register(AudioLabContextProvider(_mock_db()))
        keys = registry.list_registered()
        assert "library_hub" in keys
        assert "audio_lab" in keys


class TestContextSuggestions:
    def test_library_suggestions_missing_metadata(self):
        provider = LibraryContextProvider(_mock_db())
        suggestions = provider.get_suggestions()
        assert any(s.get("id") == "library_missing_metadata" for s in suggestions)

    def test_audio_lab_suggestions_conversion(self):
        provider = AudioLabContextProvider(_mock_db())
        suggestions = provider.get_suggestions()
        assert any(s.get("action") == "explain_audio_format" for s in suggestions)

    def test_playlist_suggestions(self):
        db = _mock_db()
        db.get_playlists.return_value = []
        provider = PlaylistContextProvider(db)
        suggestions = provider.get_suggestions()
        assert any(s.get("id") == "playlist_create_first" for s in suggestions)
