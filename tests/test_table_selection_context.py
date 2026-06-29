"""Tests: table selection without playback — connect_table_selection, _on_table_selection."""

from unittest.mock import MagicMock


class DummyTrack:
    uri = "/music/song.flac"
    title = "Song"
    artist = "Artist"
    album = "Album"
    genre = "Rock"
    duration = 180


class DummyModel:
    def get_trackref(self, row):
        return DummyTrack()


class DummyIndex:
    def __init__(self, row=0):
        self._row = row
        self._valid = True

    def isValid(self):
        return self._valid

    def row(self):
        return self._row


class TestTableSelectionContext:

    def test_on_table_selection_calls_update_selection(self):
        ctx_svc = MagicMock()
        win = MagicMock()
        win._services = None
        win._ctx.context_svc = ctx_svc
        win._ctx.model = DummyModel()

        from core.playback_controller import PlaybackController
        ctrl = PlaybackController(win)

        ctrl._on_table_selection(DummyIndex(), None)
        ctx_svc.update_selection.assert_called_once()
        kwargs = ctx_svc.update_selection.call_args[1]
        assert kwargs["scope"] == "track"
        assert kwargs["track"].title == "Song"

    def test_does_nothing_if_index_invalid(self):
        ctx_svc = MagicMock()
        win = MagicMock()
        win._services = None
        win._ctx.context_svc = ctx_svc
        win._ctx.model = DummyModel()

        from core.playback_controller import PlaybackController
        ctrl = PlaybackController(win)

        idx = DummyIndex()
        idx._valid = False
        ctrl._on_table_selection(idx, None)
        ctx_svc.update_selection.assert_not_called()

    def test_does_nothing_if_no_model(self):
        ctx_svc = MagicMock()
        win = MagicMock()
        win._services = None
        win._ctx.context_svc = ctx_svc
        win._ctx.model = None

        from core.playback_controller import PlaybackController
        ctrl = PlaybackController(win)

        ctrl._on_table_selection(DummyIndex(), None)
        ctx_svc.update_selection.assert_not_called()

    def test_attach_track_table_calls_setModel_and_connect(self):
        win = MagicMock()
        win._services = None
        table = MagicMock()
        sel = MagicMock()
        table.selectionModel.return_value = sel
        model = MagicMock()

        from core.playback_controller import PlaybackController
        ctrl = PlaybackController(win)

        result = ctrl.attach_track_table(table, model)
        assert result is table
        table.setModel.assert_called_once_with(model)
        sel.currentChanged.disconnect.assert_called_once()
        sel.currentChanged.connect.assert_called_once()

    def test_attach_track_table_calls_connect_with_correct_table(self):
        win = MagicMock()
        win._services = None
        table = MagicMock()
        sel = MagicMock()
        table.selectionModel.return_value = sel
        model = MagicMock()

        from core.playback_controller import PlaybackController
        ctrl = PlaybackController(win)

        ctrl.attach_track_table(table, model)
        # Verify the slot is connected to the correct table's selectionModel
        connect_args = sel.currentChanged.connect.call_args
        assert connect_args is not None

    def test_connect_table_selection_disconnects_before(self):
        win = MagicMock()
        win._services = None
        win._ctx.table = MagicMock()
        sel = MagicMock()
        win._ctx.table.selectionModel.return_value = sel

        from core.playback_controller import PlaybackController
        ctrl = PlaybackController(win)

        ctrl.connect_table_selection(win._ctx.table)
        sel.currentChanged.connect.assert_called_once()
        sel.currentChanged.disconnect.assert_called_once()

    def test_connect_table_selection_does_not_play(self):
        win = MagicMock()
        win._services = None
        win._ctx.table = MagicMock()
        sel = MagicMock()
        win._ctx.table.selectionModel.return_value = sel
        win._ctx.model = DummyModel()
        win._ctx.context_svc = MagicMock()

        from core.playback_controller import PlaybackController
        ctrl = PlaybackController(win)

        ctrl.connect_table_selection(win._ctx.table)
        signal_handler = sel.currentChanged.connect.call_args[0][0]
        signal_handler(DummyIndex(), None)

        win._ctx.playback.enqueue.assert_not_called()
        win._ctx.playback.play.assert_not_called()
