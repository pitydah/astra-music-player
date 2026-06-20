"""Tests for AppContext — dependency container for controllers."""
from unittest.mock import MagicMock
from core.app_context import AppContext


class TestAppContext:
    def test_exposes_dependencies(self):
        w = MagicMock()
        w._db = "mock_db"
        w._player = "mock_player"
        w._playback = "mock_playback"
        w._model = "mock_model"
        w._search_ctrl = "mock_search"

        ctx = AppContext(w)

        assert ctx.db == "mock_db"
        assert ctx.player == "mock_player"
        assert ctx.playback == "mock_playback"
        assert ctx.model == "mock_model"
        assert ctx.search == "mock_search"
        assert ctx.window is w

    def test_window_reference(self):
        w = MagicMock()
        ctx = AppContext(w)
        assert ctx.window is w
