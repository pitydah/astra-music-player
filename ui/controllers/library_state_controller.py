"""LibraryStateController — emits Signals on library state changes."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QObject, Signal

from library.library_state import (
    LibraryFilters, LibrarySection, LibrarySelection, LibrarySort,
    LibraryState, LibraryViewMode, default_view_mode, normalize_view_mode,
)

if TYPE_CHECKING:
    from ui.window import MainWindow


class LibraryStateController(QObject):
    state_changed = Signal(object)
    section_changed = Signal(object)
    view_mode_changed = Signal(object)
    search_changed = Signal(str)
    filters_changed = Signal(object)
    selection_changed = Signal(object)
    sort_changed = Signal(object)

    def __init__(self, window: MainWindow, parent=None):
        super().__init__(parent)
        self._win = window
        self._state = LibraryState()

    def state(self) -> LibraryState:
        return self._state

    def set_section(self, section: str | LibrarySection) -> None:
        if isinstance(section, str):
            try:
                section = LibrarySection(section)
            except ValueError:
                return
        if self._state.section == section:
            return
        self._state = self._state.copy_with(
            section=section, view_mode=default_view_mode(section),
            filters=LibraryFilters(), selection=LibrarySelection(), scroll_position=0)
        self.section_changed.emit(self._state.section)
        self.state_changed.emit(self._state)

    def set_view_mode(self, mode: str | LibraryViewMode) -> None:
        normalized = normalize_view_mode(self._state.section, mode)
        if self._state.view_mode == normalized:
            return
        self._state = self._state.copy_with(view_mode=normalized)
        self.view_mode_changed.emit(self._state.view_mode)
        self.state_changed.emit(self._state)

    def set_search(self, query: str) -> None:
        if self._state.filters.query == query:
            return
        new_filters = LibraryFilters(query=query)
        self._state = self._state.copy_with(filters=new_filters, selection=LibrarySelection())
        self.search_changed.emit(query)
        self.state_changed.emit(self._state)

    def set_filters(self, filters: LibraryFilters) -> None:
        if self._state.filters == filters:
            return
        self._state = self._state.copy_with(filters=filters)
        self.filters_changed.emit(self._state.filters)
        self.state_changed.emit(self._state)

    def set_selection(self, selection: LibrarySelection) -> None:
        if self._state.selection == selection:
            return
        self._state = self._state.copy_with(selection=selection)
        self.selection_changed.emit(self._state.selection)
        self.state_changed.emit(self._state)

    def set_sort(self, sort: LibrarySort) -> None:
        if self._state.sort == sort:
            return
        self._state = self._state.copy_with(sort=sort)
        self.sort_changed.emit(self._state.sort)
        self.state_changed.emit(self._state)

    def snapshot(self) -> dict[str, Any]:
        return self._state.to_dict()

    def restore(self, snapshot: dict[str, Any]) -> None:
        restored = LibraryState.from_dict(snapshot)
        self._state = restored
        self.section_changed.emit(self._state.section)
        self.view_mode_changed.emit(self._state.view_mode)
        self.filters_changed.emit(self._state.filters)
        self.selection_changed.emit(self._state.selection)
        self.sort_changed.emit(self._state.sort)
        self.state_changed.emit(self._state)

    def breadcrumb_parts(self) -> list[str]:
        return self._state.breadcrumb_parts()

    def context_payload(self) -> dict[str, Any]:
        return self._state.context_payload()
