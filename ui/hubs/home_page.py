"""HomePage — clean dashboard: library status, assistant, last session, connections."""

from __future__ import annotations

import os

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QPushButton, QFileDialog,
)

from ui.central.central_styles import (
    glass_button_qss, card_title_qss,
)
from ui.effects.michi_glass import AcrylicGlassFrame


class HomePage(QWidget):
    navigation_requested = Signal(str)
    refresh_requested = Signal()
    add_music_requested = Signal(list)   # filepaths to add
    add_folder_requested = Signal(str)   # directory path to scan

    def __init__(self, db=None, playback=None, window=None,
                 parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("homePage")
        self._db = db
        self._playback = playback
        self._win = window
        self._build_ui()

    # ── Public API ──

    def refresh(self, items=None, servers=None, devices=None):
        """Update all sections with fresh data."""
        stats = self._get_stats()
        self._update_library_status(stats)
        self._update_assistant(stats, items or [])
        self._update_last_session()
        self._update_connections(servers or [], devices or [])

    # ── Stats ──

    def _get_stats(self) -> dict:
        stats = {"total_songs": 0, "total_artists": 0, "total_albums": 0,
                 "missing_metadata": 0}
        try:
            if self._db and hasattr(self._db, "get_dashboard_stats"):
                ds = self._db.get_dashboard_stats()
                stats.update(ds)
            elif self._db and hasattr(self._db, "get_stats"):
                st = self._db.get_stats()
                stats["total_songs"] = st.get("total", 0)
        except Exception:
            pass
        return stats

    # ── Build UI ──

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setObjectName("homeScroll")

        content = QWidget()
        content.setObjectName("homeContent")
        cl = QVBoxLayout(content)
        cl.setContentsMargins(40, 16, 40, 40)
        cl.setSpacing(20)

        # ── 1. Library Status ──
        self._lib_card = AcrylicGlassFrame("homeLibCard", hover_shine=True)
        self._lib_card.setObjectName("homeLibCard")
        lc = QVBoxLayout(self._lib_card)
        lc.setContentsMargins(24, 20, 24, 20)
        lc.setSpacing(4)
        self._lib_status_msg = QLabel("Tu biblioteca está lista")
        self._lib_status_msg.setObjectName("libStatusMsg")
        self._lib_status_msg.setStyleSheet(
            "QLabel { color: rgba(255,255,255,0.92); font-size: 15px;"
            "  font-weight: 600; background: transparent; border: none; }")
        lc.addWidget(self._lib_status_msg)
        self._lib_counts = QLabel("")
        self._lib_counts.setStyleSheet(
            "QLabel { color: rgba(255,255,255,0.56); font-size: 12px;"
            "  background: transparent; border: none; }")
        lc.addWidget(self._lib_counts)
        cl.addWidget(self._lib_card)

        # ── 1b. Añadir música ──
        self._add_music_card = AcrylicGlassFrame("homeAddMusicCard", hover_shine=True)
        amc = QVBoxLayout(self._add_music_card)
        amc.setContentsMargins(24, 16, 24, 16)
        amc.setSpacing(8)
        add_title = QLabel("Añadir música")
        add_title.setStyleSheet(card_title_qss())
        amc.addWidget(add_title)
        add_desc = QLabel("Agrega archivos o carpetas a tu biblioteca.")
        add_desc.setStyleSheet(
            "QLabel { color: rgba(255,255,255,0.56); font-size: 12px;"
            "  background: transparent; border: none; }")
        amc.addWidget(add_desc)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        self._add_folder_btn = QPushButton("📁 Añadir carpeta")
        self._add_folder_btn.setCursor(Qt.PointingHandCursor)
        self._add_folder_btn.setStyleSheet(glass_button_qss("secondary"))
        self._add_folder_btn.clicked.connect(self._on_add_folder_clicked)
        btn_row.addWidget(self._add_folder_btn)

        self._add_files_btn = QPushButton("🎵 Añadir archivos")
        self._add_files_btn.setCursor(Qt.PointingHandCursor)
        self._add_files_btn.setStyleSheet(glass_button_qss("accent"))
        self._add_files_btn.clicked.connect(self._on_add_files_clicked)
        btn_row.addWidget(self._add_files_btn)
        btn_row.addStretch()
        amc.addLayout(btn_row)

        # Preview section (hidden by default)
        self._preview_widget = QWidget()
        self._preview_widget.setVisible(False)
        self._preview_widget.setStyleSheet("background: transparent;")
        pw_layout = QVBoxLayout(self._preview_widget)
        pw_layout.setContentsMargins(0, 4, 0, 0)
        pw_layout.setSpacing(6)
        self._preview_label = QLabel("")
        self._preview_label.setWordWrap(True)
        self._preview_label.setStyleSheet(
            "QLabel { color: rgba(255,255,255,0.72); font-size: 12px;"
            "  background: transparent; border: none; }")
        pw_layout.addWidget(self._preview_label)

        preview_btn_row = QHBoxLayout()
        preview_btn_row.setSpacing(10)
        self._cancel_preview_btn = QPushButton("✕ Cancelar")
        self._cancel_preview_btn.setCursor(Qt.PointingHandCursor)
        self._cancel_preview_btn.setStyleSheet(glass_button_qss("ghost"))
        self._cancel_preview_btn.clicked.connect(self._clear_selection)
        preview_btn_row.addWidget(self._cancel_preview_btn)

        self._confirm_btn = QPushButton("✓ Importar")
        self._confirm_btn.setCursor(Qt.PointingHandCursor)
        self._confirm_btn.setStyleSheet(glass_button_qss("accent"))
        self._confirm_btn.clicked.connect(self._on_confirm)
        preview_btn_row.addWidget(self._confirm_btn)
        preview_btn_row.addStretch()
        pw_layout.addLayout(preview_btn_row)
        amc.addWidget(self._preview_widget)

        cl.addWidget(self._add_music_card)

        # ── 2. Michi Assistant ──
        self._asst_card = AcrylicGlassFrame("homeAsstCard", hover_shine=True)
        ac = QVBoxLayout(self._asst_card)
        ac.setContentsMargins(24, 16, 24, 16)
        ac.setSpacing(8)
        asst_title = QLabel("Michi Asistente")
        asst_title.setStyleSheet(card_title_qss())
        ac.addWidget(asst_title)
        self._asst_content = QVBoxLayout()
        self._asst_content.setSpacing(4)
        ac.addLayout(self._asst_content)
        cl.addWidget(self._asst_card)

        # ── 3. Last Session + Connections (side by side) ──
        bottom = QHBoxLayout()
        bottom.setSpacing(16)

        # Last session
        self._session_card = AcrylicGlassFrame("homeSessionCard", hover_shine=True)
        sc = QVBoxLayout(self._session_card)
        sc.setContentsMargins(20, 16, 20, 16)
        sc.setSpacing(8)
        session_title = QLabel("Última sesión")
        session_title.setStyleSheet(card_title_qss())
        sc.addWidget(session_title)
        self._session_track = QLabel("Sin reproducción reciente")
        self._session_track.setStyleSheet(
            "QLabel { color: rgba(255,255,255,0.56); font-size: 12px;"
            "  background: transparent; border: none; }")
        self._session_track.setWordWrap(True)
        sc.addWidget(self._session_track)
        sc.addStretch()
        self._continue_btn = QPushButton("Continuar")
        self._continue_btn.setObjectName("homeContinueBtn")
        self._continue_btn.setCursor(Qt.PointingHandCursor)
        self._continue_btn.setStyleSheet(glass_button_qss("ghost"))
        self._continue_btn.clicked.connect(
            lambda: self.navigation_requested.emit("playback_hub"))
        sc.addWidget(self._continue_btn)
        bottom.addWidget(self._session_card, 1)

        # Connections
        self._conn_card = AcrylicGlassFrame("homeConnCard", hover_shine=True)
        cc = QVBoxLayout(self._conn_card)
        cc.setContentsMargins(20, 16, 20, 16)
        cc.setSpacing(8)
        conn_title = QLabel("Conexiones")
        conn_title.setStyleSheet(card_title_qss())
        cc.addWidget(conn_title)
        self._conn_status = QLabel("")
        self._conn_status.setStyleSheet(
            "QLabel { color: rgba(255,255,255,0.56); font-size: 12px;"
            "  background: transparent; border: none; }")
        self._conn_status.setWordWrap(True)
        cc.addWidget(self._conn_status)
        cc.addStretch()
        self._conn_btn = QPushButton("Abrir Conexiones")
        self._conn_btn.setCursor(Qt.PointingHandCursor)
        self._conn_btn.setStyleSheet(glass_button_qss("ghost"))
        self._conn_btn.clicked.connect(
            lambda: self.navigation_requested.emit("connections_hub"))
        cc.addWidget(self._conn_btn)
        bottom.addWidget(self._conn_card, 1)

        cl.addLayout(bottom)
        cl.addStretch()

        scroll.setWidget(content)
        layout.addWidget(scroll)
        self._apply_qss()
        # State
        self._selected_files: list[str] = []

    # ── Add Music handlers ──

    def _on_add_folder_clicked(self):
        path = QFileDialog.getExistingDirectory(
            self, "Añadir carpeta", os.path.expanduser("~"))
        if path:
            self.add_folder_requested.emit(path)

    def _on_add_files_clicked(self):
        from library.library_db import AUDIO_EXTS
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Añadir archivos", os.path.expanduser("~"),
            f"Audio ({' '.join('*' + e for e in AUDIO_EXTS)})")
        if paths:
            self._selected_files = paths
            self._update_preview()
            self._preview_widget.setVisible(True)

    def _clear_selection(self):
        self._selected_files = []
        self._preview_widget.setVisible(False)

    def _on_confirm(self):
        if self._selected_files:
            self.add_music_requested.emit(self._selected_files)
            self._clear_selection()

    def _update_preview(self):
        n = len(self._selected_files)
        if n == 0:
            self._preview_label.setText("")
            self._confirm_btn.setText("✓ Importar")
            return
        lines = [f"{n} archivos seleccionados:"]
        for fp in self._selected_files[:3]:
            lines.append(f"  • {os.path.basename(fp)}")
        if n > 3:
            lines.append(f"  ... y {n - 3} más")
        self._preview_label.setText("\n".join(lines))
        self._confirm_btn.setText(f"✓ Importar {n} canciones")

    # ── Update sections ──

    def _update_library_status(self, stats: dict):
        songs = stats.get("total_songs", 0)
        if songs == 0:
            self._lib_status_msg.setText("Tu biblioteca necesita atención")
        else:
            self._lib_status_msg.setText("Tu biblioteca está lista")
        self._lib_counts.setText(
            f"{songs:,} canciones · {stats['total_albums']:,} álbumes"
            f" · {stats['total_artists']:,} artistas")

    def _update_assistant(self, stats: dict, _items=None):
        _clear_layout(self._asst_content)
        actions = []

        missing = stats.get("missing_metadata", 0)
        if missing > 0:
            actions.append((f"Completar metadatos de {missing} canciones",
                            "metadata_editor", "accent"))

        songs = stats.get("total_songs", 0)
        if songs == 0:
            actions.append(("Añadir carpeta de música",
                            "library", "primary"))

        if not actions:
            no_op = QLabel("No hay tareas importantes pendientes.")
            no_op.setStyleSheet(
                "QLabel { color: rgba(255,255,255,0.42); font-size: 12px;"
                "  background: transparent; border: none; padding: 4px 0; }")
            self._asst_content.addWidget(no_op)
        else:
            for text, target, kind in actions[:3]:
                btn = QPushButton(text)
                btn.setCursor(Qt.PointingHandCursor)
                btn.setStyleSheet(glass_button_qss(kind))
                btn.clicked.connect(
                    lambda c=None, t=target: self.navigation_requested.emit(t))
                self._asst_content.addWidget(btn)

    def _update_last_session(self):
        w = self._win or self.window()
        ref = getattr(w, '_current_ref', None) if w else None
        if ref and (ref.title or ref.uri):
            name = ref.title or os.path.basename(ref.uri)
            artist = getattr(ref, "artist", "") or ""
            text = f"{artist} — {name}" if artist else name
            self._session_track.setText(text)
            self._continue_btn.setVisible(True)
        else:
            self._session_track.setText("Sin reproducción reciente")
            self._continue_btn.setVisible(False)
        if hasattr(self, '_last_playback_state') and self._last_playback_state == "playing":
            self._continue_btn.setText("Continuar")

    def _update_connections(self, servers: list, devices: list):
        lines = []
        if servers:
            lines.append(f"Servidor: {servers[0].name if hasattr(servers[0], 'name') else 'Conectado'}")
        else:
            lines.append("Servidor: no configurado")
        if devices:
            lines.append(f"Dispositivos: {len(devices)} detectado(s)")
        else:
            lines.append("Dispositivos: no detectados")
        self._conn_status.setText("\n".join(lines))

    # ── QSS ──

    def _apply_qss(self):
        self.setStyleSheet("""
            QWidget#homePage { background: #090B11; }
            QScrollArea#homeScroll { background: transparent; border: none; }
            QWidget#homeContent { background: transparent; }
        """)


def _clear_layout(layout):
    while layout.count():
        item = layout.takeAt(0)
        if item.widget():
            item.widget().deleteLater()
        elif item.layout():
            _clear_layout(item.layout())

