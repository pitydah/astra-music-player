"""Tests for PlaylistController."""
from ui.controllers.playlist_controller import PlaylistController


class TestPlaylistController:
    def test_stub_action(self, mock_window):
        ctrl = PlaylistController(mock_window)
        ctrl.stub_action()
        mock_window._toast_svc.show.assert_called_once()

    def test_export_playlists(self, mock_window):
        ctrl = PlaylistController(mock_window)
        ctrl.export_playlists()
        mock_window._toast_svc.show.assert_called_once()

    def test_open_smart_playlist(self, mock_window):
        ctrl = PlaylistController(mock_window)
        ctrl.open_smart_playlist("favorites")
        mock_window._on_sidebar_navigate.assert_called_with("mix_favorites")

    def test_refresh_library(self, mock_window):
        ctrl = PlaylistController(mock_window)
        ctrl.refresh_library()
        mock_window._load_library.assert_called()
