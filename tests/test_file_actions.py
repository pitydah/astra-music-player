"""Tests for FileActions — requires QApplication via pytest-qt."""
from unittest.mock import MagicMock
from core.file_actions import FileActions


class MockFileActionsWindow:
    def __init__(self):
        self._db = MagicMock()
        self._playback = MagicMock()
        self._toast_svc = MagicMock()
        self._toast_svc.show = MagicMock()
        self._content = None  # QStackedWidget not needed for basic tests
        self._load_library = MagicMock()
        self._rebuild_sidebar = MagicMock()
        self._play_file = MagicMock()


def test_init(qtbot):
    w = MockFileActionsWindow()
    fa = FileActions(w)
    assert fa._db is w._db


def test_folder_create_playlist(qtbot):
    from unittest.mock import patch
    w = MockFileActionsWindow()
    fa = FileActions(w)
    w._db.create_playlist.return_value = 42
    with patch("core.file_actions.ToastNotification"):
        fa.folder_create_playlist("Test", ["/tmp/a.flac"])
    w._db.create_playlist.assert_called_with("Test")
    w._rebuild_sidebar.assert_called()
