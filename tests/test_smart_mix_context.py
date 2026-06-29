"""Tests: SmartMix context — MIX_OPENED, scope=mix, connect_table_selection."""

from unittest.mock import MagicMock
from core.context.context_events import AppEvent


class DummyItem:
    filepath = "/music/a.flac"
    title = "Song"
    artist = "Artist"
    album = "Album"
    duration = 180
    year = 2000
    genre = "Rock"


def _make_win(ctx_svc=None):
    ctx = ctx_svc or MagicMock()
    win = MagicMock()
    win._services.context_svc = ctx
    win._ctx.context_svc = ctx
    win._ctx.context_svc = ctx
    win._db.get_favorites.return_value = []
    win._db.get_play_history.return_value = []
    win._items_index = {DummyItem.filepath: DummyItem()}
    win._all_items = [DummyItem()]
    win._playback_ctrl = MagicMock()
    win._section_title = MagicMock()
    win._model = MagicMock()
    win._count = MagicMock()
    win._fade_content = MagicMock()
    win._table = MagicMock()
    win._views = MagicMock()
    win._search = MagicMock()
    return win, ctx


class TestSmartMixContext:

    def test_show_smart_mix_registers_mix_opened(self, tmp_path):
        win, ctx = _make_win()
        audio_file = tmp_path / "a.flac"
        audio_file.write_text("")
        str_path = str(audio_file)
        item = DummyItem()
        item.filepath = str_path
        win._items_index[str_path] = item

        import library.smart_mixes as sm
        original = sm.get_daily_mix
        sm.get_daily_mix = lambda: [str_path]

        from ui.controllers.smart_mix_controller import SmartMixController
        try:
            ctrl = SmartMixController(win)
            ctrl.show_smart_mix("mix_daily")
            called = any(
                c[0][0] == AppEvent.MIX_OPENED and c[0][1].get("key") == "mix_daily"
                for c in ctx.record_event.call_args_list
            )
            assert called
            kwargs = ctx.update_selection.call_args[1]
            assert kwargs["scope"] == "mix"
            assert kwargs["mix_key"] == "mix_daily"
        finally:
            sm.get_daily_mix = original

    def test_show_smart_mix_reconnects_table_selection(self, tmp_path):
        win, ctx = _make_win()
        audio_file = tmp_path / "a.flac"
        audio_file.write_text("")
        str_path = str(audio_file)
        item = DummyItem()
        item.filepath = str_path
        win._items_index[str_path] = item

        import library.smart_mixes as sm
        original = sm.get_daily_mix
        sm.get_daily_mix = lambda: [str_path]

        from ui.controllers.smart_mix_controller import SmartMixController
        try:
            ctrl = SmartMixController(win)
            ctrl.show_smart_mix("mix_daily")
            win._playback_ctrl.connect_table_selection.assert_called()
        finally:
            sm.get_daily_mix = original

    def test_show_favs_registers_mix_opened(self, tmp_path):
        win, ctx = _make_win()
        audio_file = tmp_path / "fav.flac"
        audio_file.write_text("")
        fp = str(audio_file)
        win._db.get_favorites.return_value = [fp]
        win._items_index[fp] = DummyItem()

        from ui.controllers.smart_mix_controller import SmartMixController
        ctrl = SmartMixController(win)
        ctrl.show_favs("favs")

        called = any(
            c[0][0] == AppEvent.MIX_OPENED and c[0][1].get("key") == "favs"
            for c in ctx.record_event.call_args_list
        )
        assert called

    def test_show_favs_reconnects_table_selection(self, tmp_path):
        win, ctx = _make_win()
        audio_file = tmp_path / "fav.flac"
        audio_file.write_text("")
        fp = str(audio_file)
        win._db.get_favorites.return_value = [fp]
        win._items_index[fp] = DummyItem()

        from ui.controllers.smart_mix_controller import SmartMixController
        ctrl = SmartMixController(win)
        ctrl.show_favs("favs")
        win._playback_ctrl.connect_table_selection.assert_called()

    def test_show_recent_registers_mix_opened(self, tmp_path):
        win, ctx = _make_win()
        audio_file = tmp_path / "rec.flac"
        audio_file.write_text("")
        fp = str(audio_file)
        win._db.get_play_history.return_value = [{"track_id": fp}]
        win._items_index[fp] = DummyItem()

        from ui.controllers.smart_mix_controller import SmartMixController
        ctrl = SmartMixController(win)
        ctrl.show_recent("recent")

        called = any(
            c[0][0] == AppEvent.MIX_OPENED and c[0][1].get("key") == "recent"
            for c in ctx.record_event.call_args_list
        )
        assert called
