"""Song Grid Widget — flat mosaic of song cards with status badges."""

import os

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QLabel,
    QGridLayout, QFrame, QHBoxLayout,
)
from library.album_art import find_cover_in_dir
from ui.effects.michi_glass import apply_card_shadow
from ui.central.central_styles import glass_card_qss, badge_qss


class SongGridWidget(QWidget):
    song_double_clicked = Signal(str)  # filepath
    song_context_menu = Signal(str, object)  # filepath, QPoint

    def __init__(self, parent=None):
        super().__init__(parent)
        self._items = []
        self._card_size = 170
        self._status_cache = {}

        self.setStyleSheet(
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            " stop:0 rgba(20,22,28,0.94), stop:1 rgba(8,10,16,0.94));")

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QScrollArea.NoFrame)
        self._scroll.setStyleSheet(
            "QScrollArea { background: transparent; border: none; }"
            "QScrollBar:vertical { width: 3px; background: transparent;"
            "  border: none; }"
            "QScrollBar::handle:vertical { background: rgba(255,255,255,0.12);"
            "  min-height: 32px; border-radius: 2px; }"
            "QScrollBar::handle:vertical:hover { background: rgba(255,255,255,0.24); }"
            "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }")

        self._container = QWidget()
        self._container.setStyleSheet("background: transparent;")
        self._grid = QGridLayout(self._container)
        self._grid.setContentsMargins(20, 16, 20, 16)
        self._grid.setSpacing(14)
        self._grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self._scroll.setWidget(self._container)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._scroll)

    def set_items(self, items, card_size: int = 170, status_cache: dict[int, dict] | None = None):
        self._items = items
        self._card_size = card_size
        self._status_cache = status_cache or {}

        # Clear grid
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not items:
            return

        cols = max(1, (self._scroll.viewport().width() - 40) // (card_size + 14))
        if cols < 1:
            cols = 1

        for i, item in enumerate(items):
            st = self._status_cache.get(getattr(item, 'id', 0), {})
            card = _SongCard(item, card_size, status=st)
            card.double_clicked.connect(self.song_double_clicked.emit)
            card.context_menu_requested.connect(self._on_menu)
            row = i // cols
            col = i % cols
            self._grid.addWidget(card, row, col, Qt.AlignTop)

    def _on_menu(self, filepath, pos):
        self.song_context_menu.emit(filepath, pos)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Only relayout, don't rebuild cards
        if self._items and self._scroll.viewport().width() > 40:
            cols = max(1, (self._scroll.viewport().width() - 40) // (self._card_size + 14))
            for i in range(self._grid.count()):
                item = self._grid.itemAt(i)
                if item and item.widget():
                    old_col = i % max(1, self._grid.columnCount() or 1)
                    new_col = i % cols
                    if old_col != new_col:
                        row = i // cols
                        col = i % cols
                        self._grid.addWidget(item.widget(), row, col, Qt.AlignTop)


class _SongCard(QFrame):
    double_clicked = Signal(str)
    context_menu_requested = Signal(str, object)

    def __init__(self, item, size: int, status: dict | None = None):
        super().__init__()
        self._fp = getattr(item, 'filepath', None) or getattr(item, 'uri', '')
        self._status = status or {}
        self.setFixedSize(size, size + 86)
        self.setCursor(Qt.PointingHandCursor)
        self.setObjectName("songCard")
        self.setStyleSheet(glass_card_qss("songCard"))
        apply_card_shadow(self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)

        # Cover
        cover = QLabel()
        cover.setFixedSize(size - 12, size - 12)
        cover.setAlignment(Qt.AlignCenter)
        cover.setStyleSheet(
            "QLabel { background: rgba(255,255,255,0.04); border-radius: 8px; }")

        title = getattr(item, 'title', '') or os.path.basename(self._fp)
        artist = getattr(item, 'artist', '') or ""
        album = getattr(item, 'album', '') or ""

        # Load cover or show skeleton
        cover_path = find_cover_in_dir(os.path.dirname(self._fp)) if self._fp else ""
        if cover_path:
            pix = QPixmap(cover_path)
            if not pix.isNull():
                pix = pix.scaled(size - 16, size - 16, Qt.KeepAspectRatio,
                                 Qt.SmoothTransformation)
                cover.setPixmap(pix)
            else:
                cover.setStyleSheet(
                    "QLabel { background: qlineargradient(x1:0, y1:0, x2:1, y2:1,"
                    "  stop:0 rgba(255,255,255,0.045), stop:0.5 rgba(255,255,255,0.06),"
                    "  stop:1 rgba(255,255,255,0.045)); border-radius: 8px;"
                    "  color: rgba(255,255,255,0.08); font-size: 28px; }")
                cover.setText("♪")
        else:
            cover.setStyleSheet(
                "QLabel { background: qlineargradient(x1:0, y1:0, x2:1, y2:1,"
                "  stop:0 rgba(255,255,255,0.045), stop:0.5 rgba(255,255,255,0.06),"
                "  stop:1 rgba(255,255,255,0.045)); border-radius: 8px;"
                "  color: rgba(255,255,255,0.08); font-size: 28px; }")
            cover.setText("♪")

        # Favorite star overlay
        if self._status.get("is_favorite"):
            fav_overlay = QLabel("★", cover)
            fav_overlay.setAlignment(Qt.AlignTop | Qt.AlignRight)
            fav_overlay.setStyleSheet(
                "color: #FFD700; font-size: 18px; background: transparent;"
                " padding: 4px;")
            fav_overlay.setGeometry(0, 0, size - 12, size - 12)
        layout.addWidget(cover, alignment=Qt.AlignCenter)

        # Title
        title_lbl = QLabel(title[:40] + "..." if len(title) > 40 else title)
        title_lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        title_lbl.setStyleSheet(
            "QLabel { color: rgba(255,255,255,0.88); font-size: 11px;"
            "  font-weight: 550; background: transparent; border: none; }")
        title_lbl.setWordWrap(False)
        title_lbl.setFixedHeight(16)
        layout.addWidget(title_lbl)

        # Artist
        artist_lbl = QLabel(artist[:35] + "..." if len(artist) > 35 else artist or "—")
        artist_lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        artist_lbl.setStyleSheet(
            "QLabel { color: rgba(255,255,255,0.45); font-size: 10px;"
            "  background: transparent; border: none; }")
        artist_lbl.setFixedHeight(14)
        layout.addWidget(artist_lbl)

        # Duration or album
        dur = getattr(item, 'duration', 0.0)
        dur_str = f"{int(dur//60)}:{int(dur%60):02d}" if dur else ""
        extra = album[:25] if album else dur_str
        extra_lbl = QLabel(extra)
        extra_lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        extra_lbl.setStyleSheet(
            "QLabel { color: rgba(255,255,255,0.56); font-size: 10px;"
            "  background: transparent; border: none; }")
        extra_lbl.setFixedHeight(14)
        layout.addWidget(extra_lbl)

        # Badge row (format + quality + warning)
        badges = []
        ext = getattr(item, 'ext', '') or ''
        if ext:
            badges.append(ext.upper().lstrip("."))
        qcat = self._status.get("quality_category", "")
        if qcat == "hires":
            badges.append("Hi-Res")
        elif qcat == "lossless":
            pass
        elif qcat == "lossy":
            badges.append("Lossy")
        elif qcat == "dsd":
            badges.append("DSD")
        if self._status.get("has_audio_lab_warning"):
            badges.append("⚠")
        if badges:
            badge_row = QHBoxLayout()
            badge_row.setContentsMargins(0, 0, 0, 0)
            badge_row.setSpacing(4)
            for b in badges:
                bl = QLabel(b)
                is_warn = b == "⚠"
                bl.setStyleSheet(badge_qss("warning" if is_warn else "info"))
                bl.setFixedHeight(16)
                badge_row.addWidget(bl)
            badge_row.addStretch()
            layout.addLayout(badge_row)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.double_clicked.emit(self._fp)

    def contextMenuEvent(self, event):
        self.context_menu_requested.emit(self._fp, event.globalPos())
