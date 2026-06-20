"""Folder Browser — premium music explorer with columns and navigation."""

import os
import subprocess

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QPushButton, QLabel, QFileDialog, QHeaderView, QFrame, QMenu,
    QApplication,
)

from library.folder_index import list_audio_files, list_subfolders
from ui.icons import get_icon


class FolderBrowserWidget(QWidget):
    folder_selected = Signal(list)      # filepaths to play
    queue_requested = Signal(list)      # filepaths to queue
    scan_requested = Signal(str)        # directory to scan

    def __init__(self, parent=None):
        super().__init__(parent)
        self._root = os.path.expanduser("~")

        self.setStyleSheet("background: #090B11;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # ── Toolbar ──
        toolbar_frame = QFrame()
        toolbar_frame.setObjectName("folderToolbar")
        toolbar_frame.setStyleSheet("""
            QFrame#folderToolbar {
                background: rgba(255,255,255,0.035);
                border: 1px solid rgba(255,255,255,0.075);
                border-radius: 14px;
            }
        """)

        toolbar_layout = QHBoxLayout(toolbar_frame)
        toolbar_layout.setContentsMargins(10, 8, 10, 8)
        toolbar_layout.setSpacing(8)

        btn_qss = """
            QPushButton {
                background: rgba(255,255,255,0.055);
                color: rgba(255,255,255,0.82);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 10px;
                padding: 7px 12px;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.09);
                color: #FFFFFF;
            }
            QPushButton:pressed {
                background: rgba(255,122,0,0.16);
            }
            QPushButton:disabled {
                color: rgba(255,255,255,0.28);
                background: rgba(255,255,255,0.025);
                border: 1px solid rgba(255,255,255,0.035);
            }
        """

        self._home_btn = QPushButton("Inicio")
        self._home_btn.setStyleSheet(btn_qss)
        self._home_btn.clicked.connect(self._go_home)
        toolbar_layout.addWidget(self._home_btn)

        self._up_btn = QPushButton("Subir")
        self._up_btn.setStyleSheet(btn_qss)
        self._up_btn.clicked.connect(self._go_up)
        toolbar_layout.addWidget(self._up_btn)

        # ── Breadcrumb ──
        self._breadcrumb = QLabel("")
        self._breadcrumb.setObjectName("breadcrumbLabel")
        self._breadcrumb.setStyleSheet("""
            QLabel#breadcrumbLabel {
                color: rgba(255,255,255,0.86);
                background: rgba(0,0,0,0.18);
                border: 1px solid rgba(255,255,255,0.06);
                border-radius: 10px;
                padding: 7px 12px;
                font-size: 12px;
                font-weight: 650;
            }
        """)
        toolbar_layout.addWidget(self._breadcrumb, 1)
        toolbar_layout.addStretch()

        self._play_btn = QPushButton("▶ Reproducir carpeta")
        self._play_btn.setStyleSheet(btn_qss + """
            QPushButton { color: #FF7A00; border-color: rgba(255,122,0,0.25); }
            QPushButton:hover { color: #FF9A3D; border-color: rgba(255,122,0,0.45); }
        """)
        self._play_btn.clicked.connect(self._play_folder)
        toolbar_layout.addWidget(self._play_btn)

        self._queue_btn = QPushButton("+ Añadir a cola")
        self._queue_btn.setStyleSheet(btn_qss)
        self._queue_btn.clicked.connect(self._queue_folder)
        toolbar_layout.addWidget(self._queue_btn)

        self._scan_btn = QPushButton("Escanear")
        self._scan_btn.setStyleSheet(btn_qss)
        self._scan_btn.clicked.connect(
            lambda: self.scan_requested.emit(self._root))
        toolbar_layout.addWidget(self._scan_btn)

        self._refresh_btn = QPushButton("Actualizar")
        self._refresh_btn.setStyleSheet(btn_qss)
        self._refresh_btn.clicked.connect(lambda: self._load(self._root))
        toolbar_layout.addWidget(self._refresh_btn)

        self._browse_btn = QPushButton("Abrir carpeta...")
        self._browse_btn.setStyleSheet(btn_qss)
        self._browse_btn.clicked.connect(self._browse_folder)
        toolbar_layout.addWidget(self._browse_btn)

        layout.addWidget(toolbar_frame)

        # ── Tree ──
        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(False)
        self._tree.setColumnCount(4)
        self._tree.setHeaderLabels(["Nombre", "Tipo", "Canciones", "Ruta"])
        self._tree.setIndentation(22)
        self._tree.setIconSize(QSize(32, 32))
        self._tree.setFrameShape(QTreeWidget.NoFrame)
        self._tree.setAlternatingRowColors(True)
        self._tree.setAnimated(True)
        self._tree.setUniformRowHeights(True)
        self._tree.setSelectionMode(QTreeWidget.SingleSelection)
        self._tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self._tree.setStyleSheet("""
            QTreeWidget {
                background: #090B11;
                alternate-background-color: #0E1118;
                color: #FFFFFF;
                border: 1px solid rgba(255,255,255,0.055);
                border-radius: 16px;
                outline: none;
                padding: 8px;
                margin: 0 8px 8px 8px;
            }
            QTreeWidget::item {
                min-height: 42px;
                padding: 7px 10px;
                margin: 2px 4px;
                border-radius: 12px;
                color: rgba(255,255,255,0.78);
            }
            QTreeWidget::item:hover {
                background: rgba(255,255,255,0.06);
                color: #FFFFFF;
            }
            QTreeWidget::item:selected {
                background: rgba(255,77,46,0.20);
                color: #FFFFFF;
                border-left: 3px solid rgba(255,122,0,0.85);
            }
            QHeaderView::section {
                background: #10131A;
                color: rgba(255,255,255,0.72);
                border: none;
                border-bottom: 1px solid rgba(255,255,255,0.07);
                padding: 8px 10px;
                font-size: 11.5px;
                font-weight: 700;
            }
            QScrollBar:vertical {
                background: rgba(255,255,255,0.025);
                width: 10px;
                margin: 4px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255,255,255,0.18);
                min-height: 40px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(255,122,0,0.42);
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
                background: transparent;
            }
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: transparent;
            }
        """)

        header = self._tree.header()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

        self._tree.itemDoubleClicked.connect(self._on_item)
        self._tree.customContextMenuRequested.connect(self._on_context_menu)
        layout.addWidget(self._tree, 1)

        # ── Status ──
        self._status = QLabel("")
        self._status.setObjectName("folderStatus")
        self._status.setStyleSheet("""
            QLabel#folderStatus {
                color: rgba(255,255,255,0.48);
                font-size: 12px;
                font-weight: 500;
                padding: 8px 12px;
            }
        """)
        layout.addWidget(self._status)

        self._load(self._root)

    # ── Navigation ──

    def _load(self, path: str):
        self._tree.clear()
        self._root = path
        self._breadcrumb.setText(self._format_breadcrumb(path))

        try:
            folders = list_subfolders(path)
        except Exception:
            folders = []
        try:
            files = list_audio_files(path)
        except Exception:
            files = []

        for folder in folders:
            item = QTreeWidgetItem(self._tree)
            item.setIcon(0, QIcon(get_icon("folder")))
            item.setText(0, os.path.basename(folder))
            item.setText(1, "Carpeta")
            try:
                count = len(list_audio_files(folder))
                item.setText(2, str(count))
            except Exception:
                item.setText(2, "—")
            item.setText(3, folder)
            item.setData(0, Qt.UserRole, folder)
            item.setData(0, Qt.UserRole + 1, "folder")

        for fp in files:
            item = QTreeWidgetItem(self._tree)
            song_icon = get_icon("songs") or get_icon("sidebar_library")
            if song_icon:
                item.setIcon(0, QIcon(song_icon))
            item.setText(0, os.path.basename(fp))
            item.setText(1, "Canción")
            item.setText(2, "")
            item.setText(3, fp)
            item.setData(0, Qt.UserRole, fp)
            item.setData(0, Qt.UserRole + 1, "file")

        self._status.setText(f"{len(folders)} carpetas · {len(files)} canciones")

    @staticmethod
    def _format_breadcrumb(path: str) -> str:
        home = os.path.expanduser("~")
        if path.startswith(home):
            rel = os.path.relpath(path, home)
            if rel == ".":
                return "Inicio"
            parts = ["Inicio"] + rel.split(os.sep)
        else:
            parts = path.strip(os.sep).split(os.sep)
        if len(parts) > 4:
            parts = ["…"] + parts[-3:]
        return " / ".join(parts)

    def _on_item(self, item, col):
        kind = item.data(0, Qt.UserRole + 1)
        path = item.data(0, Qt.UserRole)
        if kind == "folder":
            self._load(path)
        elif kind == "file":
            self.folder_selected.emit([path])

    # ── Toolbar actions ──

    def _play_folder(self):
        files = list_audio_files(self._root)
        if files:
            self.folder_selected.emit(files)

    def _queue_folder(self):
        files = list_audio_files(self._root)
        if files:
            self.queue_requested.emit(files)

    def _go_up(self):
        parent = os.path.dirname(self._root)
        if parent and parent != self._root:
            self._load(parent)

    def _go_home(self):
        self._load(os.path.expanduser("~"))

    def _browse_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Abrir carpeta", self._root)
        if path:
            self._load(path)

    # ── Context menu ──

    def _on_context_menu(self, pos):
        item = self._tree.itemAt(pos)
        if not item:
            return
        path = item.data(0, Qt.UserRole)
        kind = item.data(0, Qt.UserRole + 1)
        menu = QMenu(self)

        if kind == "folder":
            menu.addAction("Abrir carpeta", lambda: self._load(path))
            menu.addAction("Reproducir carpeta", lambda: self._play_path_folder(path))
            menu.addAction("Añadir carpeta a la cola", lambda: self._queue_path_folder(path))
            menu.addAction("Escanear carpeta", lambda: self.scan_requested.emit(path))
            menu.addSeparator()
            menu.addAction("Abrir en Dolphin", lambda: self._open_in_file_manager(path))
            menu.addAction("Copiar ruta", lambda: QApplication.clipboard().setText(path))
        elif kind == "file":
            menu.addAction("Reproducir canción", lambda: self.folder_selected.emit([path]))
            menu.addAction("Añadir a cola", lambda: self.queue_requested.emit([path]))
            menu.addSeparator()
            menu.addAction("Abrir en Dolphin",
                          lambda: self._open_in_file_manager(os.path.dirname(path)))
            menu.addAction("Copiar ruta", lambda: QApplication.clipboard().setText(path))

        menu.exec(self._tree.viewport().mapToGlobal(pos))

    def _play_path_folder(self, path: str):
        files = list_audio_files(path)
        if files:
            self.folder_selected.emit(files)

    def _queue_path_folder(self, path: str):
        files = list_audio_files(path)
        if files:
            self.queue_requested.emit(files)

    @staticmethod
    def _open_in_file_manager(path: str):
        target = path if os.path.isdir(path) else os.path.dirname(path)
        try:
            subprocess.Popen(["xdg-open", target])
        except Exception:
            pass
