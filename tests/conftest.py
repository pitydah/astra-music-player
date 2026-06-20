"""Shared fixtures for controller tests."""
from unittest.mock import MagicMock
import pytest
from ui.controllers.artist_repository import ArtistRepository


class MockWindow:
    """Simulates MainWindow attributes needed by controllers."""

    def __init__(self):
        self._db = MagicMock()
        self._playback = MagicMock()
        self._player = MagicMock()
        self._toast_svc = MagicMock()
        self._toast_svc.show = MagicMock()
        self._artist_repo = ArtistRepository()
        self._artist_grid = MagicMock()
        self._artist_detail = MagicMock()
        self._metadata_editor = MagicMock()
        self._section_title = MagicMock()
        self._section_subtitle = MagicMock()
        self._view_switcher = MagicMock()
        self._views = MagicMock()
        self._model = MagicMock()
        self._table = MagicMock()
        self._items_index = {}
        self._current_ref = None
        self._current_section_key = "library"
        self._mpris_ctrl = MagicMock()
        self._player_bar_ctrl = MagicMock()
        self._bg_theme = MagicMock()
        self._tray_ctrl = MagicMock()
        self._transmit_mgr = MagicMock()
        self._fade_content = MagicMock()
        self._configure_header_for_section = MagicMock()
        self._rebuild_sidebar = MagicMock()
        self._load_library = MagicMock()
        self._notify_track = MagicMock()
        self._on_sidebar_navigate = MagicMock()
        self._play_file = MagicMock()
        self._show_album_grid = MagicMock()
        self._expanded = None
        self._eq_dlg = None
        self._view_mode = "grid"
        self._search = MagicMock()
        self._nav = MagicMock()
        self.setWindowTitle = MagicMock()


@pytest.fixture
def mock_window():
    return MockWindow()
