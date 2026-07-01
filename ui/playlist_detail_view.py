"""Playlist Detail View — premium banner + track list with drag-drop and context menu."""
import os
from PySide6.QtCore import Qt, Signal, QMimeData
from PySide6.QtGui import QDrag
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QScrollArea, QMenu,
)

from ui.services.playlist_cover_service import get_playlist_cover
from ui.central.central_styles import glass_button_qss, menu_qss

_BG = "#090B11"
_TEXT = "rgba(255,255,255,0.95)"
_TEXT2 = "rgba(255,255,255,0.78)"
_TEXT3 = "rgba(255,255,255,0.62)"
_HOVER = "rgba(255,255,255,0.075)"
_SELECTED = "rgba(255,255,255,0.115)"


class PlaylistDetailView(QWidget):
    play_requested = Signal(int)
    queue_requested = Signal(int)
    edit_requested = Signal(int)
    export_requested = Signal(int)
    track_double_clicked = Signal(str)
    track_activated = Signal(int, str)
    order_changed = Signal(int, list)  # pid, ordered_filepaths
    track_context_action = Signal(str, int, str)  # action, pid, filepath

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {_BG};")
        self._playlist: dict | None = None
        self._tracks: list = []
        self._pid: int = 0
        self._dragged_row = -1

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QScrollArea.NoFrame)
        self._scroll.setStyleSheet(f"""
            QScrollArea {{ background: {_BG}; border: none; }}
            QScrollBar:vertical {{ background: rgba(255,255,255,0.02); width: 10px;
              margin: 4px; border-radius: 5px; }}
            QScrollBar::handle:vertical {{ background: rgba(255,255,255,0.16);
              min-height: 44px; border-radius: 5px; }}
            QScrollBar::handle:vertical:hover {{ background: rgba(255,255,255,0.28); }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        """)

        self._container = QWidget()
        self._container.setStyleSheet("background: transparent;")
        self._layout = QVBoxLayout(self._container)
        self._layout.setContentsMargins(28, 20, 28, 32)
        self._layout.setSpacing(20)

        self._scroll.setWidget(self._container)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self._scroll)

    def set_playlist(self, playlist: dict, tracks: list):
        sig = (playlist.get("id"), playlist.get("name"), playlist.get("cover_path"),
               len(tracks), sum(getattr(t, 'duration', 0) or 0 for t in tracks))
        if sig == getattr(self, '_last_detail_sig', None):
            return
        self._last_detail_sig = sig
        self._playlist = playlist
        self._tracks = tracks
        self._pid = playlist.get("id", 0)
        self._rebuild()

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item is None:
                continue
            w = item.widget()
            if w is not None:
                w.hide()
                w.setParent(None)
                w.deleteLater()
            elif item.layout() is not None:
                self._clear_layout(item.layout())

    def _rebuild(self):
        self._clear_layout(self._layout)

        if not self._playlist:
            return

        self._build_banner()
        self._build_actions()
        self._build_tracklist()
        self._build_inspector()
        self._layout.addStretch()

    def _build_banner(self):
        pl = self._playlist
        tracks = self._tracks

        banner = QHBoxLayout()
        banner.setSpacing(22)

        cover = get_playlist_cover(pl, tracks)
        cover_lbl = QLabel()
        cover_lbl.setFixedSize(170, 170)
        if cover and not cover.isNull():
            cover_lbl.setPixmap(cover.scaled(170, 170, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
        cover_lbl.setStyleSheet(
            "QLabel { background: rgba(255,255,255,0.04); border-radius: 16px; }")
        banner.addWidget(cover_lbl)

        info = QVBoxLayout()
        info.setSpacing(6)

        name = pl.get("name", "Sin nombre")
        name_lbl = QLabel(name)
        name_lbl.setStyleSheet(
            f"color: {_TEXT}; font-size: 26px; font-weight: 800; background: transparent;")
        name_lbl.setWordWrap(True)
        info.addWidget(name_lbl)

        desc = pl.get("description", "")
        if desc:
            desc_lbl = QLabel(desc)
            desc_lbl.setWordWrap(True)
            desc_lbl.setStyleSheet(
                f"color: {_TEXT2}; font-size: 13px; background: transparent;")
            info.addWidget(desc_lbl)

        count = len(tracks)
        dur = sum(getattr(t, 'duration', 0) or 0 for t in tracks)
        dur_str = ""
        if dur:
            s = int(dur)
            dur_str = f"{s // 3600} h {(s % 3600) // 60} min" if s >= 3600 else f"{s // 60} min"

        meta = f"{count} canciones"
        if dur_str:
            meta += f" · {dur_str}"
        meta_lbl = QLabel(meta)
        meta_lbl.setStyleSheet(
            f"color: {_TEXT3}; font-size: 13px; background: transparent;")
        info.addWidget(meta_lbl)

        info.addStretch()
        banner.addLayout(info)
        banner.addStretch()

        self._layout.addLayout(banner)

    def _build_actions(self):
        pid = self._playlist.get("id", 0)
        row = QHBoxLayout()
        row.setSpacing(10)

        for label, sig in [
            ("Reproducir", lambda: self.play_requested.emit(pid)),
            ("Añadir a cola", lambda: self.queue_requested.emit(pid)),
            ("Editar", lambda: self.edit_requested.emit(pid)),
            ("Exportar", lambda: self.export_requested.emit(pid)),
            ("Auditar", lambda: self._on_audit()),
        ]:
            btn = QPushButton(label)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(glass_button_qss("secondary"))
            btn.clicked.connect(sig)
            row.addWidget(btn)

        row.addStretch()
        self._layout.addLayout(row)

    def _on_audit(self):
        from library.playlists.playlist_audit import audit_playlist
        from library.playlists.playlist_store import PlaylistStore
        db = getattr(self, '_db_conn', None)
        if db:
            store = PlaylistStore(db)
            report = audit_playlist(store, self._pid)
            score = report.score
            issues = len(report.issues)
            from PySide6.QtWidgets import QMessageBox
            msg = f"Health Score: {score}/100\nIssues: {issues}"
            if issues:
                for iss in report.issues[:10]:
                    msg += f"\n• [{iss.severity}] {iss.message[:80]}"
            QMessageBox.information(self, "Auditoría de playlist", msg)

    def _build_tracklist(self):
        tracks = self._tracks
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["#", "Título", "Artista", "Duración", ""])
        table.setRowCount(len(tracks))
        table.verticalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setFrameShape(QFrame.NoFrame)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setAlternatingRowColors(True)
        table.horizontalHeader().setStretchLastSection(False)

        # Enable drag-and-drop for reordering
        table.setDragEnabled(True)
        table.setAcceptDrops(True)
        table.setDropIndicatorShown(True)
        table.setDragDropOverwriteMode(False)
        table.setDefaultDropAction(Qt.MoveAction)

        table.setStyleSheet(f"""
            QTableWidget {{
                background: transparent; color: {_TEXT}; border: none;
                gridline-color: transparent;
                selection-background-color: {_SELECTED}; selection-color: {_TEXT};
                alternate-background-color: rgba(255,255,255,0.015);
            }}
            QTableWidget::item {{ padding: 6px; color: {_TEXT2}; font-size: 12px; }}
            QTableWidget::item:hover {{ background: {_HOVER}; }}
            QHeaderView::section {{
                background: rgba(255,255,255,0.030); color: {_TEXT3};
                border: none; border-bottom: 1px solid rgba(255,255,255,0.02);
                padding: 8px 10px; font-size: 11px; font-weight: 600;
            }}
        """)

        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        table.setColumnWidth(0, 40)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        table.setColumnWidth(2, 180)
        table.setColumnWidth(3, 70)
        table.setColumnWidth(4, 30)

        for i, t in enumerate(tracks):
            fp = getattr(t, 'filepath', '')
            title = getattr(t, 'title', '') or (fp and os.path.basename(fp)) or "—"
            artist = getattr(t, 'artist', '') or "—"
            dur = getattr(t, 'duration', 0) or 0
            dur_s = f"{int(dur // 60)}:{int(dur % 60):02d}" if dur else "—"

            table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            item_title = QTableWidgetItem(title)
            item_title.setData(Qt.UserRole, fp)
            table.setItem(i, 1, item_title)
            table.setItem(i, 2, QTableWidgetItem(artist))
            table.setItem(i, 3, QTableWidgetItem(dur_s))
            table.setItem(i, 4, QTableWidgetItem("⋮⋮"))

        # Context menu on right-click
        table.setContextMenuPolicy(Qt.CustomContextMenu)
        table.customContextMenuRequested.connect(
            lambda pos: self._show_context_menu(table, pos))

        # Double-click to play
        table.itemDoubleClicked.connect(
            lambda item: (
                self.track_double_clicked.emit(
                    getattr(tracks[item.row()], 'filepath', '')),
                self.track_activated.emit(
                    item.row(), getattr(tracks[item.row()], 'filepath', ''))
            ))

        # Drag support
        table.startDrag = lambda drop_action: self._on_start_drag(table, drop_action)
        table.dragEnterEvent = lambda e: e.acceptProposedAction() if e.mimeData().hasText() else None
        table.dragMoveEvent = lambda e: e.acceptProposedAction()
        table.dropEvent = lambda e: self._on_drop(table, e)

        self._table = table
        self._layout.addWidget(table)

    def _on_start_drag(self, table, drop_action):
        row = table.currentRow()
        if row < 0:
            return
        self._dragged_row = row
        drag = QDrag(table)
        mime = QMimeData()
        mime.setText(str(row))
        drag.setMimeData(mime)
        drag.exec(Qt.MoveAction)

    def _on_drop(self, table, event):
        if self._dragged_row < 0:
            return
        row = table.rowAt(event.position().toPoint().y())
        if row < 0 or row == self._dragged_row:
            self._dragged_row = -1
            return
        tracks = self._tracks
        item = tracks.pop(self._dragged_row)
        tracks.insert(row, item)
        self._dragged_row = -1
        self._rebuild_tracklist_only()
        # Emit order change
        fps = [getattr(t, 'filepath', '') for t in tracks]
        self.order_changed.emit(self._pid, fps)

    def _rebuild_tracklist_only(self):
        """Rebuild only the table without affecting banner/actions."""
        if hasattr(self, '_table') and self._table:
            self._layout.removeWidget(self._table)
            self._table.deleteLater()
        self._build_tracklist()

    def _show_context_menu(self, table, pos):
        item = table.itemAt(pos)
        if item is None:
            return
        row = item.row()
        tracks = self._tracks
        if row < 0 or row >= len(tracks):
            return
        t = tracks[row]
        fp = getattr(t, 'filepath', '')
        menu = QMenu(self)
        menu.setStyleSheet(menu_qss())

        play_act = menu.addAction("▶ Reproducir")
        queue_act = menu.addAction("⊕ Añadir a cola")
        menu.addSeparator()
        remove_act = menu.addAction("✕ Quitar de playlist")
        menu.addSeparator()
        view_album_act = menu.addAction("📀 Ver álbum")
        view_artist_act = menu.addAction("🎤 Ver artista")
        locate_act = menu.addAction("📁 Localizar archivo")
        menu.addSeparator()
        metadata_act = menu.addAction("✎ Editar metadatos")
        analyze_act = menu.addAction("🔬 Analizar canción")
        menu.addSeparator()
        up_act = menu.addAction("↑ Subir")
        down_act = menu.addAction("↓ Bajar")
        top_act = menu.addAction("⏫ Mover al inicio")

        action = menu.exec(table.viewport().mapToGlobal(pos))
        if action == play_act:
            self.track_activated.emit(row, fp)
        elif action == queue_act:
            self.track_context_action.emit("queue", self._pid, fp)
        elif action == remove_act:
            self.track_context_action.emit("remove", self._pid, fp)
        elif action == view_album_act:
            self.track_context_action.emit("view_album", self._pid, fp)
        elif action == view_artist_act:
            self.track_context_action.emit("view_artist", self._pid, fp)
        elif action == locate_act:
            self.track_context_action.emit("locate", self._pid, fp)
        elif action == metadata_act:
            self.track_context_action.emit("metadata", self._pid, fp)
        elif action == analyze_act:
            self.track_context_action.emit("analyze", self._pid, fp)
        elif action == up_act:
            self._move_track(row, max(0, row - 1))
        elif action == down_act:
            self._move_track(row, min(len(tracks) - 1, row + 1))
        elif action == top_act:
            self._move_track(row, 0)

    def _move_track(self, from_idx, to_idx):
        tracks = self._tracks
        if from_idx == to_idx:
            return
        item = tracks.pop(from_idx)
        tracks.insert(to_idx, item)
        self._rebuild_tracklist_only()
        fps = [getattr(t, 'filepath', '') for t in tracks]
        self.order_changed.emit(self._pid, fps)

    def _build_inspector(self):
        tracks = self._tracks
        if not tracks:
            return
        artists = set()
        albums = set()
        genres = set()
        total_bitrate = 0
        bitrate_count = 0
        for t in tracks:
            if getattr(t, 'artist', ''):
                artists.add(t.artist)
            if getattr(t, 'album', ''):
                albums.add(t.album)
            if getattr(t, 'genre', ''):
                genres.add(t.genre)
            br = getattr(t, 'bitrate', 0) or 0
            if br:
                total_bitrate += br
                bitrate_count += 1

        stats = QFrame()
        stats.setStyleSheet("QFrame { background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.04); border-radius: 12px; }")
        sl = QHBoxLayout(stats)
        sl.setContentsMargins(16, 10, 16, 10)

        avg_br = total_bitrate // bitrate_count // 1000 if bitrate_count else 0
        for label, val in [
            ("Artistas", str(len(artists))),
            ("Álbumes", str(len(albums))),
            ("Géneros", str(len(genres))),
            ("Bitrate", f"{avg_br} kbps" if avg_br else "—"),
        ]:
            col = QVBoxLayout()
            col.setSpacing(0)
            v = QLabel(val)
            v.setStyleSheet(f"color: {_TEXT}; font-size: 18px; font-weight: 700; background: transparent;")
            lbl = QLabel(label)
            lbl.setStyleSheet(f"color: {_TEXT3}; font-size: 10px; background: transparent;")
            col.addWidget(v, alignment=Qt.AlignCenter)
            col.addWidget(lbl, alignment=Qt.AlignCenter)
            sl.addLayout(col)
            sl.addSpacing(20)

        sl.addStretch()
        self._layout.addWidget(stats)
