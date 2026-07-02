"""Tests for LibraryStateController."""
from unittest.mock import MagicMock

import pytest
from PySide6.QtCore import QCoreApplication

from library.library_state import LibrarySection, LibraryViewMode
from ui.controllers.library_state_controller import LibraryStateController


@pytest.fixture
def app():
    return QCoreApplication.instance() or QCoreApplication([])


@pytest.fixture
def win():
    return MagicMock()


@pytest.fixture
def ctrl(app, win):
    return LibraryStateController(win)


class TestInitial:
    def test_defaults(self, ctrl):
        assert ctrl.state().section == LibrarySection.SONGS

    def test_set_section(self, ctrl):
        ctrl.set_section("albums")
        assert ctrl.state().section == LibrarySection.ALBUMS

    def test_set_section_folders_view(self, ctrl):
        ctrl.set_section("folders")
        assert ctrl.state().view_mode == LibraryViewMode.TREE

    def test_set_view_mode(self, ctrl):
        ctrl.set_section("albums")
        ctrl.set_view_mode("coverflow")
        assert ctrl.state().view_mode == LibraryViewMode.COVERFLOW

    def test_set_search(self, ctrl):
        ctrl.set_search("test")
        assert ctrl.state().filters.query == "test"

    def test_set_search_clears_selection(self, ctrl):
        ctrl.set_search("test")
        assert ctrl.state().selection.is_empty()

    def test_snapshot_roundtrip(self, ctrl):
        ctrl.set_section("artists")
        ctrl.set_search("hello")
        snap = ctrl.snapshot()
        restored = ctrl.__class__.__module__
        from library.library_state import LibraryState
        state = LibraryState.from_dict(snap)
        assert state.section == LibrarySection.ARTISTS

    def test_signals(self, ctrl):
        spy = MagicMock()
        ctrl.state_changed.connect(spy)
        ctrl.set_section("albums")
        spy.assert_called_once()

    def test_breadcrumb(self, ctrl):
        ctrl.set_section("albums")
        assert "Álbumes" in ctrl.breadcrumb_parts()
