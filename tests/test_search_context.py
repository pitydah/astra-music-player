"""Tests: Search context — SEARCH_PERFORMED, SEARCH_CLEARED, scope=search."""

import os
from unittest.mock import MagicMock
from core.context import context_repository as repo
from core.context.context_events import AppEvent


class TestSearchContext:

    def teardown_method(self):
        repo.close()
        repo.override_db_path(None)

    def test_on_results_registers_search_performed(self, tmp_path):
        repo.override_db_path(os.path.join(str(tmp_path), "ctx.sqlite"))

        ctx_svc = MagicMock()
        win = MagicMock()
        win._services.context_svc = ctx_svc
        win._ctx.context_svc = ctx_svc
        win._search_text = "test"
        win._current_section_key = "library"

        from ui.routers.search_router import SearchRouter
        router = SearchRouter(win)
        router.on_results([MagicMock()])

        called = any(
            c[0][0] == AppEvent.SEARCH_PERFORMED
            for c in ctx_svc.record_event.call_args_list
        )
        assert called

    def test_search_performed_has_result_count(self, tmp_path):
        repo.override_db_path(os.path.join(str(tmp_path), "ctx.sqlite"))

        ctx_svc = MagicMock()
        win = MagicMock()
        win._services.context_svc = ctx_svc
        win._ctx.context_svc = ctx_svc
        win._search_text = "test"
        win._current_section_key = "library"

        from ui.routers.search_router import SearchRouter
        router = SearchRouter(win)
        router.on_results([MagicMock(), MagicMock()])

        for call in ctx_svc.record_event.call_args_list:
            if call[0][0] == AppEvent.SEARCH_PERFORMED:
                assert call[0][1]["result_count"] == 2
                return
        assert False, "SEARCH_PERFORMED not found"

    def test_search_artist_records_performed(self, tmp_path):
        repo.override_db_path(os.path.join(str(tmp_path), "ctx.sqlite"))

        ctx_svc = MagicMock()
        win = MagicMock()
        win._services.context_svc = ctx_svc
        win._ctx.context_svc = ctx_svc
        win._current_section_key = "library"
        win._current_route_key = "artists"
        win._search_text = "test_artist"
        win._artist_repo.current_key = None
        win._artist_repo.groups = []
        win._artist_grid = MagicMock()
        win._lib_ctrl = MagicMock()

        from ui.routers.search_router import SearchRouter
        router = SearchRouter(win)
        router.on_search("test")

        called = any(
            c[0][0] == AppEvent.SEARCH_PERFORMED
            for c in ctx_svc.record_event.call_args_list
        )
        assert called
