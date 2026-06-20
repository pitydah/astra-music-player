"""Tests for TrayController."""
from ui.controllers.tray_controller import TrayController


class TestTrayController:
    def test_init(self, mock_window):
        ctrl = TrayController(mock_window)
        assert ctrl._win is mock_window
        assert ctrl._icon is None
