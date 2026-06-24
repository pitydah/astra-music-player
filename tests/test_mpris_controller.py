"""Tests for MPRISController."""
import contextlib
from unittest.mock import MagicMock, patch
from ui.controllers.mpris_controller import MPRISController


class TestMPRISController:
    def test_init_no_dbus(self, mock_window):
        ctrl = MPRISController(mock_window)
        ctrl.init()
        assert ctrl.adapter is None
        assert not ctrl.is_active

    def test_update_metadata_no_adapter(self, mock_window):
        ctrl = MPRISController(mock_window)
        ctrl.update_metadata("Title", "Artist", "Album", 240)

    def test_raise_calls_window_methods(self):
        from adapters.mpris import MPRISObject
        w = MagicMock()
        mpris = MPRISObject(None, None)
        mpris.set_window(w)
        mpris.Raise()
        w.show.assert_called_once()
        w.raise_.assert_called_once()
        w.activateWindow.assert_called_once()

    def test_quit_calls_close(self):
        from adapters.mpris import MPRISObject
        w = MagicMock()
        mpris = MPRISObject(None, None)
        mpris.set_window(w)
        mpris.Quit()
        w.close.assert_called_once()

    def test_raise_no_window(self):
        from adapters.mpris import MPRISObject
        mpris = MPRISObject(None, None)
        mpris.Raise()  # must not crash

    def test_quit_no_window(self):
        from adapters.mpris import MPRISObject
        mpris = MPRISObject(None, None)
        mpris.Quit()  # must not crash

    def test_quit_fallback_to_qapp(self):
        from adapters.mpris import MPRISObject
        mpris = MPRISObject(None, None)
        w = MagicMock()
        del w.close  # make close not exist
        mpris.set_window(w)
        with patch("PySide6.QtWidgets.QApplication.quit") as mock_quit:
            mpris.Quit()
            mock_quit.assert_called_once()

    def test_adapter_accepts_window(self, mock_window):
        from adapters.mpris import MPRISAdapter
        adapter = MPRISAdapter(None, window=mock_window)
        assert adapter.player._window is mock_window

    def test_adapter_set_window(self):
        from adapters.mpris import MPRISAdapter
        import contextlib
        with contextlib.suppress(Exception):
            w = MagicMock()
            adapter = MPRISAdapter(None)
            adapter.set_window(w)
            assert adapter.player._window is w

    def test_controller_passes_window(self, mock_window):
        ctrl = MPRISController(mock_window)
        with contextlib.suppress(Exception):
            ctrl.init()
