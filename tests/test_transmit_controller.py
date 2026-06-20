"""Tests for TransmitController."""
from ui.controllers.transmit_controller import TransmitController


class TestTransmitController:
    def test_activate_none(self, mock_window):
        ctrl = TransmitController(mock_window)
        ctrl.activate_transmit_device(None)
        mock_window._transmit_mgr.set_active.assert_called_with(None)
        mock_window._playback.set_output_device.assert_called_with(None)

    def test_devices_changed(self, mock_window):
        ctrl = TransmitController(mock_window)
        ctrl.on_transmit_devices_changed()
        # Should not crash — currently a no-op

    def test_active_changed_none(self, mock_window):
        mock_window._transmit_mgr.get_active.return_value = None
        ctrl = TransmitController(mock_window)
        ctrl.on_transmit_active_changed()
        mock_window._player_bar_ctrl.set_transmit_active.assert_called_with(False)
