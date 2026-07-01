"""Tests: FileActions — open_containing_folder."""

from unittest.mock import patch

from core.file_actions import open_containing_folder


class TestFileActions:

    def test_open_containing_folder_empty_path(self):
        assert open_containing_folder("") is False

    def test_open_containing_folder_nonexistent(self):
        assert open_containing_folder("/nonexistent/path/file.flac") is False

    @patch("core.file_actions.subprocess.Popen")
    @patch("core.file_actions.os.path.isdir", return_value=True)
    def test_open_containing_folder_valid(self, mock_isdir, mock_popen):
        result = open_containing_folder("/home/user/Music/song.flac")
        assert result is True
        mock_popen.assert_called_once_with(["xdg-open", "/home/user/Music"])
