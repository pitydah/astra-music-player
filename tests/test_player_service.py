"""Tests for PlayerService wrappers."""
import pytest
from unittest.mock import MagicMock


class TestPlayerService:
    @pytest.fixture
    def service(self):
        from audio.player_service import PlayerService
        engine = MagicMock()
        engine.state = MagicMock()
        return PlayerService(engine)

    def test_set_transmit_device(self, service):
        service.set_transmit_device(None)
        service._engine.set_transmit_device.assert_called_once_with(None)

    def test_get_transmit_device(self, service):
        service._engine.get_transmit_device.return_value = "dev1"
        result = service.get_transmit_device()
        assert result == "dev1"

    def test_set_eq_graphic(self, service):
        bands = [0.0] * 31
        service.set_eq_graphic(bands)
        service._engine.set_eq_graphic.assert_called_once_with(bands)

    def test_set_eq_parametric(self, service):
        bands = [{"type": "peaking", "frequency": 1000, "q": 0.7, "gain": 3.0}]
        service.set_eq_parametric(bands)
        service._engine.set_eq_parametric.assert_called_once_with(bands)

    def test_set_eq_bypass(self, service):
        service.set_eq_bypass(True)
        service._engine.set_eq_bypass.assert_called_once_with(True)

    def test_set_eq_preamp(self, service):
        service.set_eq_preamp(-2.0)
        service._engine.set_eq_preamp.assert_called_once_with(-2.0)

    def test_set_spectrum_enabled(self, service):
        service.set_spectrum_enabled(True)
        service._engine.set_spectrum_enabled.assert_called_once_with(True)

    def test_set_volume_emits_signal(self, service):
        """set_volume should emit volume_changed signal."""
        received = []
        service.volume_changed.connect(lambda v: received.append(v))
        service.set_volume(42)
        service._engine.set_volume.assert_called_once_with(42)
        assert received == [42]

    def test_set_volume_zero(self, service):
        received = []
        service.volume_changed.connect(lambda v: received.append(v))
        service.set_volume(0)
        assert received == [0]

    def test_play_calls_engine(self, service):
        service._engine.play = MagicMock()
        service.play("/tmp/test.mp3", "Title", "Artist")
        service._engine.play.assert_called_once_with("/tmp/test.mp3")

    def test_pause_resume(self, service):
        service._engine.pause = MagicMock()
        service._engine.resume = MagicMock()
        service.pause()
        service._engine.pause.assert_called_once()
        service.resume()
        service._engine.resume.assert_called_once()

    def test_toggle_calls_engine(self, service):
        service._engine.toggle = MagicMock()
        service.toggle()
        service._engine.toggle.assert_called_once()
