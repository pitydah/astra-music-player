"""Tests: Playback mode context — shuffle, repeat."""

from unittest.mock import MagicMock


class TestPlaybackModeContext:

    def test_toggle_shuffle_records_mode_changed(self):
        ctx = MagicMock()
        pb = MagicMock()
        win = MagicMock()
        win._services = None
        win._ctx.context_svc = ctx
        win._playback = pb

        from core.playback_controller import PlaybackController
        ctrl = PlaybackController(win)

        pb.shuffle = True
        ctrl.toggle_shuffle_with_context()

        pb.toggle_shuffle.assert_called_once()
        ctx.record_playback_mode_changed.assert_called_once_with(shuffle=True)

    def test_toggle_repeat_records_mode_changed(self):
        ctx = MagicMock()
        pb = MagicMock()
        pb.toggle_repeat.return_value = "one"
        win = MagicMock()
        win._services = None
        win._ctx.context_svc = ctx
        win._playback = pb

        from core.playback_controller import PlaybackController
        ctrl = PlaybackController(win)

        ctrl.toggle_repeat_with_context()

        pb.toggle_repeat.assert_called_once()
        ctx.record_playback_mode_changed.assert_called_once_with(repeat="one")
