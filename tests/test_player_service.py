"""Behavior tests for PlayerService — state, queue, EQ, transmit.

Tests against current main branch.
Documents gaps: volume_changed and play_queue not yet on main.
"""
from unittest.mock import MagicMock

import pytest

from audio.player_service import PlayerService


@pytest.fixture
def service():
    from audio.player import GStreamerEngine
    engine = MagicMock(spec=GStreamerEngine)
    engine.state = MagicMock()
    return PlayerService(engine)


class TestCorePlayback:
    def test_play_delegates(self, service):
        service.play("/tmp/a.mp3")
        service._engine.play.assert_called_once_with("/tmp/a.mp3")

    def test_pause_delegates(self, service):
        service.pause()
        service._engine.pause.assert_called_once()

    def test_toggle_delegates(self, service):
        service.toggle()
        service._engine.toggle.assert_called_once()

    def test_stop_delegates(self, service):
        service.stop()
        service._engine.stop.assert_called_once()

    def test_seek_delegates(self, service):
        service.seek(42.0)
        service._engine.seek.assert_called_once_with(42.0)

    def test_set_volume_delegates(self, service):
        service.set_volume(75)
        service._engine.set_volume.assert_called_once_with(75)


class TestQueue:
    def test_enqueue_delegates(self, service):
        service.enqueue(["/tmp/a.mp3"], play_now=False)
        service._engine.enqueue.assert_called_once_with(["/tmp/a.mp3"], False)

    def test_enqueue_empty_errors(self, service):
        spy = MagicMock()
        service.error_occurred.connect(spy)
        service.enqueue([])
        assert spy.called

    def test_clear_queue(self, service):
        service.clear_queue()
        service._engine.clear_queue.assert_called_once()

    def test_get_queue(self, service):
        service._engine.get_queue.return_value = [{"filepath": "/tmp/a.mp3"}]
        q = service.get_queue()
        assert q == [{"filepath": "/tmp/a.mp3"}]

    def test_play_next(self, service):
        service.play_next()
        service._engine.play_next.assert_called_once()

    def test_play_prev(self, service):
        service.play_prev()
        service._engine.play_prev.assert_called_once()


class TestEQ:
    def test_set_eq_graphic(self, service):
        bands = [0.0] * 31
        service.set_eq_graphic(bands)
        service._engine.set_eq_graphic.assert_called_once_with(bands)

    def test_set_eq_bypass(self, service):
        service.set_eq_bypass(True)
        service._engine.set_eq_bypass.assert_called_once_with(True)

    def test_set_eq_preamp(self, service):
        service.set_eq_preamp(-2.0)
        service._engine.set_eq_preamp.assert_called_once_with(-2.0)


class TestTransmit:
    def test_set_transmit_device(self, service):
        service.set_transmit_device(None)
        service._engine.set_transmit_device.assert_called_once_with(None)

    def test_get_transmit_device(self, service):
        service._engine.get_transmit_device.return_value = "dev1"
        assert service.get_transmit_device() == "dev1"


class TestVolumeChanged:
    """DOCUMENTED GAP: volume_changed signal does not exist on main.

    PlayerService.set_volume does not emit volume_changed.
    This is a known gap awaiting merge from fix/core-beta-blockers-mpris-api-init.
    """

    def test_set_volume_works_without_signal(self, service):
        """set_volume must work even without volume_changed signal."""
        service.set_volume(50)
        service._engine.set_volume.assert_called_once_with(50)


class TestPlayQueue:
    """DOCUMENTED GAP: play_queue does not exist on main.

    PlayerService lacks play_queue(filepaths, start_index).
    The enqueue method offers only append-or-replace with play_now=True.
    """

    def test_enqueue_play_now_replaces_queue(self, service):
        """enqueue with play_now=True replaces the queue and starts playback."""
        service.enqueue(["/tmp/a.mp3"], play_now=True)
        service._engine.enqueue.assert_called_once_with(["/tmp/a.mp3"], True)


class TestSignals:
    def test_signals_exist(self, service):
        from PySide6.QtCore import Signal
        assert isinstance(service.track_changed, Signal)
        assert isinstance(service.state_changed, Signal)
        assert isinstance(service.position_changed, Signal)
        assert isinstance(service.queue_changed, Signal)
        assert isinstance(service.finished, Signal)
        assert isinstance(service.error_occurred, Signal)
