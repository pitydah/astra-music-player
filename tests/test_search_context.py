"""Tests: Search context — SEARCH_PERFORMED, SEARCH_STARTED, SEARCH_CLEARED, SELECTION_CHANGED."""

import os
from unittest.mock import MagicMock
from core.context import context_repository as repo
from core.context.context_events import AppEvent


class TestSearchContext:

    def teardown_method(self):
        repo.close()
        repo.override_db_path(None)

    def _make_router(self, tmp_path, ctx_svc=None):
        repo.override_db_path(os.path.join(str(tmp_path), "ctx.sqlite"))
        if ctx_svc is None:
            ctx_svc = MagicMock()
        win = MagicMock()
        win._services.context_svc = ctx_svc
        win._ctx.context_svc = ctx_svc
        win._search_text = "test"
        win._current_section_key = "library"
        win._current_route_key = "library"
        from ui.routers.search_router import SearchRouter
        return SearchRouter(win), ctx_svc

    def test_on_results_registers_search_performed(self, tmp_path):
        router, ctx_svc = self._make_router(tmp_path)
        router._win._search_text = "test"
        router.on_results([MagicMock(), MagicMock()])

        called = any(
            c[0][0] == AppEvent.SEARCH_PERFORMED and c[0][1].get("result_count") == 2
            for c in ctx_svc.record_event.call_args_list
        )
        assert called

    def test_search_artist_records_performed_with_count(self, tmp_path):
        router, ctx_svc = self._make_router(tmp_path)
        router._win._current_route_key = "artists"
        router._win._artist_repo.current_key = None
        router._win._artist_repo.groups = []
        router._win._artist_grid = MagicMock()

        router.on_search("test")

        called = any(
            c[0][0] == AppEvent.SEARCH_PERFORMED
            for c in ctx_svc.record_event.call_args_list
        )
        assert called

    def test_search_albums_records_search_started(self, tmp_path):
        router, ctx_svc = self._make_router(tmp_path)
        router._win._current_route_key = "albums"
        router._win._lib_ctrl = MagicMock()

        router.on_search("test")

        called = any(
            c[0][0] == AppEvent.SEARCH_STARTED
            for c in ctx_svc.record_event.call_args_list
        )
        assert called

    def test_search_genres_records_search_started(self, tmp_path):
        router, ctx_svc = self._make_router(tmp_path)
        router._win._current_route_key = "genres"
        router._win._lib_ctrl = MagicMock()

        router.on_search("test")

        called = any(
            c[0][0] == AppEvent.SEARCH_STARTED
            for c in ctx_svc.record_event.call_args_list
        )
        assert called
        for call in ctx_svc.record_event.call_args_list:
            if call[0][0] == AppEvent.SEARCH_PERFORMED:
                assert False, "SEARCH_PERFORMED should not be emitted for genres"

    def test_search_folders_callable_count(self, tmp_path):
        router, ctx_svc = self._make_router(tmp_path)
        router._win._current_route_key = "folders"
        router._win._folder_browser = MagicMock()
        router._win._folder_browser.visible_count = lambda: 7

        router.on_search("test")

        called = any(
            c[0][0] == AppEvent.SEARCH_PERFORMED and c[0][1].get("result_count") == 7
            for c in ctx_svc.record_event.call_args_list
        )
        assert called

    def test_search_folders_non_callable_count(self, tmp_path):
        router, ctx_svc = self._make_router(tmp_path)
        router._win._current_route_key = "folders"
        router._win._folder_browser = MagicMock()
        router._win._folder_browser.visible_count = 7

        router.on_search("test")

        called_performed = any(
            c[0][0] == AppEvent.SEARCH_PERFORMED
            for c in ctx_svc.record_event.call_args_list
        )
        assert not called_performed
        called_started = any(
            c[0][0] == AppEvent.SEARCH_STARTED
            for c in ctx_svc.record_event.call_args_list
        )
        assert called_started

    def test_search_folders_exception_in_callable(self, tmp_path):
        router, ctx_svc = self._make_router(tmp_path)
        router._win._current_route_key = "folders"
        router._win._folder_browser = MagicMock()

        def broken():
            raise ValueError("boom")

        router._win._folder_browser.visible_count = broken

        router.on_search("test")

        called_performed = any(
            c[0][0] == AppEvent.SEARCH_PERFORMED
            for c in ctx_svc.record_event.call_args_list
        )
        assert not called_performed
        called_started = any(
            c[0][0] == AppEvent.SEARCH_STARTED
            for c in ctx_svc.record_event.call_args_list
        )
        assert called_started

    def test_search_folders_no_false_count(self, tmp_path):
        router, ctx_svc = self._make_router(tmp_path)
        router._win._current_route_key = "folders"
        router._win._folder_browser = MagicMock()
        router._win._folder_browser.visible_count = None

        router.on_search("test")

        for call in ctx_svc.record_event.call_args_list:
            if call[0][0] == AppEvent.SEARCH_PERFORMED:
                assert False, "SEARCH_PERFORMED should not be emitted for folders without visible_count"

    def test_empty_query_clears_search(self, tmp_path):
        router, ctx_svc = self._make_router(tmp_path)
        router._win._search_text = ""
        router._win._current_route_key = "library"
        router._win._lib_ctrl = MagicMock()

        router.on_search("")

        called = any(
            c[0][0] == AppEvent.SEARCH_CLEARED
            for c in ctx_svc.record_event.call_args_list
        )
        assert called

        state = repo.get_state("selection", {})
        query = state.get("search_query", "")
        assert query == ""

    def test_query_truncated(self, tmp_path):
        router, ctx_svc = self._make_router(tmp_path)
        long_query = "a" * 200
        router._win._search_text = long_query
        router._win._current_route_key = "library"
        router._win._lib_ctrl = MagicMock()

        router.on_search(long_query)
        state = repo.get_state("selection", {})
        query = state.get("search_query", "")
        assert len(query) <= 80
