"""Tests: selection scope — TRACK_SELECTED vs SELECTION_CHANGED."""

import os
from core.context import context_repository as repo
from core.context.context_service import ContextService
from core.context.context_events import AppEvent


class TestSelectionScope:

    def teardown_method(self):
        repo.close()
        repo.override_db_path(None)

    def _svc(self, tmp_path):
        repo.override_db_path(os.path.join(str(tmp_path), "ctx.sqlite"))
        return ContextService()

    def test_track_registers_track_selected(self, tmp_path):
        svc = self._svc(tmp_path)
        track = type("T", (), {"title": "S", "artist": "A", "name": "S"})()
        svc.update_selection(scope="track", track=track)
        events = svc.recent_events(5)
        assert any(e["event_type"] == AppEvent.TRACK_SELECTED for e in events)

    def test_album_registers_selection_changed(self, tmp_path):
        svc = self._svc(tmp_path)
        svc.update_selection(scope="album", album="A")
        events = svc.recent_events(5)
        assert any(e["event_type"] == AppEvent.SELECTION_CHANGED for e in events)

    def test_artist_registers_selection_changed(self, tmp_path):
        svc = self._svc(tmp_path)
        svc.update_selection(scope="artist", artist="A")
        events = svc.recent_events(5)
        assert any(e["event_type"] == AppEvent.SELECTION_CHANGED for e in events)

    def test_genre_registers_selection_changed(self, tmp_path):
        svc = self._svc(tmp_path)
        svc.update_selection(scope="genre", genre="Rock")
        events = svc.recent_events(5)
        assert any(e["event_type"] == AppEvent.SELECTION_CHANGED for e in events)

    def test_playlist_registers_selection_changed(self, tmp_path):
        svc = self._svc(tmp_path)
        svc.update_selection(scope="playlist", playlist_id=1, playlist_name="P")
        events = svc.recent_events(5)
        assert any(e["event_type"] == AppEvent.SELECTION_CHANGED for e in events)

    def test_mix_registers_selection_changed(self, tmp_path):
        svc = self._svc(tmp_path)
        svc.update_selection(scope="mix", mix_key="daily")
        events = svc.recent_events(5)
        assert any(e["event_type"] == AppEvent.SELECTION_CHANGED for e in events)

    def test_search_registers_selection_changed(self, tmp_path):
        svc = self._svc(tmp_path)
        svc.update_selection(scope="search", search_query="abc")
        events = svc.recent_events(5)
        assert any(e["event_type"] == AppEvent.SELECTION_CHANGED for e in events)

    def test_infers_track_from_track_param(self, tmp_path):
        svc = self._svc(tmp_path)
        track = type("T", (), {"title": "S", "artist": "A", "name": "S"})()
        svc.update_selection(track=track)
        events = svc.recent_events(5)
        assert any(e["event_type"] == AppEvent.TRACK_SELECTED for e in events)

    def test_infers_album_from_album_param(self, tmp_path):
        svc = self._svc(tmp_path)
        svc.update_selection(album="A")
        events = svc.recent_events(5)
        assert any(e["event_type"] == AppEvent.SELECTION_CHANGED for e in events)

    def test_infers_search_from_query_param(self, tmp_path):
        svc = self._svc(tmp_path)
        svc.update_selection(search_query="test")
        events = svc.recent_events(5)
        assert any(e["event_type"] == AppEvent.SELECTION_CHANGED for e in events)
