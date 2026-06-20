"""Album grid — premium 2D grid of album cards with metadata."""

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QGridLayout,
    QPushButton, QLabel, QFrame, QSizePolicy,
)

from library.album_art import load_covers_for_albums
from library.library_db import MediaItem


class AlbumGridWidget(QWidget):
    album_double_clicked = Signal(list)  # list of filepaths

    def __init__(self, parent=None):
        super().__init__(parent)
        self._items = []

        self.setStyleSheet("background: #090B11;")

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QScrollArea.NoFrame)
        self._scroll.setStyleSheet(
            "QScrollArea { background: #090B11; border: none; }"
            "QScrollBar:vertical { width: 8px; background: rgba(255,255,255,0.025);"
            "  border-radius: 4px; }"
            "QScrollBar::handle:vertical { background: rgba(255,255,255,0.16);"
            "  min-height: 40px; border-radius: 4px; }"
            "QScrollBar::handle:vertical:hover { background: rgba(255,255,255,0.28); }"
            "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }")

        self._container = QWidget()
        self._container.setStyleSheet("background: transparent;")
        self._grid = QGridLayout(self._container)
        self._grid.setSpacing(16)
        self._grid.setContentsMargins(20, 16, 20, 16)
        self._grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self._scroll.setWidget(self._container)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._scroll)

    def set_items(self, items: list[MediaItem], cover_size: int = 200):
        self._items = items
        while self._grid.count():
            w = self._grid.takeAt(0).widget()
            if w:
                w.deleteLater()

        groups = load_covers_for_albums(items, cover_size)

        cols = max(1, (self._scroll.viewport().width() - 40) // (cover_size + 24))
        if cols < 1:
            cols = 1

        for i, group in enumerate(groups):
            card = _AlbumCard(group, cover_size)
            tracks = group.data.get("tracks", [])
            if tracks:
                fps = [t.filepath for t in tracks]
                card.clicked.connect(
                    lambda checked=False, f=fps: self.album_double_clicked.emit(f))
            row = i // cols
            col = i % cols
            self._grid.addWidget(card, row, col, Qt.AlignTop)


class _AlbumCard(QFrame):
    clicked = Signal()

    def __init__(self, cover_item, cover_size: int):
        super().__init__()
        self.setFixedSize(cover_size + 16, cover_size + 78)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.035);
                border: 1px solid rgba(255,255,255,0.06);
                border-radius: 14px;
            }
            QFrame:hover {
                background: rgba(255,255,255,0.065);
                border: 1px solid rgba(255,255,255,0.12);
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # Cover
        cover_btn = QPushButton()
        cover_btn.setFixedSize(cover_size, cover_size)
        cover_btn.setIconSize(QSize(cover_size - 8, cover_size - 8))
        cover_btn.setFlat(True)
        cover_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.04); border-radius: 10px; border: none;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.06);
            }
        """)
        if cover_item.pixmap and not cover_item.pixmap.isNull():
            cover_btn.setIcon(QIcon(cover_item.pixmap.scaled(
                cover_size - 8, cover_size - 8,
                Qt.KeepAspectRatio, Qt.SmoothTransformation)))
        else:
            place = QLabel("♪")
            place.setAlignment(Qt.AlignCenter)
            place.setStyleSheet(
                "color: rgba(255,255,255,0.12); font-size: 36px; background: transparent;")
            place.setParent(cover_btn)
            place.setGeometry(0, 0, cover_size, cover_size)

        cover_btn.clicked.connect(self.clicked.emit)
        layout.addWidget(cover_btn, alignment=Qt.AlignCenter)

        # Title
        title = cover_item.title[:30] + "…" if len(cover_item.title) > 30 else cover_item.title
        title_lbl = QLabel(title)
        title_lbl.setAlignment(Qt.AlignCenter)
        title_lbl.setStyleSheet(
            "QLabel { color: rgba(255,255,255,0.84); font-size: 12px; font-weight: 600;"
            "  background: transparent; }")
        title_lbl.setWordWrap(False)
        layout.addWidget(title_lbl)

        # Subtitle
        sub = cover_item.subtitle[:28] + "…" if len(cover_item.subtitle) > 28 else cover_item.subtitle
        sub_lbl = QLabel(sub or "—")
        sub_lbl.setAlignment(Qt.AlignCenter)
        sub_lbl.setStyleSheet(
            "QLabel { color: rgba(255,255,255,0.45); font-size: 10.5px;"
            "  background: transparent; }")
        sub_lbl.setWordWrap(False)
        layout.addWidget(sub_lbl)

        # Track count + info
        tracks = cover_item.data.get("tracks", [])
        count = len(tracks)
        dur = sum(getattr(t, 'duration', 0) or 0 for t in tracks)
        dur_str = f"{int(dur//60)}:{int(dur%60):02d}" if dur > 0 else ""

        info_parts = []
        if count:
            info_parts.append(f"{count} tracks")
        if dur_str:
            info_parts.append(dur_str)

        fmt_str = ""
        if tracks:
            exts = set(getattr(t, 'ext', '') for t in tracks if getattr(t, 'ext', ''))
            if exts:
                fmt_str = ", ".join(e.upper().lstrip(".") for e in exts)[:20]

        info_lbl = QLabel(" · ".join(info_parts))
        info_lbl.setAlignment(Qt.AlignCenter)
        info_lbl.setStyleSheet(
            "QLabel { color: rgba(255,255,255,0.35); font-size: 10px;"
            "  background: transparent; }")
        layout.addWidget(info_lbl)

        if fmt_str:
            badge = QLabel(fmt_str)
            badge.setAlignment(Qt.AlignCenter)
            badge.setStyleSheet(
                "QLabel { color: rgba(255,255,255,0.28); font-size: 9px;"
                "  background: rgba(255,255,255,0.03); border-radius: 5px; padding: 1px 6px; }")
            layout.addWidget(badge, alignment=Qt.AlignCenter)

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)
