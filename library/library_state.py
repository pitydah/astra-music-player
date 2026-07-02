"""LibraryState — canonical state contract for the Library subsystem.

Defines enums, dataclasses, and validation for all library UI state.
Single source of truth for section, view mode, filters, sort, and selection.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any


class LibrarySection(Enum):
    SONGS = "songs"
    ALBUMS = "albums"
    ARTISTS = "artists"
    GENRES = "genres"
    FOLDERS = "folders"


class LibraryViewMode(Enum):
    LIST = "list"
    GRID = "grid"
    COVERFLOW = "coverflow"
    TREE = "tree"


_VALID_VIEW_MODES: dict[LibrarySection, tuple[LibraryViewMode, ...]] = {
    LibrarySection.SONGS: (LibraryViewMode.LIST, LibraryViewMode.GRID),
    LibrarySection.ALBUMS: (LibraryViewMode.GRID, LibraryViewMode.COVERFLOW),
    LibrarySection.ARTISTS: (LibraryViewMode.GRID, LibraryViewMode.LIST),
    LibrarySection.GENRES: (LibraryViewMode.GRID, LibraryViewMode.LIST),
    LibrarySection.FOLDERS: (LibraryViewMode.TREE,),
}

_DEFAULT_VIEW_MODE: dict[LibrarySection, LibraryViewMode] = {
    LibrarySection.SONGS: LibraryViewMode.LIST,
    LibrarySection.ALBUMS: LibraryViewMode.GRID,
    LibrarySection.ARTISTS: LibraryViewMode.GRID,
    LibrarySection.GENRES: LibraryViewMode.GRID,
    LibrarySection.FOLDERS: LibraryViewMode.TREE,
}


def valid_view_modes(section: LibrarySection) -> tuple[LibraryViewMode, ...]:
    return _VALID_VIEW_MODES.get(section, (LibraryViewMode.LIST,))


def default_view_mode(section: LibrarySection) -> LibraryViewMode:
    return _DEFAULT_VIEW_MODE.get(section, LibraryViewMode.LIST)


def is_valid_view_mode(section: LibrarySection, mode: LibraryViewMode) -> bool:
    return mode in _VALID_VIEW_MODES.get(section, ())


def normalize_view_mode(section: LibrarySection, mode: str | LibraryViewMode) -> LibraryViewMode:
    if isinstance(mode, str):
        try:
            mode = LibraryViewMode(mode)
        except ValueError:
            return default_view_mode(section)
    if not is_valid_view_mode(section, mode):
        return default_view_mode(section)
    return mode


@dataclass
class LibrarySelection:
    scope: str = ""
    track_id: int | None = None
    filepath: str = ""
    album_key: str = ""
    artist_key: str = ""
    genre: str = ""
    folder_path: str = ""

    def is_empty(self) -> bool:
        return not any(
            [self.scope, self.track_id, self.filepath, self.album_key,
             self.artist_key, self.genre, self.folder_path]
        )


@dataclass
class LibraryFilters:
    query: str = ""
    formats: tuple[str, ...] = ()
    qualities: tuple[str, ...] = ()
    genres: tuple[str, ...] = ()
    year_min: int | None = None
    year_max: int | None = None
    bitrate_min: int | None = None
    sample_rate_min: int | None = None
    only_favorites: bool = False
    only_missing_metadata: bool = False
    only_missing_cover: bool = False
    only_missing_file: bool = False
    only_audio_lab_warning: bool = False

    def is_active(self) -> bool:
        return bool(
            self.query or self.formats or self.qualities or self.genres
            or self.year_min or self.year_max or self.bitrate_min
            or self.sample_rate_min or self.only_favorites
            or self.only_missing_metadata or self.only_missing_cover
            or self.only_missing_file or self.only_audio_lab_warning
        )


@dataclass
class LibrarySort:
    key: str = "title"
    ascending: bool = True


@dataclass
class LibraryState:
    section: LibrarySection = LibrarySection.SONGS
    view_mode: LibraryViewMode = LibraryViewMode.LIST
    filters: LibraryFilters = field(default_factory=LibraryFilters)
    sort: LibrarySort = field(default_factory=LibrarySort)
    selection: LibrarySelection = field(default_factory=LibrarySelection)
    scroll_position: int = 0
    source: str = "local"

    def __post_init__(self):
        if isinstance(self.section, str):
            try:
                self.section = LibrarySection(self.section)
            except ValueError:
                self.section = LibrarySection.SONGS
        if isinstance(self.view_mode, str):
            try:
                self.view_mode = LibraryViewMode(self.view_mode)
            except ValueError:
                self.view_mode = default_view_mode(self.section)
        self.view_mode = normalize_view_mode(self.section, self.view_mode)

    def copy_with(self, **kwargs) -> LibraryState:
        d = {
            "section": self.section,
            "view_mode": self.view_mode,
            "filters": self.filters,
            "sort": self.sort,
            "selection": self.selection,
            "scroll_position": self.scroll_position,
            "source": self.source,
        }
        d.update(kwargs)
        return LibraryState(**d)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["section"] = self.section.value
        d["view_mode"] = self.view_mode.value
        return d

    @staticmethod
    def from_dict(data: dict[str, Any]) -> LibraryState:
        clean = dict(data)
        section_str = clean.pop("section", "songs")
        view_mode_str = clean.pop("view_mode", "list")
        filters_data = clean.pop("filters", {})
        sort_data = clean.pop("sort", {})
        selection_data = clean.pop("selection", {})

        if isinstance(filters_data, dict):
            clean["filters"] = LibraryFilters(**filters_data)
        if isinstance(sort_data, dict):
            clean["sort"] = LibrarySort(**sort_data)
        if isinstance(selection_data, dict):
            clean["selection"] = LibrarySelection(**selection_data)

        state = LibraryState(**clean)
        try:
            state.section = LibrarySection(section_str)
        except ValueError:
            state.section = LibrarySection.SONGS
        try:
            state.view_mode = LibraryViewMode(view_mode_str)
        except ValueError:
            state.view_mode = default_view_mode(state.section)
        state.view_mode = normalize_view_mode(state.section, state.view_mode)
        return state

    def breadcrumb_parts(self) -> list[str]:
        parts = ["Biblioteca"]
        section_names = {
            LibrarySection.SONGS: "Canciones",
            LibrarySection.ALBUMS: "Álbumes",
            LibrarySection.ARTISTS: "Artistas",
            LibrarySection.GENRES: "Géneros",
            LibrarySection.FOLDERS: "Carpetas",
        }
        parts.append(section_names.get(self.section, self.section.value))
        if self.filters.query:
            parts.append(f'"{self.filters.query}"')
        if self.filters.only_favorites:
            parts.append("Favoritos")
        if self.selection.album_key:
            parts.append(self.selection.album_key)
        elif self.selection.artist_key:
            parts.append(self.selection.artist_key)
        elif self.selection.genre:
            parts.append(self.selection.genre)
        elif self.selection.folder_path:
            folder = self.selection.folder_path.rstrip("/").split("/")[-1]
            parts.append(folder)
        return parts

    def context_payload(self) -> dict[str, Any]:
        return {
            "section": self.section.value,
            "view_mode": self.view_mode.value,
            "search": self.filters.query,
            "filters_active": self.filters.is_active(),
            "selection_scope": self.selection.scope,
            "source": self.source,
        }
