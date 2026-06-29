"""Tests: SmartMix context — MIX_OPENED, scope=mix."""

from unittest.mock import MagicMock
from core.context.context_events import AppEvent


class TestSmartMixContext:

    def _make_win(self):
        ctx_svc = MagicMock()
        win = MagicMock()
        win._services.context_svc = ctx_svc
        win._ctx.context_svc = ctx_svc
        win._db.get_favorites.return_value = []
        win._db.get_play_history.return_value = []
        win._items_index = {}
        win._all_items = []
        return win, ctx_svc

    def test_show_favs_registers_mix_opened(self):
        win, ctx_svc = self._make_win()
        from ui.controllers.smart_mix_controller import SmartMixController
        ctrl = SmartMixController(win)
        ctrl.show_favs("favs")

        called = any(
            c[0][0] == AppEvent.MIX_OPENED
            for c in ctx_svc.record_event.call_args_list
        )
        assert called

    def test_show_recent_registers_mix_opened(self):
        win, ctx_svc = self._make_win()
        from ui.controllers.smart_mix_controller import SmartMixController
        ctrl = SmartMixController(win)
        ctrl.show_recent("recent")

        called = any(
            c[0][0] == AppEvent.MIX_OPENED
            for c in ctx_svc.record_event.call_args_list
        )
        assert called

    def test_mix_opened_includes_key(self):
        win, ctx_svc = self._make_win()
        from ui.controllers.smart_mix_controller import SmartMixController
        ctrl = SmartMixController(win)
        ctrl.show_favs("favs")

        for call in ctx_svc.record_event.call_args_list:
            if call[0][0] == AppEvent.MIX_OPENED:
                assert call[0][1]["key"] == "favs"
                return
