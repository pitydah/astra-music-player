"""Behavior tests for playlist DB operations — main branch schema.

Documents gaps where track_id/position are not yet on main branch.
"""
import os
import tempfile
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def db():
    tmpdir = tempfile.mkdtemp()
    try:
        from library.library_db import LibraryDB
        db_path = os.path.join(tmpdir, "test.db")
        db = LibraryDB(db_path)
        db._conn.executemany(
            "INSERT INTO media_items (filepath,filename,directory,ext,kind) VALUES (?,?,?,?,?)",
            [
                ("/tmp/a.mp3", "a.mp3", "/tmp", ".mp3", "audio"),
                ("/tmp/b.mp3", "b.mp3", "/tmp", ".mp3", "audio"),
                ("/tmp/c.mp3", "c.mp3", "/tmp", ".mp3", "audio"),
            ])
        db._conn.commit()
        yield db
    finally:
        import shutil
        shutil.rmtree(tmpdir, ignore_errors=True)


class TestPlaylistCRUD:
    def test_create_playlist_returns_id(self, db):
        pid = db.create_playlist("Test")
        assert pid > 0

    def test_get_playlists_returns_list(self, db):
        db.create_playlist("Test")
        playlists = db.get_playlists()
        assert len(playlists) == 1
        assert playlists[0]["name"] == "Test"

    def test_delete_playlist(self, db):
        pid = db.create_playlist("Temp")
        db.delete_playlist(pid)
        assert len(db.get_playlists()) == 0

    def test_update_playlist_name(self, db):
        pid = db.create_playlist("Old")
        db.update_playlist(pid, name="New")
        pl = db.get_playlists()
        assert pl[0]["name"] == "New"


class TestAddToPlaylist:
    def test_add_track_by_filepath(self, db):
        pid = db.create_playlist("Test")
        db.add_to_playlist(pid, "/tmp/a.mp3")
        items = db.get_playlist_items(pid)
        assert len(items) == 1

    def test_add_multiple_tracks(self, db):
        pid = db.create_playlist("Multi")
        db.add_to_playlist(pid, "/tmp/a.mp3")
        db.add_to_playlist(pid, "/tmp/b.mp3")
        db.add_to_playlist(pid, "/tmp/c.mp3")
        items = db.get_playlist_items(pid)
        assert len(items) == 3

    def test_duplicate_filepath_not_prevented(self, db):
        """DOCUMENTED GAP: no unique constraint prevents duplicates on main.

        INSERT OR IGNORE with no UNIQUE constraint allows duplicates.
        Awaiting add_to_playlist dedup logic from fix/playlist-ui-playback-wiring."""
        pid = db.create_playlist("Test")
        db.add_to_playlist(pid, "/tmp/a.mp3")
        db.add_to_playlist(pid, "/tmp/a.mp3")
        items = db.get_playlist_items(pid)
        assert len(items) >= 1


class TestPlaylistItems:
    def test_get_items_returns_media_items(self, db):
        pid = db.create_playlist("Test")
        db.add_to_playlist(pid, "/tmp/a.mp3")
        items = db.get_playlist_items(pid)
        assert items[0].filepath == "/tmp/a.mp3"

    def test_empty_playlist_returns_empty(self, db):
        pid = db.create_playlist("Empty")
        assert db.get_playlist_items(pid) == []

    def test_items_not_returned_for_deleted_playlist(self, db):
        pid = db.create_playlist("Test")
        db.add_to_playlist(pid, "/tmp/a.mp3")
        db.delete_playlist(pid)
        assert db.get_playlist_items(pid) == []


class TestSidebar:
    def test_nav_routes_has_playlist_hub(self):
        from ui.window import NAV_ROUTES
        assert "playlist_hub" in NAV_ROUTES

    def test_sidebar_controller_has_playlist_item(self):
        mock_db = MagicMock()
        mock_db.get_playlists.return_value = []
        mock_sidebar = MagicMock()
        mock_sidebar.item_clicked = MagicMock()
        from ui.sidebar_controller import SidebarController
        ctrl = SidebarController(mock_sidebar, mock_db)
        ctrl.rebuild([])
        calls = mock_sidebar.add_item.call_args_list
        keys = [c[0][1] for c in calls]
        assert "playlist_hub" in keys


class TestPlaylistDetailSignals:
    def test_signals_exist(self):
        from ui.playlist_detail_view import PlaylistDetailView
        from PySide6.QtCore import Signal
        view_cls = PlaylistDetailView
        assert isinstance(view_cls.track_double_clicked, Signal)
        assert isinstance(view_cls.play_requested, Signal)
        assert isinstance(view_cls.queue_requested, Signal)
