"""Metadata Editor — premium 3-panel tag editor with drag-drop, table, and inspector."""
from __future__ import annotations

import os
from pathlib import Path

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap, QColor, QIcon, QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QScrollArea,
    QLabel, QLineEdit, QPushButton, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QFileDialog, QMessageBox,
    QComboBox, QSpinBox, QTabWidget, QTextEdit, QListWidget, QListWidgetItem,
    QSizePolicy,
)

from metadata.tag_model import TrackTags
from metadata.tag_reader import read_tags, AUDIO_EXTS
from metadata.tag_writer import write_tags
from metadata import tag_actions as ta

# ═══════════════════════════════════════════════════════════
# Style tokens
# ═══════════════════════════════════════════════════════════
_BG = "#090B11"
_PANEL = "rgba(255,255,255,0.035)"
_PANEL_ALT = "rgba(255,255,255,0.050)"
_HOVER = "rgba(255,255,255,0.075)"
_SELECTED = "rgba(255,255,255,0.115)"
_BORDER = "rgba(255,255,255,0.08)"
_BORDER_HOVER = "rgba(255,255,255,0.14)"
_TEXT = "#FFFFFF"
_TEXT2 = "rgba(255,255,255,0.78)"
_TEXT3 = "rgba(255,255,255,0.62)"
_TEXT_DIM = "rgba(255,255,255,0.34)"


def _btn_css(extra: str = "") -> str:
    return f"""
        QPushButton {{
            background: rgba(255,255,255,0.060);
            color: {_TEXT};
            border: 1px solid {_BORDER_HOVER};
            border-radius: 12px;
            padding: 8px 13px;
            font-size: 12.5px; font-weight: 650;
            {extra}
        }}
        QPushButton:hover {{
            background: rgba(255,255,255,0.095);
            border: 1px solid rgba(255,255,255,0.15);
        }}
        QPushButton:pressed {{
            background: rgba(255,255,255,0.125);
        }}
        QPushButton:disabled {{
            color: {_TEXT_DIM};
            background: rgba(255,255,255,0.025);
        }}
    """


def _field_css() -> str:
    return f"""
        background: rgba(255,255,255,0.060);
        color: {_TEXT};
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 10px;
        padding: 7px 10px;
        selection-background-color: rgba(255,255,255,0.18);
        selection-color: {_TEXT};
    """


def _panel_frame(name: str) -> str:
    return f"""
        QFrame#{name} {{
            background: {_PANEL};
            border: 1px solid {_BORDER};
            border-radius: 18px;
        }}
    """


# ═══════════════════════════════════════════════════════════
# MetadataEditorWidget
# ═══════════════════════════════════════════════════════════

class MetadataEditorWidget(QWidget):
    files_saved = Signal(list)
    request_library_refresh = Signal()
    metadata_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("metadataEditor")
        self.setStyleSheet(f"QWidget#metadataEditor {{ background: {_BG}; }}")
        self.setAcceptDrops(True)

        self._tags: list[TrackTags] = []
        self._selected_indices: list[int] = []
        self._dirty_count = 0

        # ── Header ──
        header_row = QHBoxLayout()
        header_row.setContentsMargins(0, 0, 0, 0)
        header_row.setSpacing(10)

        icons_path = Path(__file__).parent.parent / "icons/sidebar/metadata.svg"
        if icons_path.exists():
            icon_lbl = QLabel()
            icon_pix = QPixmap(str(icons_path))
            if not icon_pix.isNull():
                icon_pix = icon_pix.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                icon_lbl.setPixmap(icon_pix)
            icon_lbl.setFixedSize(40, 40)
            icon_lbl.setStyleSheet("background: transparent; border: none;")
            header_row.addWidget(icon_lbl)

        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        t = QLabel("Editor de metadatos")
        t.setStyleSheet(f"color: {_TEXT}; font-size: 24px; font-weight: 800; background: transparent; border: none;")
        title_box.addWidget(t)
        s = QLabel("Limpia, completa y normaliza la información de tus archivos")
        s.setStyleSheet(f"color: {_TEXT2}; font-size: 13px; font-weight: 500; background: transparent; border: none;")
        title_box.addWidget(s)
        header_row.addLayout(title_box)
        header_row.addStretch()

        # Header buttons
        for label, slot in [
            ("Abrir archivos", self._open_files),
            ("Abrir carpeta", self._open_folder),
            ("Identificar", self._identify),
            ("Deshacer", self._revert_all),
            ("Guardar", self._save_all),
        ]:
            btn = QPushButton(label)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(_btn_css())
            btn.clicked.connect(slot)
            header_row.addWidget(btn)

        header = QFrame()
        header.setObjectName("metadataHero")
        header.setStyleSheet(
            f"QFrame#metadataHero {{"
            f"  background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            f"    stop:0 rgba(255,255,255,0.075),"
            f"    stop:0.55 rgba(255,255,255,0.040),"
            f"    stop:1 rgba(255,255,255,0.025));"
            f"  border: 1px solid rgba(255,255,255,0.085);"
            f"  border-radius: 22px; }}")
        header.setContentsMargins(24, 20, 24, 20)
        header.setLayout(header_row)

        # ── Splitter (3 panels) ──
        self._splitter = QSplitter(Qt.Horizontal)
        self._splitter.setStyleSheet(
            "QSplitter::handle { background: rgba(255,255,255,0.045); width: 1px; }")

        self._left_panel = self._build_left_panel()
        self._center_panel = self._build_center_panel()
        self._right_panel = self._build_right_panel()

        self._splitter.addWidget(self._left_panel)
        self._splitter.addWidget(self._center_panel)
        self._splitter.addWidget(self._right_panel)
        self._splitter.setSizes([200, 500, 320])

        # ── Main layout ──
        main = QVBoxLayout(self)
        main.setContentsMargins(24, 20, 24, 20)
        main.setSpacing(16)
        main.addWidget(header)
        main.addWidget(self._splitter)

        self._rebuild_navigator()

    # ── Left Panel: Navigator ──

    def _build_left_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("leftPanel")
        panel.setStyleSheet(_panel_frame("leftPanel"))
        v = QVBoxLayout(panel)
        v.setContentsMargins(10, 10, 10, 10)
        v.setSpacing(8)

        title = QLabel("Navegador")
        title.setStyleSheet(f"color: {_TEXT}; font-size: 14px; font-weight: 700; background: transparent; border: none;")
        v.addWidget(title)

        self._nav_list = QListWidget()
        self._nav_list.setStyleSheet(f"""
            QListWidget {{
                background: transparent; border: none; color: {_TEXT2}; font-size: 12px;
            }}
            QListWidget::item {{
                padding: 5px 8px; border-radius: 8px;
            }}
            QListWidget::item:hover {{
                background: {_HOVER}; color: {_TEXT};
            }}
            QListWidget::item:selected {{
                background: {_SELECTED}; color: {_TEXT};
            }}
        """)
        self._nav_list.currentRowChanged.connect(self._on_nav_filter)
        v.addWidget(self._nav_list)

        # Diagnostic stats
        self._diag_label = QLabel("0 archivos cargados")
        self._diag_label.setStyleSheet(f"color: {_TEXT3}; font-size: 10.5px; background: transparent; border: none;")
        v.addWidget(self._diag_label)

        return panel

    def _rebuild_navigator(self):
        self._nav_list.blockSignals(True)
        self._nav_list.clear()

        items = [
            (f"Archivos cargados ({len(self._tags)})", -1),
            (f"Modificados ({self._dirty_count})", "dirty"),
            (f"Sin carátula ({sum(1 for t in self._tags if not t.has_artwork)})", "no_cover"),
            (f"Sin artista ({sum(1 for t in self._tags if not t.artist)})", "no_artist"),
            (f"Sin álbum ({sum(1 for t in self._tags if not t.album)})", "no_album"),
            (f"Sin nº pista ({sum(1 for t in self._tags if not t.tracknumber)})", "no_track"),
            (f"Con error ({sum(1 for t in self._tags if t.error)})", "error"),
        ]

        for label, key in items:
            it = QListWidgetItem(label)
            it.setData(Qt.UserRole, key)
            self._nav_list.addItem(it)

        self._nav_list.setCurrentRow(0)
        self._nav_list.blockSignals(False)
        self._diag_label.setText(f"{len(self._tags)} archivos cargados · {self._dirty_count} modificados")

    def _on_nav_filter(self, row: int):
        item = self._nav_list.item(row)
        if not item:
            return
        key = item.data(Qt.UserRole)
        self._populate_table(key)

    # ── Center Panel: Table ──

    _TABLE_COLS = ["Estado", "Título", "Artista", "Álbum", "Nº", "Año", "Género", "Formato", "Ruta"]

    def _build_center_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("centerPanel")
        panel.setStyleSheet(_panel_frame("centerPanel"))
        v = QVBoxLayout(panel)
        v.setContentsMargins(8, 8, 8, 8)
        v.setSpacing(6)

        # Batch edit toolbar
        bar = QHBoxLayout()
        bar.setSpacing(6)

        for label, slot in [
            ("Aplicar a todos", self._batch_apply_all),
            ("Numerar pistas", self._batch_number_tracks),
            ("Normalizar", self._batch_normalize),
            ("Capitalizar", self._batch_title_case),
        ]:
            btn = QPushButton(label)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(_btn_css("padding: 5px 10px; font-size: 11px;"))
            btn.clicked.connect(slot)
            bar.addWidget(btn)
        bar.addStretch()
        v.addLayout(bar)

        self._table = QTableWidget()
        self._table.setColumnCount(len(self._TABLE_COLS))
        self._table.setHorizontalHeaderLabels(self._TABLE_COLS)
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self._table.setShowGrid(False)
        self._table.setFrameShape(QFrame.NoFrame)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)

        self._table.setStyleSheet(f"""
            QTableWidget {{
                background: transparent; color: {_TEXT}; border: none;
                gridline-color: rgba(255,255,255,0.045);
                selection-background-color: {_SELECTED};
                selection-color: {_TEXT};
                alternate-background-color: rgba(255,255,255,0.018);
            }}
            QTableWidget::item {{
                color: {_TEXT}; padding: 6px;
            }}
            QTableWidget::item:hover {{
                background: {_HOVER};
            }}
            QHeaderView::section {{
                background: rgba(255,255,255,0.045);
                color: rgba(255,255,255,0.86); border: none;
                border-bottom: 1px solid rgba(255,255,255,0.075);
                padding: 8px 10px; font-size: 11.5px; font-weight: 700;
            }}
        """)

        self._table.itemSelectionChanged.connect(self._on_table_selection)
        self._table.setColumnWidth(0, 80)
        self._table.setColumnWidth(1, 180)
        self._table.setColumnWidth(2, 160)
        self._table.setColumnWidth(3, 160)
        self._table.setColumnWidth(4, 55)
        self._table.setColumnWidth(5, 60)
        self._table.setColumnWidth(6, 100)
        self._table.setColumnWidth(7, 60)
        self._table.setColumnWidth(8, 200)
        v.addWidget(self._table)

        return panel

    def _populate_table(self, filter_key=None):
        self._table.setRowCount(0)

        rows = self._tags
        if filter_key == "dirty":
            rows = [t for t in rows if t.dirty]
        elif filter_key == "no_cover":
            rows = [t for t in rows if not t.has_artwork]
        elif filter_key == "no_artist":
            rows = [t for t in rows if not t.artist]
        elif filter_key == "no_album":
            rows = [t for t in rows if not t.album]
        elif filter_key == "no_track":
            rows = [t for t in rows if not t.tracknumber]
        elif filter_key == "error":
            rows = [t for t in rows if t.error]

        self._table.setRowCount(len(rows))
        for i, tag in enumerate(rows):
            status = "●" if tag.dirty else "○"
            if tag.error:
                status = "⚠"

            items = [
                QTableWidgetItem(status),
                QTableWidgetItem(tag.title),
                QTableWidgetItem(tag.artist),
                QTableWidgetItem(tag.album),
                QTableWidgetItem(tag.tracknumber),
                QTableWidgetItem(tag.date),
                QTableWidgetItem(tag.genre),
                QTableWidgetItem(tag.kind),
                QTableWidgetItem(os.path.basename(tag.filepath)),
            ]
            for j, it in enumerate(items):
                it.setFlags(it.flags() & ~Qt.ItemIsEditable)
                if tag.dirty:
                    it.setForeground(QColor("#FFE066"))
                elif tag.error:
                    it.setForeground(QColor("#FF6B6B"))
                it.setData(Qt.UserRole, i)
                self._table.setItem(i, j, it)

    def _on_table_selection(self):
        rows = set()
        for item in self._table.selectedItems():
            rows.add(item.row())
        self._selected_indices = sorted(rows)
        self._update_inspector()

    # ── Right Panel: Inspector ──

    def _build_right_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("rightPanel")
        panel.setStyleSheet(_panel_frame("rightPanel"))
        v = QVBoxLayout(panel)
        v.setContentsMargins(12, 10, 12, 10)
        v.setSpacing(8)

        title = QLabel("Inspector")
        title.setStyleSheet(f"color: {_TEXT}; font-size: 14px; font-weight: 700; background: transparent; border: none;")
        v.addWidget(title)

        # Artwork preview
        self._artwork_label = QLabel()
        self._artwork_label.setFixedSize(180, 180)
        self._artwork_label.setAlignment(Qt.AlignCenter)
        self._artwork_label.setStyleSheet(
            f"background: {_PANEL_ALT}; border: 1px solid {_BORDER}; border-radius: 12px;")
        v.addWidget(self._artwork_label, alignment=Qt.AlignCenter)

        art_btns = QHBoxLayout()
        art_btns.setSpacing(6)
        for label, slot in [
            ("Cambiar", self._change_artwork),
            ("Quitar", self._remove_artwork),
        ]:
            btn = QPushButton(label)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(_btn_css("padding: 4px 8px; font-size: 10.5px;"))
            btn.clicked.connect(slot)
            art_btns.addWidget(btn)
        v.addLayout(art_btns)

        # Tabs: Básico / Avanzado / Archivo
        self._tabs = QTabWidget()
        self._tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                background: transparent; border: none;
            }}
            QTabBar::tab {{
                background: transparent; color: {_TEXT3};
                padding: 6px 12px; font-size: 11.5px; border: none;
                border-bottom: 2px solid transparent;
            }}
            QTabBar::tab:selected {{
                color: {_TEXT}; border-bottom: 2px solid {_TEXT};
            }}
            QTabBar::tab:hover {{
                color: {_TEXT2};
            }}
        """)

        self._basic_tab = self._build_field_tab([
            ("Título", "title"), ("Artista", "artist"),
            ("Álbum", "album"), ("Artista del álbum", "albumartist"),
            ("Nº pista", "tracknumber"), ("Total pistas", "tracktotal"),
            ("Disco", "discnumber"), ("Total discos", "disctotal"),
            ("Año", "date"), ("Género", "genre"),
        ])
        self._advanced_tab = self._build_field_tab([
            ("Compositor", "composer"), ("Comentario", "comment"),
            ("Letra", "lyrics"), ("BPM", "bpm"), ("ISRC", "isrc"),
            ("MB Track ID", "musicbrainz_trackid"), ("MB Album ID", "musicbrainz_albumid"),
        ])

        self._file_tab = QWidget()
        fv = QVBoxLayout(self._file_tab)
        fv.setSpacing(4)
        self._file_info_label = QLabel()
        self._file_info_label.setWordWrap(True)
        self._file_info_label.setStyleSheet(f"color: {_TEXT3}; font-size: 11px; background: transparent; border: none;")
        fv.addWidget(self._file_info_label)
        fv.addStretch()

        self._tabs.addTab(self._basic_tab, "Básico")
        self._tabs.addTab(self._advanced_tab, "Avanzado")
        self._tabs.addTab(self._file_tab, "Archivo")

        v.addWidget(self._tabs)
        return panel

    def _build_field_tab(self, fields: list[tuple[str, str]]) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(4, 8, 4, 8)
        layout.setSpacing(6)

        self._field_widgets: dict[str, QLineEdit | QSpinBox] = {}

        for label, attr in fields:
            row = QHBoxLayout()
            row.setSpacing(6)
            lbl = QLabel(label)
            lbl.setFixedWidth(85)
            lbl.setStyleSheet(f"color: {_TEXT3}; font-size: 11px; background: transparent; border: none;")
            row.addWidget(lbl)

            if attr == "bpm":
                edit = QSpinBox()
                edit.setRange(0, 999)
                edit.setStyleSheet(_field_css())
                self._field_widgets[attr] = edit
                edit.valueChanged.connect(lambda v, a=attr: self._on_field_changed(a, str(v)))
            else:
                edit = QLineEdit()
                edit.setStyleSheet(_field_css())
                self._field_widgets[attr] = edit
                edit.textChanged.connect(lambda txt, a=attr: self._on_field_changed(a, txt))

            row.addWidget(edit)
            layout.addLayout(row)

        return w

    def _update_inspector(self):
        if not self._selected_indices:
            self._clear_inspector()
            return

        idx = self._selected_indices[0]
        if idx >= len(self._tags):
            self._clear_inspector()
            return

        tag = self._tags[idx]
        multi = len(self._selected_indices) > 1

        # Artwork
        if tag.artwork_data:
            pix = QPixmap()
            pix.loadFromData(tag.artwork_data)
            self._artwork_label.setPixmap(
                pix.scaled(176, 176, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self._artwork_label.clear()
            self._artwork_label.setText("Sin carátula")
            self._artwork_label.setStyleSheet(
                f"background: {_PANEL_ALT}; border: 1px solid {_BORDER}; border-radius: 12px;"
                f" color: {_TEXT_DIM}; font-size: 12px;")

        # Fields
        for attr, w in self._field_widgets.items():
            w.blockSignals(True)
            val = getattr(tag, attr, "")
            if isinstance(w, QSpinBox):
                w.setValue(int(val) if val.isdigit() else 0)
            else:
                if multi:
                    # Check if all selected share the same value
                    vals = set(getattr(self._tags[i], attr, "") for i in self._selected_indices if i < len(self._tags))
                    w.setText(val if len(vals) == 1 else "")
                    w.setPlaceholderText("— múltiples —" if len(vals) > 1 else "")
                else:
                    w.setText(val)
                    w.setPlaceholderText("")
            w.blockSignals(False)

        # File info
        info_lines = [
            f"Ruta: {tag.filepath}",
            f"Formato: {tag.kind}",
            f"Bitrate: {tag.bitrate} kbps" if tag.bitrate else "",
            f"Sample rate: {tag.sample_rate} Hz" if tag.sample_rate else "",
            f"Canales: {tag.channels}" if tag.channels else "",
            f"Duración: {int(tag.duration//60)}:{int(tag.duration%60):02d}",
            f"Tamaño: {tag.filesize / (1024*1024):.1f} MB",
        ]
        self._file_info_label.setText("\n".join(line for line in info_lines if line))

    def _clear_inspector(self):
        self._artwork_label.clear()
        self._artwork_label.setText("")
        self._artwork_label.setStyleSheet(
            f"background: {_PANEL_ALT}; border: 1px solid {_BORDER}; border-radius: 12px;")
        for w in self._field_widgets.values():
            w.blockSignals(True)
            if isinstance(w, QLineEdit):
                w.clear()
                w.setPlaceholderText("")
            else:
                w.setValue(0)
            w.blockSignals(False)
        self._file_info_label.setText("")

    def _on_field_changed(self, attr: str, value: str):
        if not self._selected_indices:
            return
        for idx in self._selected_indices:
            if idx < len(self._tags):
                tag = self._tags[idx]
                old = getattr(tag, attr, "")
                if old != value:
                    setattr(tag, attr, value)
                    tag.mark_dirty()
        self._dirty_count = sum(1 for t in self._tags if t.dirty)
        self._rebuild_navigator()
        self._populate_table()
        self.metadata_changed.emit()

    # ── Batch actions ──

    def _batch_apply_all(self):
        if not self._selected_indices:
            return
        from PySide6.QtWidgets import QInputDialog
        field, ok = QInputDialog.getItem(self, "Aplicar a todos", "Campo:",
                                         ["artist", "album", "albumartist", "genre", "date", "composer"], 0, False)
        if not ok:
            return
        value, ok = QInputDialog.getText(self, "Valor", f"Valor para '{field}':")
        if not ok:
            return
        items = [self._tags[i] for i in self._selected_indices if i < len(self._tags)]
        ta.apply_field_to_all(items, field, value)
        self._dirty_count = sum(1 for t in self._tags if t.dirty)
        self._rebuild_navigator()
        self._populate_table()
        self._update_inspector()

    def _batch_number_tracks(self):
        items = [self._tags[i] for i in self._selected_indices if i < len(self._tags)]
        ta.auto_number_tracks(items, 1)
        self._dirty_count = sum(1 for t in self._tags if t.dirty)
        self._rebuild_navigator()
        self._populate_table()
        self._update_inspector()

    def _batch_normalize(self):
        items = [self._tags[i] for i in self._selected_indices if i < len(self._tags)]
        ta.normalize_spaces(items)
        self._dirty_count = sum(1 for t in self._tags if t.dirty)
        self._rebuild_navigator()
        self._populate_table()
        self._update_inspector()

    def _batch_title_case(self):
        items = [self._tags[i] for i in self._selected_indices if i < len(self._tags)]
        ta.title_case(items)
        self._dirty_count = sum(1 for t in self._tags if t.dirty)
        self._rebuild_navigator()
        self._populate_table()
        self._update_inspector()

    # ── File loading ──

    def load_files(self, filepaths: list[str]):
        tags = []
        for fp in filepaths:
            ext = os.path.splitext(fp)[1].lower()
            if ext not in AUDIO_EXTS:
                continue
            tag = read_tags(fp)
            tags.append(tag)

        self._tags = tags
        self._dirty_count = 0
        self._selected_indices = []
        self._rebuild_navigator()
        self._populate_table()
        self._clear_inspector()

    def _open_files(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Abrir archivos de audio", "",
            "Audio (*.mp3 *.flac *.ogg *.opus *.m4a *.mp4 *.wav *.aiff *.aif *.ape);;Todos (*.*)")
        if paths:
            self.load_files(paths)

    def _open_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Abrir carpeta musical")
        if not folder:
            return
        files = []
        for root, _, fnames in os.walk(folder):
            for fn in fnames:
                if os.path.splitext(fn)[1].lower() in AUDIO_EXTS:
                    files.append(os.path.join(root, fn))

        if not files:
            QMessageBox.information(self, "Sin archivos",
                                    "No se encontraron archivos de audio en esta carpeta.")
            return

        reply = QMessageBox.question(
            self, "Cargar carpeta",
            f"Se encontraron {len(files)} archivos de audio.\n¿Cargarlos todos?",
            QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.load_files(files)

    # ── Save ──

    def _save_all(self):
        dirty = [t for t in self._tags if t.dirty]
        if not dirty:
            return

        reply = QMessageBox.question(
            self, "Guardar cambios",
            f"Se guardarán cambios en {len(dirty)} archivos.\n\n¿Confirmar?",
            QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return

        saved = []
        failed = 0
        for tag in dirty:
            if write_tags(tag):
                saved.append(tag.filepath)
            else:
                failed += 1

        self._dirty_count = sum(1 for t in self._tags if t.dirty)
        self._rebuild_navigator()
        self._populate_table()

        if saved:
            self.files_saved.emit(saved)
            self.request_library_refresh.emit()
        if failed:
            QMessageBox.warning(self, "Errores al guardar",
                                f"{failed} archivos no se pudieron guardar.")

    def _revert_all(self):
        for tag in self._tags:
            tag.revert()
        self._dirty_count = 0
        self._rebuild_navigator()
        self._populate_table()
        self._clear_inspector()

    # ── Identify stub ──

    def _identify(self):
        QMessageBox.information(self, "Identificar",
                                "Identificación online pendiente de implementar.\n\n"
                                "MusicBrainz y AcoustID estarán disponibles en una actualización futura.")

    # ── Artwork ──

    def _change_artwork(self):
        if not self._selected_indices:
            return
        path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar carátula", "",
            "Imágenes (*.jpg *.jpeg *.png *.webp);;Todos (*.*)")
        if not path:
            return
        try:
            with open(path, "rb") as f:
                data = f.read()
        except OSError:
            return
        for idx in self._selected_indices:
            if idx < len(self._tags):
                self._tags[idx].has_artwork = True
                self._tags[idx].artwork_mime = "image/jpeg" if path.lower().endswith((".jpg", ".jpeg")) else "image/png"
                self._tags[idx].artwork_data = data
                self._tags[idx].mark_dirty()
        self._dirty_count = sum(1 for t in self._tags if t.dirty)
        self._rebuild_navigator()
        self._populate_table()
        self._update_inspector()

    def _remove_artwork(self):
        if not self._selected_indices:
            return
        for idx in self._selected_indices:
            if idx < len(self._tags):
                self._tags[idx].has_artwork = False
                self._tags[idx].artwork_mime = ""
                self._tags[idx].artwork_data = None
                self._tags[idx].mark_dirty()
        self._dirty_count = sum(1 for t in self._tags if t.dirty)
        self._rebuild_navigator()
        self._populate_table()
        self._update_inspector()

    # ── Drag & Drop ──

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        paths = []
        for url in event.mimeData().urls():
            p = url.toLocalFile()
            if os.path.isfile(p):
                if os.path.splitext(p)[1].lower() in AUDIO_EXTS:
                    paths.append(p)
            elif os.path.isdir(p):
                for root, _, fnames in os.walk(p):
                    for fn in fnames:
                        if os.path.splitext(fn)[1].lower() in AUDIO_EXTS:
                            paths.append(os.path.join(root, fn))

        if paths:
            self.load_files(paths)
