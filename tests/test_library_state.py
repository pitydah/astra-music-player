"""Tests for LibraryState."""
from library.library_state import (
    LibrarySection, LibraryViewMode, LibraryFilters, LibraryState,
    LibrarySelection, LibrarySort, valid_view_modes, default_view_mode,
    is_valid_view_mode, normalize_view_mode,
)


class TestLibrarySection:
    def test_values(self):
        assert LibrarySection.SONGS.value == "songs"
        assert LibrarySection.ALBUMS.value == "albums"


class TestLibraryViewMode:
    def test_values(self):
        assert LibraryViewMode.LIST.value == "list"
        assert LibraryViewMode.GRID.value == "grid"


class TestViewModeValidation:
    def test_valid_modes(self):
        assert is_valid_view_mode(LibrarySection.ALBUMS, LibraryViewMode.COVERFLOW)
        assert not is_valid_view_mode(LibrarySection.SONGS, LibraryViewMode.COVERFLOW)
        assert is_valid_view_mode(LibrarySection.FOLDERS, LibraryViewMode.TREE)

    def test_default_view_mode(self):
        assert default_view_mode(LibrarySection.SONGS) == LibraryViewMode.LIST
        assert default_view_mode(LibrarySection.FOLDERS) == LibraryViewMode.TREE

    def test_normalize_invalid_fallback(self):
        assert normalize_view_mode(LibrarySection.SONGS, "coverflow") == LibraryViewMode.LIST


class TestLibraryStateDefaults:
    def test_default_section(self):
        assert LibraryState().section == LibrarySection.SONGS

    def test_default_view_mode(self):
        assert LibraryState().view_mode == LibraryViewMode.LIST


class TestLibraryStatePostInit:
    def test_string_section(self):
        assert LibraryState(section="albums").section == LibrarySection.ALBUMS

    def test_invalid_section_fallback(self):
        assert LibraryState(section="bogus").section == LibrarySection.SONGS


class TestLibraryStateCopyWith:
    def test_copy_with_section(self):
        s = LibraryState(section="songs")
        s2 = s.copy_with(section="albums")
        assert s2.section == LibrarySection.ALBUMS
        assert s.section == LibrarySection.SONGS


class TestLibraryStateSerialization:
    def test_to_dict(self):
        s = LibraryState(section="albums", view_mode=LibraryViewMode.COVERFLOW)
        d = s.to_dict()
        assert d["section"] == "albums"
        assert d["view_mode"] == "coverflow"

    def test_from_dict_roundtrip(self):
        s = LibraryState(section="genres", view_mode="grid")
        s2 = LibraryState.from_dict(s.to_dict())
        assert s2.section == s.section
        assert s2.view_mode == s.view_mode

    def test_from_dict_filters(self):
        data = {"section": "songs", "view_mode": "list",
                "filters": {"query": "hello", "only_favorites": True},
                "sort": {}, "selection": {}, "scroll_position": 0, "source": "local"}
        s = LibraryState.from_dict(data)
        assert s.filters.query == "hello"
        assert s.filters.only_favorites is True


class TestBreadcrumb:
    def test_default(self):
        assert LibraryState().breadcrumb_parts() == ["Biblioteca", "Canciones"]

    def test_albums(self):
        parts = LibraryState(section="albums").breadcrumb_parts()
        assert "Álbumes" in parts
