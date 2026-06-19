"""Folder Browser — tree view of music directories."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QPushButton, QLabel, QFileDialog, QHeaderView,
)
import os

from library.folder_index import list_audio_files, list_subfolders
from ui.icons import get_icon


class FolderBrowserWidget(QWidget):
    folder_selected = Signal(list)  # list of filepaths

    def __init__(self, parent=None):
        super().__init__(parent)
        self._root = os.path.expanduser("~")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        toolbar = QHBoxLayout()
        self._root_label = QLabel(os.path.basename(self._root))
        self._root_label.setStyleSheet(
            "color: rgba(245,245,247,0.7); font-size: 13px; font-weight: 600;")
        up_btn = QPushButton("↑")
        up_btn.setFixedSize(28, 28)
        up_btn.setFlat(True)
        up_btn.clicked.connect(self._go_up)
        home_btn = QPushButton("⌂")
        home_btn.setFixedSize(28, 28)
        home_btn.setFlat(True)
        home_btn.clicked.connect(self._go_home)
        browse_btn = QPushButton("Abrir carpeta...")
        browse_btn.clicked.connect(self._browse_folder)
        toolbar.addWidget(home_btn)
        toolbar.addWidget(up_btn)
        toolbar.addWidget(self._root_label)
        toolbar.addStretch()
        toolbar.addWidget(browse_btn)
        layout.addLayout(toolbar)

        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.setIndentation(16)
        self._tree.setFrameShape(QTreeWidget.NoFrame)
        self._tree.setStyleSheet("""
            QTreeWidget {
                background: transparent; border: none; outline: none;
            }
            QTreeWidget::item {
                padding: 6px 10px; border-radius: 6px; margin: 1px 4px;
                color: rgba(245,245,247,0.7); font-size: 13px;
            }
            QTreeWidget::item:hover {
                background: rgba(255,255,255,0.06);
            }
            QTreeWidget::item:selected {
                background: rgba(255,122,0,0.15); color: #fff;
            }
        """)
        self._tree.itemDoubleClicked.connect(self._on_item)
        self._tree.itemClicked.connect(self._on_click)
        layout.addWidget(self._tree)

        self._load(self._root)

    def _load(self, path: str):
        self._tree.clear()
        self._root = path
        self._root_label.setText(os.path.basename(path) or path)

        # Folders first
        for folder in list_subfolders(path):
            item = QTreeWidgetItem(self._tree)
            item.setText(0, "📁 " + os.path.basename(folder))
            item.setData(0, Qt.UserRole, folder)
            item.setData(0, Qt.UserRole + 1, "folder")

        # Files second
        for fp in list_audio_files(path):
            item = QTreeWidgetItem(self._tree)
            item.setText(0, "🎵 " + os.path.basename(fp))
            item.setData(0, Qt.UserRole, fp)
            item.setData(0, Qt.UserRole + 1, "file")

    def _on_item(self, item, col):
        kind = item.data(0, Qt.UserRole + 1)
        path = item.data(0, Qt.UserRole)
        if kind == "folder":
            self._load(path)
        elif kind == "file":
            self.folder_selected.emit([path])

    def _on_click(self, item, col):
        kind = item.data(0, Qt.UserRole + 1)
        path = item.data(0, Qt.UserRole)
        if kind == "file":
            # Select all audio files in the same folder
            folder = os.path.dirname(path)
            all_files = list_audio_files(folder)
            if all_files:
                self.folder_selected.emit(all_files)

    def _go_up(self):
        parent = os.path.dirname(self._root)
        if parent and parent != self._root:
            self._load(parent)

    def _go_home(self):
        self._load(os.path.expanduser("~"))

    def _browse_folder(self):
        path = QFileDialog.getExistingDirectory(
            self, "Abrir carpeta", self._root)
        if path:
            self._load(path)
