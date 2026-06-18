"""MainWindow — 2 panels + nowplaying bar with library, EQ, and streaming."""

import os
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QStandardItemModel, QStandardItem, QBrush, QColor, QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QSplitter, QLabel,
    QFrame, QHBoxLayout, QLineEdit, QPushButton, QListWidget, QComboBox,
    QListWidgetItem, QStackedWidget, QTableView, QHeaderView,
    QAbstractItemView, QFileDialog, QProgressDialog,
    QInputDialog, QMessageBox, QMenu, QDialog, QFormLayout,
    QDialogButtonBox,
)

from sidebar_widget import SidebarWidget

from icons import get_icon, app_icon
from nowplaying_bar import NowPlayingBar
from player import PlayerEngine, PlaybackState
from audio_chain import DacConfig, get_quality_label
from library_db import (
    LibraryDB, DB_PATH, ScannerWorker, MediaItem,
    AUDIO_EXTS, ALL_EXTS, media_kind, get_mounted_devices, scan_device_music,
)
from transmit_manager import TransmitManager

from subsonic_client import (
    SubsonicClient, ServerConfig, load_servers, save_servers,
    SubsonicError, AuthError, ServerNotFoundError,
)
from server_dialog import ServerDialog
from remote_browser import RemoteBrowser
from coverflow import CoverFlowWidget
from album_art import load_covers_for_albums
from expanded_view import ExpandedNowPlaying
from radio_widget import RadioWidget


class MediaTableModel(QStandardItemModel):
    COL_TITLE = 0; COL_ARTIST = 1; COL_ALBUM = 2
    COL_YEAR = 3; COL_GENRE = 4; COL_DURATION = 5; COL_FILEPATH = 6

    def __init__(self, parent=None):
        super().__init__(0, 7, parent)
        self.setHorizontalHeaderLabels(
            ["Título", "Artista", "Álbum", "Año", "Género", "Duración", ""])

    def populate(self, items: list[MediaItem]):
        self.removeRows(0, self.rowCount())
        for item in items:
            t = QStandardItem(item.title or item.filename)
            t.setEditable(False); t.setToolTip(item.filepath)
            a = QStandardItem(item.artist); a.setEditable(False)
            al = QStandardItem(item.album); al.setEditable(False)
            y = QStandardItem(str(item.year) if item.year else ""); y.setEditable(False)
            y.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            y.setForeground(QBrush(QColor("#8e8e93")))
            g = QStandardItem(item.genre); g.setEditable(False)
            d = QStandardItem(item.duration_str); d.setEditable(False)
            d.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            d.setForeground(QBrush(QColor("#8e8e93")))
            fp = QStandardItem(item.filepath); fp.setEditable(False)
            self.appendRow([t, a, al, y, g, d, fp])


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Astra Music Player")
        self.resize(1100, 700)
        self.setMinimumSize(800, 500)
        self.setAcceptDrops(True)

        icon = app_icon()
        if icon:
            self.setWindowIcon(QIcon(icon))

        self._db = LibraryDB(DB_PATH)
        self._player = PlayerEngine(parent=self)
        self._player.set_volume(70)
        self._player.set_library_db(self._db)
        self._model = MediaTableModel(self)
        self._all_items: list[MediaItem] = []
        self._kind_filter: str | None = None
        self._search_text = ""
        self._current_playlist: int | None = None

        self._setup_menu()
        self._setup_ui()
        self._connect_signals()
        self._load_library()

        self._transmit_mgr = TransmitManager(self)
        self._transmit_mgr.device_changed.connect(self._on_transmit_devices_changed)
        self._transmit_mgr.active_changed.connect(self._on_transmit_active_changed)

    def _setup_menu(self):
        mb = self.menuBar()
        fm = mb.addMenu("&Archivo")
        fm.addAction("Abrir archivo...", self._open_file, "Ctrl+O")
        fm.addAction("Añadir carpeta...", self._add_folder, "Ctrl+D")
        fm.addSeparator()
        self._sync_action = fm.addAction("Activar sincronización Android")
        self._sync_action.setCheckable(True)
        self._sync_action.triggered.connect(self._toggle_sync)
        fm.addSeparator()
        fm.addAction("Salir", self.close, "Ctrl+Q")

        em = mb.addMenu("&Editar")
        em.addAction("Preferencias...", self._show_preferences, "Ctrl+P")

        tm = mb.addMenu("&Transmitir")
        tm.addAction("Añadir dispositivo...", self._add_transmit_device)
        tm.addAction("Administrar dispositivos...", self._manage_transmit_devices)

        hm = mb.addMenu("A&yuda")
        hm.addAction("Acerca de", self._show_about)

    def _toggle_sync(self):
        if not hasattr(self, '_sync_mgr'):
            from sync_manager import SyncManager
            self._sync_mgr = SyncManager(self._db, self)
            self._sync_mgr.sync_started.connect(
                lambda p: self._sync_action.setText(
                    f"✓ Sincronización activa (puerto {p})"))
            self._sync_mgr.sync_stopped.connect(
                lambda: self._sync_action.setText(
                    "Activar sincronización Android"))
            self._sync_mgr.error_occurred.connect(
                lambda m: print(f"Sync error: {m}"))
            self._sync_mgr.client_connected.connect(
                lambda d: print(f"Device connected: {d}"))

        if self._sync_mgr.is_active:
            self._sync_mgr.stop()
            self._sync_action.setChecked(False)
        else:
            self._sync_mgr.start()
            self._sync_action.setChecked(True)

    def _show_preferences(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Preferencias")
        dlg.setMinimumWidth(380)
        layout = QFormLayout(dlg)
        dev = QComboBox()
        dev.addItem("Default (PipeWire/PulseAudio)", "default")
        dev.addItem("hw:1,0 (ALC1220 Analog)", "hw:1,0")
        dev.addItem("hw:0,3 (HDMI)", "hw:0,3")
        layout.addRow("Audio:", dev)
        info = QLabel("Cambia tras reiniciar reproducción.")
        info.setStyleSheet("color: #8e8e93; font-size: 11px;")
        layout.addRow("", info)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(dlg.accept)
        btns.rejected.connect(dlg.reject)
        layout.addRow(btns)
        from theme import apply_dialog_shadow
        apply_dialog_shadow(dlg)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._player._dac.device = dev.currentData()

    def _show_about(self):
        QMessageBox.about(self, "Acerca de",
            "<h2>Astra Music Player</h2><p>Sincronización Android, ecualizador paramétrico, "
            "CoverFlow 3D, streaming Navidrome/Jellyfin.</p>"
            "<p>Python 3 · PySide6 · GStreamer</p>")

    def _setup_ui(self):
        # ── Sidebar ──
        self._sidebar = SidebarWidget()
        self._sidebar.setMaximumWidth(288)
        self._sidebar.setMinimumWidth(242)
        self._sidebar.setStyleSheet("""
            SidebarWidget {
                background: rgb(238, 241, 243);
                border-radius: 8px;
            }
        """)
        self._sidebar.item_clicked.connect(self._on_sidebar_click)
        self._sidebar.setContextMenuPolicy(Qt.CustomContextMenu)
        self._sidebar.customContextMenuRequested.connect(self._on_sidebar_menu)

        # ── Header ──
        header = QFrame()
        header.setStyleSheet("""
            QFrame { background: #f5f5f7; padding: 8px 14px;
                     border-bottom: 1px solid rgba(0,0,0,0.06); }
        """)
        hl = QHBoxLayout(header); hl.setContentsMargins(0, 0, 0, 0); hl.setSpacing(10)
        self._section_title = QLabel("Biblioteca")
        self._section_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1c1c1e;")
        self._search = QLineEdit()
        self._search.setPlaceholderText("Buscar..."); self._search.setClearButtonEnabled(True)
        self._search.setFixedWidth(200); self._search.textChanged.connect(self._on_search)
        self._count = QLabel("0 elementos")
        self._count.setStyleSheet("color: #8e8e93; font-size: 12px;")

        # View selector buttons (always visible)
        self._btn_list = QPushButton(QIcon(get_icon("list")), " Lista")
        self._btn_list.setFixedSize(64, 30)
        self._btn_list.clicked.connect(self._show_list_view)

        self._btn_grid = QPushButton(QIcon(get_icon("grid")), " Carátulas")
        self._btn_grid.setFixedSize(90, 30)
        self._btn_grid.clicked.connect(self._show_grid_view)

        self._btn_cf = QPushButton(QIcon(get_icon("coverflow")), " Coverflow")
        self._btn_cf.setFixedSize(100, 30)
        self._btn_cf.clicked.connect(self._show_coverflow_view)

        self._view_mode = "list"

        self._settings_btn = QPushButton(QIcon(get_icon("eq")), "")
        self._settings_btn.setFlat(True)
        self._settings_btn.setFixedSize(28, 28)
        self._settings_btn.setToolTip("Preferencias")
        self._settings_btn.clicked.connect(self._show_preferences)

        hl.addWidget(self._section_title)
        hl.addSpacing(16)
        hl.addWidget(self._btn_list)
        hl.addWidget(self._btn_grid)
        hl.addWidget(self._btn_cf)
        hl.addStretch()
        hl.addWidget(self._search)
        hl.addWidget(self._count)
        hl.addWidget(self._settings_btn)

        self._set_active_button(self._btn_list)

        # ── Table ──
        self._table = QTableView()
        self._table.setShowGrid(False)
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setFrameShape(QFrame.NoFrame)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self._table.verticalHeader().setVisible(False)
        self._table.setColumnHidden(6, True)
        self._table.doubleClicked.connect(self._on_table_dbl)

        placeholder = QLabel("Añade una carpeta o abre un archivo")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("color: #8e8e93; font-size: 16px;")

        # ── Expanded view (created on demand) ──
        self._expanded = None
        self._coverflow = None
        self._remote_browser = None
        self._remote_placeholder = QWidget()
        self._radio_widget = RadioWidget()
        self._radio_widget.station_selected.connect(self._play_radio)

        self._content = QStackedWidget()
        self._content.setMinimumHeight(200)
        self._content.addWidget(placeholder)      # 0: empty
        self._content.addWidget(self._table)      # 1: library table
        self._content.addWidget(self._remote_placeholder)  # 2: remote browser
        self._content.addWidget(placeholder)      # 3: coverflow placeholder
        self._content.addWidget(placeholder)      # 4: expanded view placeholder
        self._content.addWidget(self._radio_widget)  # 5: radio
        self._content.setCurrentIndex(0)

        # ── Content wrapper ──
        cw = QWidget()
        cl = QVBoxLayout(cw); cl.setContentsMargins(0, 0, 0, 0); cl.setSpacing(0)
        cl.addWidget(header); cl.addWidget(self._content)

        # ── Splitter ──
        sp = QSplitter(Qt.Horizontal); sp.addWidget(self._sidebar); sp.addWidget(cw)
        sp.setStretchFactor(0, 1); sp.setStretchFactor(1, 3); sp.setSizes([220, 880])
        sp.setStyleSheet("QSplitter::handle { background: rgba(0,0,0,0.06); width: 1px; }")

        # ── NowPlaying bar ──
        self._player_bar = NowPlayingBar()

        bar_wrapper = QWidget()
        wl = QHBoxLayout(bar_wrapper)
        wl.setContentsMargins(24, 0, 24, 12)
        wl.addWidget(self._player_bar)

        cent = QWidget()
        layout = QVBoxLayout(cent); layout.setContentsMargins(0, 0, 0, 0); layout.setSpacing(0)
        layout.addWidget(sp, stretch=1)
        layout.addWidget(bar_wrapper, stretch=0)
        self.setCentralWidget(cent)

    def _connect_signals(self):
        pb = self._player_bar
        self._player.position_changed.connect(pb.set_position)
        self._player.duration_changed.connect(pb.set_duration)
        self._player.state_changed.connect(self._on_state)
        self._player.error_occurred.connect(lambda m: print(f"Error: {m}"))
        pb.play_clicked.connect(self._player.toggle)
        pb.shuffle_clicked.connect(self._player.toggle_shuffle)
        pb.repeat_clicked.connect(self._player.toggle_repeat)
        pb.seek_requested.connect(self._player.seek)
        pb.volume_changed.connect(self._player.set_volume)
        pb.eq_clicked.connect(self._open_eq)
        pb.cover_clicked.connect(self._show_expanded)
        pb.transmit_clicked.connect(self._show_transmit_menu)
        pb.cover_loaded.connect(self._apply_adaptive_background)

    # ── Library ──

    def _load_library(self):
        self._all_items = self._db.get_all()
        self._apply_filters()
        self._rebuild_sidebar()

    def _apply_filters(self):
        items = self._all_items
        if self._kind_filter:
            items = [i for i in items if i.kind == self._kind_filter]
        if self._search_text:
            q = self._search_text.lower()
            items = [i for i in items if q in i.title.lower() or q in i.artist.lower()
                     or q in i.album.lower() or q in i.filename.lower()]
        self._model.populate(items)
        self._count.setText(f"{len(items)} elementos" if items else "0 elementos")
        if items:
            self._content.setCurrentIndex(1)
            self._table.setModel(self._model)
            self._table.setColumnWidth(0, 280); self._table.setColumnWidth(1, 170)
            self._table.setColumnWidth(2, 170); self._table.setColumnWidth(3, 55)
            self._table.setColumnWidth(4, 110); self._table.setColumnWidth(5, 75)
        else:
            self._content.setCurrentIndex(0)

    # ── Sidebar ──

    def _rebuild_sidebar(self):
        self._sidebar._clear()

        # Biblioteca
        self._sidebar.add_section("lib", "Biblioteca", "sidebar_library")
        self._sidebar.add_item("lib", "library", "Todas las canciones",
                               "sidebar_library")
        self._sidebar.add_item("lib", "albums", "Álbumes", "sidebar_albums")

        # Playlists
        self._sidebar.add_section("pl", "Playlist", "sidebar_playlists")
        for p in self._db.get_playlists():
            self._sidebar.add_item("pl", f"pl:{p['id']}", p['name'],
                                   "sidebar_playlist_item")
        self._sidebar.add_item("pl", "new_playlist", "+ Nueva playlist", "add")

        # Radio
        self._sidebar.add_section("rad", "Radio", "sidebar_radio")
        self._sidebar.add_item("rad", "radio", "Emisoras", "sidebar_radio")

        # Servidores
        self._sidebar.add_section("srv", "Servidores", "sidebar_servers")
        for srv in load_servers():
            ico = "sidebar_navidrome" if srv.stype == "navidrome" else "sidebar_jellyfin"
            self._sidebar.add_item("srv", f"srv:{srv.name}", srv.name, ico)
        self._sidebar.add_item("srv", "add_server", "+ Añadir servidor", "add")

        # Dispositivos
        self._sidebar.add_section("dev", "Dispositivos", "sidebar_devices")
        for d in get_mounted_devices():
            self._sidebar.add_item("dev", f"dev:{d['mount']}", d['name'],
                                   "sidebar_devices")

        self._sidebar.set_active("library")

        # Sidebar shadow
        from PySide6.QtWidgets import QGraphicsDropShadowEffect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(18); shadow.setXOffset(3); shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 30))
        self._sidebar.setGraphicsEffect(shadow)

    def _on_sidebar_click(self, key: str):
        self._current_playlist = None

        if key == "library":
            self._section_title.setText("Biblioteca")
            self._kind_filter = None
            self._apply_filters()
            self._view_mode = "list"
            self._set_active_button(self._btn_list)
            self._search.show()

        elif key and key.startswith("pl:"):
            pid = int(key.split(":", 1)[1])
            self._current_playlist = pid
            items = self._db.get_playlist_items(pid)
            self._model.populate(items)
            self._count.setText(f"{len(items)} temas")
            self._content.setCurrentIndex(1); self._table.setModel(self._model)
            self._table.setColumnWidth(0, 280); self._table.setColumnWidth(1, 170)
            self._table.setColumnWidth(2, 170); self._table.setColumnWidth(3, 55)
            self._table.setColumnWidth(4, 110); self._table.setColumnWidth(5, 75)
            name = next((p["name"] for p in self._db.get_playlists() if p["id"] == pid), "")
            self._section_title.setText(f"Playlist · {name}")
            self._search.show()

        elif key == "albums":
            self._section_title.setText("Álbumes")
            self._show_coverflow()
            self._search.show()

        elif key == "new_playlist":
            self._create_playlist()

        elif key == "radio":
            self._section_title.setText("📻 Radio")
            self._content.setCurrentIndex(5)
            self._search.hide()

        elif key == "add_server":
            self._add_server()

        elif key and key.startswith("srv:"):
            name = key.split(":", 1)[1]
            self._open_server(name)

        elif key and key.startswith("dev:"):
            mount = key.split(":", 1)[1]
            files = scan_device_music(mount)
            items = []
            for fp in files:
                n = os.path.basename(fp); e = os.path.splitext(fp)[1].lower()
                k = media_kind(e)
                items.append(MediaItem(filepath=fp, filename=n,
                             directory=os.path.dirname(fp), ext=e, kind=k, title=n))
            self._model.populate(items)
            self._count.setText(f"{len(items)} archivos")
            self._content.setCurrentIndex(1); self._table.setModel(self._model)
            self._section_title.setText(os.path.basename(mount))
            self._search.show()

    def _on_sidebar_menu(self, pos):
        widget = self._sidebar.childAt(pos)
        from sidebar_widget import _Item
        item = None
        while widget:
            if isinstance(widget, _Item):
                item = widget
                break
            widget = widget.parentWidget()
        if not item:
            return
        key = item.key
        menu = QMenu(self)

        if key and key.startswith("pl:"):
            pid = int(key.split(":", 1)[1])
            menu.addAction("Eliminar playlist", lambda: self._delete_playlist(pid))

        elif key and key.startswith("srv:"):
            name = key.split(":", 1)[1]
            menu.addAction("Eliminar servidor", lambda: self._remove_server(name))

        if not menu.isEmpty():
            menu.exec(self._sidebar._container.mapToGlobal(pos))

    def _create_playlist(self):
        name, ok = QInputDialog.getText(self, "Nueva playlist", "Nombre:")
        if ok and name.strip():
            self._db.create_playlist(name.strip())
            self._rebuild_sidebar()

    def _delete_playlist(self, pid):
        self._db.delete_playlist(pid)
        self._rebuild_sidebar(); self._load_library()

    # ── Navidrome / Jellyfin ──

    def _add_server(self):
        dlg = ServerDialog(self)
        if dlg.exec() and dlg.server:
            servers = load_servers()
            servers.append(dlg.server)
            save_servers(servers)
            self._rebuild_sidebar()

    def _open_server(self, name: str):
        servers = load_servers()
        srv_data = next((s for s in servers if s.name == name), None)
        if not srv_data:
            QMessageBox.warning(self, "Error", f"Servidor '{name}' no encontrado.")
            return

        try:
            client = SubsonicClient(srv_data)
            self._remote_browser = RemoteBrowser(client, name)
            self._remote_browser.track_selected.connect(self._play_stream)

            if self._content.count() > 2:
                self._content.removeWidget(self._content.widget(2))
            self._content.insertWidget(2, self._remote_browser)
            self._content.setCurrentIndex(2)

            self._remote_browser.load_artists()
            self._section_title.setText(f"🌐 {name}")
            self._search.hide()
        except AuthError as e:
            QMessageBox.warning(self, "Error de autenticación",
                f"No se pudo autenticar con '{name}':\n{e}")
        except ServerNotFoundError as e:
            QMessageBox.warning(self, "Servidor no encontrado",
                f"No se puede conectar a '{name}':\n{e}")
        except SubsonicError as e:
            QMessageBox.warning(self, "Error de conexión",
                f"No se pudo conectar a '{name}':\n{e}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo conectar:\n{e}")

    def _remove_server(self, name: str):
        if QMessageBox.question(self, "Eliminar",
            f"¿Eliminar servidor '{name}'?") == QMessageBox.Yes:
            servers = [s for s in load_servers() if s.name != name]
            save_servers(servers)
            self._rebuild_sidebar()
            self._load_library()

    def _play_stream(self, url: str, title: str, artist: str, album: str = ""):
        self._player.play_url(url, title, artist)
        self._player_bar.set_track(title, f"{artist} · Navidrome")
        self.setWindowTitle(f"Astra Music Player — {title}")

    def _play_radio(self, url: str, name: str):
        self._player.play_url(url, name, "Radio")
        self._player_bar.set_track(name, "📻 Radio")
        self.setWindowTitle(f"Astra Music Player — {name}")

    # ── Search ──

    def _on_search(self, text: str):
        self._search_text = text.strip()
        self._apply_filters()

    # ── CoverFlow ──

    def _set_active_button(self, active_btn):
        for btn in [self._btn_list, self._btn_grid, self._btn_cf]:
            if btn == active_btn:
                btn.setStyleSheet("""
                    QPushButton {
                        background: #FF7A00;
                        color: #ffffff;
                        border-radius: 6px;
                        padding: 2px 8px;
                        font-weight: 600;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background: transparent;
                        color: #8e8e93;
                        border-radius: 6px;
                        padding: 2px 8px;
                    }
                    QPushButton:hover {
                        background: rgba(255,122,0,0.10);
                    }
                """)

    def _show_list_view(self):
        self._view_mode = "list"
        self._set_active_button(self._btn_list)
        self._apply_filters()
        self._section_title.setText("Biblioteca")

    def _show_grid_view(self):
        self._view_mode = "grid"
        self._set_active_button(self._btn_grid)
        self._show_coverflow()
        self._section_title.setText("Carátulas")

    def _show_coverflow_view(self):
        self._view_mode = "coverflow"
        self._set_active_button(self._btn_cf)
        self._show_coverflow()
        self._section_title.setText("Coverflow")

    def _show_coverflow(self):
        items = self._all_items
        if self._kind_filter:
            items = [i for i in items if i.kind == self._kind_filter]
        covers = load_covers_for_albums(items, 260)

        if not covers:
            self._content.setCurrentIndex(0)
            self._count.setText("0 álbumes")
            return

        if self._coverflow is None:
            self._coverflow = CoverFlowWidget()
            self._coverflow.double_clicked.connect(self._on_coverflow_dbl)
            if self._content.count() > 3:
                self._content.removeWidget(self._content.widget(3))
            self._content.insertWidget(3, self._coverflow)

        self._coverflow.set_items(covers)
        self._content.setCurrentIndex(3)
        self._count.setText(f"{len(covers)} álbumes")
        self._coverflow.setFocus()

    def _on_coverflow_dbl(self, index: int):
        if not self._coverflow or index >= len(self._coverflow._items):
            return
        item = self._coverflow._items[index]
        data = item.data or {}
        tracks = data.get("tracks", [])
        if tracks:
            # Add entire album to queue and start playing
            filepaths = [t.filepath for t in tracks]
            self._player.enqueue(filepaths, play_now=True)
            self._show_expanded()

    # ── Expanded View ──

    def _show_expanded(self):
        if not self._player._current:
            return

        if self._expanded is None:
            self._expanded = ExpandedNowPlaying()
            self._expanded.go_back.connect(self._on_expanded_back)
            self._expanded.play_clicked.connect(self._player.toggle)
            self._expanded.prev_clicked.connect(self._on_expanded_prev)
            self._expanded.next_clicked.connect(self._on_expanded_next)
            self._expanded.seek_requested.connect(self._player.seek)
            self._expanded.volume_changed.connect(self._player.set_volume)
            self._expanded.track_from_queue.connect(self._on_queue_track)

            # Sync position/duration
            self._player.position_changed.connect(self._expanded.set_position)
            self._player.duration_changed.connect(self._expanded.set_duration)
            self._player.state_changed.connect(
                lambda s: self._expanded.set_state(
                    "playing" if s == PlaybackState.PLAYING else
                    "paused" if s == PlaybackState.PAUSED else "stopped"))

            if self._content.count() > 4:
                self._content.removeWidget(self._content.widget(4))
            self._content.insertWidget(4, self._expanded)

        # Update track info
        current = self._player._current
        name = os.path.basename(current) if current else ""
        from audio_chain import get_quality_label
        qual, _ = get_quality_label(current) if current else ("", "")
        artist = ""
        for i in self._all_items:
            if i.filepath == current:
                artist = i.artist
                album = i.album
                subtitle_parts = []
                if artist: subtitle_parts.append(artist)
                if album: subtitle_parts.append(album)
                if i.year: subtitle_parts.append(str(i.year))
                subtitle = " · ".join(subtitle_parts) if subtitle_parts else ""
                self._expanded.set_track(
                    i.title or name, artist, album, qual, "")
                break
        else:
            self._expanded.set_track(name, artist, "", qual, "")

        self._expanded.set_state(
            "playing" if self._player.state == PlaybackState.PLAYING else "paused")
        self._expanded.set_queue(self._player.get_queue())
        self._section_title.setText("Reproduciendo")

        self._content.setCurrentIndex(4)

    def _on_expanded_back(self):
        self._content.setCurrentIndex(1)
        self._section_title.setText("Biblioteca")

    def _on_expanded_prev(self):
        self._player.play_prev()
        self._show_expanded()

    def _on_expanded_next(self):
        self._player.play_next()
        self._show_expanded()

    def _on_queue_track(self, filepath: str):
        self._player.play(filepath)
        self._show_expanded()

    # ── File open / scan ──

    def _open_file(self):
        exts = " ".join(f"*{e}" for e in sorted(ALL_EXTS))
        fp, _ = QFileDialog.getOpenFileName(
            self, "Abrir archivo", os.path.expanduser("~"),
            f"Multimedia ({exts});;Todos (*)")
        if fp:
            self._db.add_file(fp)
            self._load_library()
            self._play_file(fp)

    def _add_folder(self):
        path = QFileDialog.getExistingDirectory(
            self, "Añadir carpeta", os.path.expanduser("~"))
        if not path:
            return
        self._scan_path(path)

    def _scan_path(self, path: str):
        from PySide6.QtCore import QThread
        worker = ScannerWorker(self._db, path)
        thread = QThread()
        progress = QProgressDialog("Escaneando...", "Cancelar", 0, 100, self)
        progress.setWindowModality(Qt.WindowModal); progress.setMinimumDuration(300)
        worker.moveToThread(thread)
        worker.progress.connect(
            lambda c, t, f: progress.setLabelText(f"[{c}/{t}] {os.path.basename(f)[:60]}"))
        worker.progress.connect(lambda c, t, f: progress.setValue(int(c / max(t, 1) * 100)))
        worker.finished.connect(lambda a: self._on_scan_done(a, progress, thread))
        progress.canceled.connect(worker.cancel)
        thread.started.connect(worker.run)
        worker.finished.connect(thread.quit); worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater); thread.start()

    def _on_scan_done(self, added, progress, thread):
        progress.close()
        self._load_library()

    # ── Playback ──

    def _on_table_dbl(self, idx):
        fp = self._model.index(idx.row(), MediaTableModel.COL_FILEPATH)
        fp = self._model.data(fp, Qt.DisplayRole)
        if fp:
            self._play_file(fp)

    def _play_file(self, filepath: str, add_to_queue: bool = False):
        if add_to_queue:
            self._player.enqueue([filepath], play_now=False)
        else:
            self._player.enqueue([filepath], play_now=True)

        name = os.path.basename(filepath)
        qual, _ = get_quality_label(filepath)
        artist = qual or ""
        quality_str = qual
        for item in self._all_items:
            if item.filepath == filepath:
                artist = item.artist or qual or ""
                ext = item.ext.upper().lstrip(".")
                if item.sample_rate:
                    if item.sample_rate >= 1000:
                        quality_str = f"{ext} · {item.sample_rate/1000:.1f}kHz"
                    else:
                        quality_str = f"{ext} · {item.sample_rate}Hz"
                elif item.bitrate and item.bitrate >= 1000:
                    quality_str = f"{ext} · {item.bitrate//1000}kbps"
                else:
                    quality_str = ext
                break
        self._player_bar.set_track(name, artist)
        self._player_bar.set_quality(quality_str)

        from album_art import find_cover_in_dir
        cover = find_cover_in_dir(os.path.dirname(filepath))
        if cover:
            from PySide6.QtGui import QPixmap
            pix = QPixmap(cover)
            if not pix.isNull():
                self._apply_adaptive_background(pix)
            else:
                self._reset_background()
        else:
            self._reset_background()

        self.setWindowTitle(f"Astra Music Player — {name}")

    def _on_state(self, state: PlaybackState):
        s = "playing" if state == PlaybackState.PLAYING else \
            "paused" if state == PlaybackState.PAUSED else "stopped"
        self._player_bar.set_state(s)
        if state == PlaybackState.STOPPED:
            self._player_bar.set_position(0)

    def _on_stop(self):
        self._player.stop()
        self._player_bar.set_state("stopped"); self._player_bar.set_position(0)
        self._player_bar.set_duration(0)
        self._player_bar.set_track("Sin reproducción", "Añade música a la biblioteca")
        self._reset_background()
        self.setWindowTitle("Astra Music Player")

    def _extract_colors(self, pixmap):
        from PySide6.QtGui import QColor
        small = pixmap.scaled(10, 10, Qt.IgnoreAspectRatio,
                             Qt.SmoothTransformation)
        img = small.toImage()
        r1 = g1 = b1 = r2 = g2 = b2 = 0
        n = 50
        for y in range(5):
            for x in range(10):
                c = img.pixelColor(x, y)
                r1 += c.red(); g1 += c.green(); b1 += c.blue()
        for y in range(5, 10):
            for x in range(10):
                c = img.pixelColor(x, y)
                r2 += c.red(); g2 += c.green(); b2 += c.blue()
        c1 = QColor(r1 // n, g1 // n, b1 // n).darker(160)
        c2 = QColor(r2 // n, g2 // n, b2 // n).darker(180)
        return c1.name(), c2.name()

    def _apply_adaptive_background(self, pixmap):
        if pixmap is None or pixmap.isNull():
            self._reset_background()
            return
        c1, c2 = self._extract_colors(pixmap)
        self._content.setStyleSheet(
            f"QStackedWidget {{"
            f"  background: qlineargradient(y1:0, y2:1, stop:0 {c1}, stop:1 {c2});"
            f"  border-radius: 12px;"
            f"}}")

    def _reset_background(self):
        self._content.setStyleSheet(
            "QStackedWidget {"
            "  background: qlineargradient(y1:0, y2:1, stop:0 #e8e8ed, stop:1 #d8d8dd);"
            "  border-radius: 12px;"
            "}")

    def _open_eq(self):
        from eq_panel import EqDialog
        dlg = EqDialog(self)
        dlg.eq_bands_graphic_changed.connect(
            lambda bands: self._player.set_eq_graphic(bands))
        dlg.eq_bands_parametric_changed.connect(
            lambda bands: self._player.set_eq_parametric(bands))
        dlg.preamp_changed.connect(
            lambda db: self._player.set_eq_preamp(db))
        dlg.eq_bypass_changed.connect(
            lambda bypass: self._player.set_eq_bypass(bypass))
        dlg.setWindowFlags(dlg.windowFlags() | Qt.WindowStaysOnTopHint)
        dlg.show()
        dlg.raise_()
        dlg.activateWindow()
        self._eq_dlg = dlg  # keep reference to prevent GC

    # ── Transmit ──

    def _show_transmit_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu { background: rgba(28,28,30,230); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 4px; }
            QMenu::item { padding: 6px 32px 6px 12px; border-radius: 6px; color: rgba(255,255,255,0.8); }
            QMenu::item:selected { background: rgba(255,122,0,0.20); }
            QMenu::separator { height: 1px; background: rgba(255,255,255,0.06); margin: 3px 8px; }
        """)

        local = menu.addAction("🔊 Local (sin transmitir)")
        local.setCheckable(True)
        active = self._transmit_mgr.get_active()
        local.setChecked(active is None)
        local.triggered.connect(lambda: self._activate_transmit_device(None))

        devices = self._transmit_mgr.get_devices()
        if devices:
            menu.addSeparator()
            for dev in devices:
                action = menu.addAction(f"📡 {dev.name}")
                action.setCheckable(True)
                action.setChecked(active is not None and active.name == dev.name)
                action.triggered.connect(
                    lambda checked, d=dev: self._activate_transmit_device(d))

        menu.addSeparator()
        menu.addAction("Añadir dispositivo...", self._add_transmit_device)
        menu.exec(self._player_bar._transmit_btn.mapToGlobal(
            self._player_bar._transmit_btn.rect().bottomLeft()))

    def _activate_transmit_device(self, device):
        if device is None:
            self._transmit_mgr.set_active(None)
            self._player.set_output_device(None)
            self._player_bar._transmit_btn.setStyleSheet("")
        else:
            self._transmit_mgr.set_active(device)
            self._player.set_output_device(device)
            self._player_bar._transmit_btn.setStyleSheet(
                "QPushButton { color: #FF7A00; }")

    def _on_transmit_devices_changed(self):
        pass

    def _on_transmit_active_changed(self):
        device = self._transmit_mgr.get_active()
        if device:
            self._player_bar._transmit_btn.setStyleSheet(
                "QPushButton { color: #FF7A00; }")
            self._player_bar._transmit_btn.setToolTip(
                f"Transmitiendo a: {device.name}")
        else:
            self._player_bar._transmit_btn.setStyleSheet("")
            self._player_bar._transmit_btn.setToolTip("Transmitir a dispositivo")

    def _add_transmit_device(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Añadir dispositivo")
        dlg.setMinimumWidth(380)
        from theme import apply_dialog_shadow
        apply_dialog_shadow(dlg)

        layout = QFormLayout(dlg)
        name = QLineEdit()
        name.setPlaceholderText("ej: Altavoz Salón")
        stype = QComboBox()
        stype.addItem("HTTP Stream (servidor TCP)", "http")
        stype.addItem("Snapcast", "snapcast")
        addr = QLineEdit()
        addr.setPlaceholderText("192.168.1.10")
        port = QLineEdit()
        port.setPlaceholderText("8554")

        layout.addRow("Nombre:", name)
        layout.addRow("Tipo:", stype)
        layout.addRow("IP / URL:", addr)
        layout.addRow("Puerto:", port)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(dlg.accept)
        btns.rejected.connect(dlg.reject)
        layout.addRow(btns)

        if dlg.exec() == QDialog.DialogCode.Accepted and name.text().strip():
            try:
                port_val = int(port.text()) if port.text().strip() else 0
            except ValueError:
                port_val = 0
            self._transmit_mgr.add_device(
                name.text().strip(), stype.currentData(),
                addr.text().strip(), port_val)

    def _manage_transmit_devices(self):
        devices = self._transmit_mgr.get_devices()
        if not devices:
            QMessageBox.information(self, "Dispositivos",
                                    "No hay dispositivos configurados.")
            return

        dlg = QDialog(self)
        dlg.setWindowTitle("Administrar dispositivos")
        dlg.setMinimumWidth(400)
        from theme import apply_dialog_shadow
        apply_dialog_shadow(dlg)

        layout = QVBoxLayout(dlg)
        lst = QListWidget()
        for dev in devices:
            item = QListWidgetItem(
                f"{dev.name}  ·  {dev.stype.upper()}  ·  "
                f"{dev.address}:{dev.port or '-'}")
            lst.addItem(item)
        layout.addWidget(lst)

        btn_row = QHBoxLayout()
        active = self._transmit_mgr.get_active()

        def _do_delete():
            sel = lst.currentItem()
            if sel:
                name = sel.text().split("  ·  ")[0]
                self._transmit_mgr.remove_device(name)
                dlg.accept()
                self._manage_transmit_devices()

        def _do_activate():
            sel = lst.currentItem()
            if sel:
                name = sel.text().split("  ·  ")[0]
                dev = next((d for d in self._transmit_mgr.get_devices()
                           if d.name == name), None)
                if dev:
                    self._activate_transmit_device(dev)
                    dlg.accept()

        del_btn = QPushButton("Eliminar")
        del_btn.clicked.connect(_do_delete)
        act_btn = QPushButton("Activar")
        act_btn.clicked.connect(_do_activate)
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(dlg.accept)

        btn_row.addWidget(act_btn)
        btn_row.addWidget(del_btn)
        btn_row.addStretch()
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)
        dlg.exec()

    def closeEvent(self, event):
        try:
            if hasattr(self, '_sync_mgr') and self._sync_mgr.is_active:
                self._sync_mgr.stop()
            if self._player._queue and self._db:
                self._db.save_queue(self._player._queue, self._player._queue_index)
        except Exception:
            pass
        self._player.stop()
        self._db.close()
        event.accept()

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            for url in urls:
                path = url.toLocalFile()
                if os.path.isdir(path):
                    event.acceptProposedAction()
                    return
                ext = os.path.splitext(path)[1].lower()
                if ext in AUDIO_EXTS:
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event: QDropEvent):
        files = []
        dirs = []
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.isdir(path):
                dirs.append(path)
            elif os.path.splitext(path)[1].lower() in AUDIO_EXTS:
                files.append(path)

        if dirs:
            for d in dirs:
                self._scan_path(d)
        if files:
            for fp in files:
                self._db.add_file(fp)
            self._load_library()
            if len(files) == 1:
                self._play_file(files[0])
            else:
                self._player.enqueue(files, play_now=True)
