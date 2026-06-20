"""Folder Browser — premium tree view of music directories."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QPushButton, QLabel, QFileDialog,
)
import os

from library.folder_index import list_audio_files, list_subfolders


class FolderBrowserWidget(QWidget):
    folder_selected = Signal(list)  # list of filepaths

    def __init__(self, parent=None):
        super().__init__(parent)
        self._root = os.path.expanduser("~")

        self.setStyleSheet("background: #090B11;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(8, 8, 8, 0)

        btn_qss = """
            QPushButton {
                background: rgba(255,255,255,0.06);
                border: 1px solid rgba(255,255,255,0.10);
                border-radius: 10px;
                padding: 6px 14px;
                color: rgba(255,255,255,0.78);
                font-size: 12px;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.10);
                color: #FFFFFF;
            }
        """

        home_btn = QPushButton("⌂ Inicio")
        home_btn.setFlat(True)
        home_btn.setStyleSheet(btn_qss)
        home_btn.clicked.connect(self._go_home)
        toolbar.addWidget(home_btn)

        up_btn = QPushButton("↑ Subir")
        up_btn.setFlat(True)
        up_btn.setStyleSheet(btn_qss)
        up_btn.clicked.connect(self._go_up)
        toolbar.addWidget(up_btn)

        self._root_label = QLabel(os.path.basename(self._root))
        self._root_label.setStyleSheet(
            "color: rgba(255,255,255,0.82); font-size: 13px; font-weight: 650;"
            "background: rgba(255,255,255,0.04); border-radius: 8px; padding: 5px 14px;")
        toolbar.addWidget(self._root_label)
        toolbar.addStretch()

        self._play_btn = QPushButton("▶ Reproducir carpeta")
        self._play_btn.setFlat(True)
        self._play_btn.setStyleSheet(btn_qss + """
            QPushButton { color: #FF7A00; border-color: rgba(255,122,0,0.25); }
            QPushButton:hover { color: #FF9A3D; border-color: rgba(255,122,0,0.45); }
        """)
        self._play_btn.clicked.connect(self._play_folder)
        toolbar.addWidget(self._play_btn)

        browse_btn = QPushButton("Abrir carpeta...")
        browse_btn.setFlat(True)
        browse_btn.setStyleSheet(btn_qss)
        browse_btn.clicked.connect(self._browse_folder)
        toolbar.addWidget(browse_btn)

        layout.addLayout(toolbar)

        # Tree
        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.setIndentation(20)
        self._tree.setFrameShape(QTreeWidget.NoFrame)
        self._tree.setStyleSheet("""
            QTreeWidget {
                background: rgba(255,255,255,0.025);
                border: 1px solid rgba(255,255,255,0.06);
                border-radius: 14px;
                outline: none;
                margin: 0 8px 8px 8px;
            }
            QTreeWidget::item {
                min-height: 34px;
                padding: 7px 14px;
                margin: 2px 8px;
                border-radius: 10px;
                color: rgba(255,255,255,0.78);
                font-size: 13px;
            }
            QTreeWidget::item:hover {
                background: rgba(255,255,255,0.06);
                color: #FFFFFF;
            }
            QTreeWidget::item:selected {
                background: rgba(255,77,46,0.20);
                color: #FFFFFF;
            }
            QScrollBar:vertical {
                width: 8px; background: transparent;
                border-radius: 4px; margin: 2px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255,255,255,0.14);
                min-height: 40px; border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(255,122,0,0.42);
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical { height: 0; }
        """)
        self._tree.itemDoubleClicked.connect(self._on_item)
        layout.addWidget(self._tree, 1)

        self._load(self._root)

    def _load(self, path: str):
        self._tree.clear()
        self._root = path
        self._root_label.setText(os.path.basename(path) or path)

        for folder in list_subfolders(path):
            item = QTreeWidgetItem(self._tree)
            item.setText(0, "📁 " + os.path.basename(folder))
            item.setData(0, Qt.UserRole, folder)
            item.setData(0, Qt.UserRole + 1, "folder")

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

    def _play_folder(self):
        all_files = list_audio_files(self._root)
        if all_files:
            self.folder_selected.emit(all_files)

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
