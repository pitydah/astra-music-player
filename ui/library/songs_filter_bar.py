"""SongsFilterBar — filter bar for the premium songs view.

Emits filters_changed with a SongsFilterState.
"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QComboBox, QCheckBox, QLineEdit, QPushButton,
)

from library.songs_view_state import SongsFilterState


class SongsFilterBar(QWidget):
    filters_changed = Signal(SongsFilterState)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self._format_combo = QComboBox()
        self._format_combo.addItem("Formato", "")
        self._format_combo.currentIndexChanged.connect(self._emit)
        layout.addWidget(self._format_combo)

        self._quality_combo = QComboBox()
        self._quality_combo.addItem("Calidad", "")
        self._quality_combo.addItem("Hi-Res", "hires")
        self._quality_combo.addItem("Lossless", "lossless")
        self._quality_combo.addItem("Lossy", "lossy")
        self._quality_combo.addItem("DSD", "dsd")
        self._quality_combo.currentIndexChanged.connect(self._emit)
        layout.addWidget(self._quality_combo)

        self._genre_combo = QComboBox()
        self._genre_combo.addItem("Género", "")
        self._genre_combo.currentIndexChanged.connect(self._emit)
        layout.addWidget(self._genre_combo)

        self._year_min = QLineEdit()
        self._year_min.setPlaceholderText("Año min")
        self._year_min.setFixedWidth(55)
        self._year_min.textChanged.connect(self._emit)
        layout.addWidget(self._year_min)

        self._year_max = QLineEdit()
        self._year_max.setPlaceholderText("Año max")
        self._year_max.setFixedWidth(55)
        self._year_max.textChanged.connect(self._emit)
        layout.addWidget(self._year_max)

        self._sr_input = QLineEdit()
        self._sr_input.setPlaceholderText("SR min (kHz)")
        self._sr_input.setFixedWidth(80)
        self._sr_input.textChanged.connect(self._emit)
        layout.addWidget(self._sr_input)

        self._br_input = QLineEdit()
        self._br_input.setPlaceholderText("BR min (kbps)")
        self._br_input.setFixedWidth(80)
        self._br_input.textChanged.connect(self._emit)
        layout.addWidget(self._br_input)

        self._fav_check = QCheckBox("♥")
        self._fav_check.setToolTip("Solo favoritos")
        self._fav_check.stateChanged.connect(self._emit)
        layout.addWidget(self._fav_check)

        self._meta_check = QCheckBox("Metadata")
        self._meta_check.setToolTip("Sin metadata")
        self._meta_check.stateChanged.connect(self._emit)
        layout.addWidget(self._meta_check)

        self._missing_check = QCheckBox("Perdido")
        self._missing_check.setToolTip("Archivo perdido")
        self._missing_check.stateChanged.connect(self._emit)
        layout.addWidget(self._missing_check)

        reset_btn = QPushButton("✕")
        reset_btn.setToolTip("Limpiar filtros")
        reset_btn.setFixedWidth(24)
        reset_btn.clicked.connect(self.reset_filters)
        layout.addWidget(reset_btn)

        layout.addStretch()

    def set_formats(self, formats: list[str]):
        current = self._format_combo.currentData()
        self._format_combo.blockSignals(True)
        self._format_combo.clear()
        self._format_combo.addItem("Formato", "")
        for f in sorted(formats):
            self._format_combo.addItem(f, f)
        idx = self._format_combo.findData(current)
        if idx >= 0:
            self._format_combo.setCurrentIndex(idx)
        self._format_combo.blockSignals(False)

    def set_genres(self, genres: list[str]):
        current = self._genre_combo.currentData()
        self._genre_combo.blockSignals(True)
        self._genre_combo.clear()
        self._genre_combo.addItem("Género", "")
        for g in genres:
            self._genre_combo.addItem(g, g)
        idx = self._genre_combo.findData(current)
        if idx >= 0:
            self._genre_combo.setCurrentIndex(idx)
        self._genre_combo.blockSignals(False)

    def current_state(self) -> SongsFilterState:
        f = self._format_combo.currentData() or None
        q = self._quality_combo.currentData() or None
        g = self._genre_combo.currentData() or None

        def _int_or_none(text: str):
            import contextlib
            with contextlib.suppress(ValueError):
                return int(text.strip())
            return None

        return SongsFilterState(
            formats=frozenset({f}) if f else frozenset(),
            qualities=frozenset({q}) if q else frozenset(),
            genres=frozenset({g}) if g else frozenset(),
            year_min=_int_or_none(self._year_min.text()),
            year_max=_int_or_none(self._year_max.text()),
            sample_rate_min=_int_or_none(self._sr_input.text()),
            bitrate_min=_int_or_none(self._br_input.text()),
            only_favorites=bool(self._fav_check.isChecked()),
            only_missing_metadata=bool(self._meta_check.isChecked()),
            only_missing_file=bool(self._missing_check.isChecked()),
        )

    def reset_filters(self):
        self._format_combo.setCurrentIndex(0)
        self._quality_combo.setCurrentIndex(0)
        self._genre_combo.setCurrentIndex(0)
        self._year_min.clear()
        self._year_max.clear()
        self._sr_input.clear()
        self._br_input.clear()
        self._fav_check.setChecked(False)
        self._meta_check.setChecked(False)
        self._missing_check.setChecked(False)
        self._emit()

    def _emit(self, _=None):
        self.filters_changed.emit(self.current_state())
