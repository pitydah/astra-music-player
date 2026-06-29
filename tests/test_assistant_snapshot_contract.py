"""Tests: Assistant snapshot contract — route, selection, capabilities, no filepaths."""

import os
from core.context import context_repository as repo
from core.context.context_service import ContextService


class TestAssistantSnapshotContract:

    def teardown_method(self):
        repo.close()
        repo.override_db_path(None)

    def _svc(self, tmp_path):
        repo.override_db_path(os.path.join(str(tmp_path), "ctx.sqlite"))
        return ContextService()

    def test_contains_route(self, tmp_path):
        svc = self._svc(tmp_path)
        snap = svc.get_assistant_snapshot()
        assert "route" in snap

    def test_contains_selection(self, tmp_path):
        svc = self._svc(tmp_path)
        snap = svc.get_assistant_snapshot()
        assert "selection" in snap

    def test_contains_playback(self, tmp_path):
        svc = self._svc(tmp_path)
        snap = svc.get_assistant_snapshot()
        assert "playback" in snap

    def test_contains_library_health(self, tmp_path):
        svc = self._svc(tmp_path)
        snap = svc.get_assistant_snapshot()
        assert "library_health" in snap

    def test_contains_capabilities(self, tmp_path):
        svc = self._svc(tmp_path)
        snap = svc.get_assistant_snapshot()
        assert "assistant_capabilities" in snap

    def test_contains_legacy_fields(self, tmp_path):
        svc = self._svc(tmp_path)
        snap = svc.get_assistant_snapshot()
        assert "selected_track" in snap
        assert "selected_album" in snap
        assert "selected_artist" in snap
        assert "current_section" in snap
        assert "selection_scope" in snap

    def test_no_absolute_paths(self, tmp_path):
        svc = self._svc(tmp_path)
        raw = str(svc.get_assistant_snapshot())
        assert "/home/" not in raw
        assert "/tmp/" not in raw
        assert "filepath" not in raw
        assert "uri" not in raw
