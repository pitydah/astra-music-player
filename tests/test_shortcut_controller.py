"""Tests for ShortcutController."""
from ui.controllers.shortcut_controller import ShortcutController


class TestShortcutController:
    def test_init(self, mock_window):
        ctrl = ShortcutController(mock_window)
        assert ctrl._win is mock_window
