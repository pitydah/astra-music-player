"""Tests: Playback context bridge — connect_context_events."""

from unittest.mock import MagicMock


class TestPlaybackContextBridge:

    def test_track_changed_registers_now_playing_and_played(self):
        ctx = MagicMock()
        pb = MagicMock()
        win = MagicMock()
        win._services = None
        win._ctx.context_svc = ctx

        from core.playback_controller import PlaybackController
        ctrl = PlaybackController(win)
        ctrl.connect_context_events(playback=pb, context_svc=ctx)

        # Simulate track_changed signal
        handler = pb.track_changed.connect.call_args[0][0]
        handler("Song", "Artist")

        ctx.record_now_playing_updated.assert_called_once_with(
            title="Song", artist="Artist")
        ctx.record_track_played_title_artist.assert_called_once_with(
            title="Song", artist="Artist")

    def test_state_changed_paused_registers_paused(self):
        ctx = MagicMock()
        pb = MagicMock()
        win = MagicMock()
        win._services = None
        win._ctx.context_svc = ctx

        from core.playback_controller import PlaybackController
        ctrl = PlaybackController(win)
        ctrl.connect_context_events(playback=pb, context_svc=ctx)

        handler = pb.state_changed.connect.call_args[0][0]
        handler("paused")
        ctx.record_track_paused.assert_called_once()

    def test_state_changed_not_paused_does_nothing(self):
        ctx = MagicMock()
        pb = MagicMock()
        win = MagicMock()
        win._services = None
        win._ctx.context_svc = ctx

        from core.playback_controller import PlaybackController
        ctrl = PlaybackController(win)
        ctrl.connect_context_events(playback=pb, context_svc=ctx)

        handler = pb.state_changed.connect.call_args[0][0]
        handler("playing")
        ctx.record_track_paused.assert_not_called()

    def test_queue_changed_records_updated(self):
        ctx = MagicMock()
        pb = MagicMock()
        win = MagicMock()
        win._services = None
        win._ctx.context_svc = ctx

        from core.playback_controller import PlaybackController
        ctrl = PlaybackController(win)
        ctrl.connect_context_events(playback=pb, context_svc=ctx)

        handler = pb.queue_changed.connect.call_args_list[0][0][0]
        handler([{"filepath": "/a.flac"}, {"filepath": "/b.flac"}])
        ctx.record_queue_updated.assert_called_once_with(count=2, source="playback")

    def test_no_crash_without_context_svc(self):
        pb = MagicMock()
        win = MagicMock()
        win._services = None

        from core.playback_controller import PlaybackController
        ctrl = PlaybackController(win)
        ctrl.connect_context_events(playback=pb, context_svc=None)

    def test_connect_context_events_is_idempotent(self):
        ctx = MagicMock()
        pb = MagicMock()
        win = MagicMock()
        win._services = None
        win._ctx.context_svc = ctx

        from core.playback_controller import PlaybackController
        ctrl = PlaybackController(win)

        ctrl.connect_context_events(playback=pb, context_svc=ctx)
        ctrl.connect_context_events(playback=pb, context_svc=ctx)

        # track_changed should have been connected only once
        assert pb.track_changed.connect.call_count == 1
        # state_changed only once
        assert pb.state_changed.connect.call_count == 1
        # queue_changed only once
        assert pb.queue_changed.connect.call_count == 1

    def test_initial_empty_queue_does_not_record_clear(self):
        ctx = MagicMock()
        pb = MagicMock()
        win = MagicMock()
        win._services = None
        win._ctx.context_svc = ctx

        from core.playback_controller import PlaybackController
        ctrl = PlaybackController(win)
        ctrl.connect_context_events(playback=pb, context_svc=ctx)

        handler = pb.queue_changed.connect.call_args[0][0]
        handler([])

        ctx.record_queue_cleared.assert_not_called()
        ctx.record_queue_updated.assert_not_called()

    def test_non_empty_queue_records_updated(self):
        ctx = MagicMock()
        pb = MagicMock()
        win = MagicMock()
        win._services = None
        win._ctx.context_svc = ctx

        from core.playback_controller import PlaybackController
        ctrl = PlaybackController(win)
        ctrl.connect_context_events(playback=pb, context_svc=ctx)

        handler = pb.queue_changed.connect.call_args[0][0]
        handler([{"filepath": "/a.flac"}])

        ctx.record_queue_updated.assert_called_once_with(count=1, source="playback")

    def test_active_to_empty_queue_records_only_cleared(self):
        ctx = MagicMock()
        pb = MagicMock()
        win = MagicMock()
        win._services = None
        win._ctx.context_svc = ctx

        from core.playback_controller import PlaybackController
        ctrl = PlaybackController(win)
        ctrl.connect_context_events(playback=pb, context_svc=ctx)

        handler = pb.queue_changed.connect.call_args[0][0]
        handler([{"filepath": "/a.flac"}])
        ctx.record_queue_updated.assert_called_once()

        ctx.reset_mock()
        handler([])

        ctx.record_queue_cleared.assert_called_once_with(reason="queue_empty")
        ctx.record_queue_updated.assert_not_called()
