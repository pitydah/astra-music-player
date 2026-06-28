"""Discover Dashboard — large cards for Mix, NoReproducidos, Favoritos, Recientes."""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QScrollArea, QFrame,
)

from ui.icons import get_pixmap
from ui.central.central_styles import (
    glass_card_qss, glass_icon_slot_qss, card_title_qss, card_desc_qss,
)


class DiscoverDashboard(QWidget):
    navigate_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("discoverDashboard")
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QScrollArea.NoFrame)
        self._scroll.setStyleSheet(
            "QScrollArea { background: transparent; border: none; }")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(32, 8, 32, 24)
        layout.setSpacing(20)

        grid = QGridLayout()
        grid.setSpacing(16)

        cards = [
            ("mix_daily", "Mix diario", "Reproducido en los últimos 7 días", "sidebar_mix"),
            ("mix_unplayed", "No escuchadas", "Canciones que aún no has reproducido", "sidebar_unplayed"),
            ("mix_popular", "Más escuchadas", "Tus canciones con más reproducciones", "sidebar_popular"),
            ("favs", "Favoritos", "Canciones que has marcado como favoritas", "sidebar_popular"),
            ("recent", "Recientes", "Reproducidas recientemente", "sidebar_recent"),
        ]

        self._cards_data = cards
        self._grid = grid
        self._layout = layout
        self._last_cols = -1
        self._rebuild_cards()

        self._scroll.setWidget(container)
        main = QVBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.addWidget(self._scroll)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._rebuild_cards()

    def _rebuild_cards(self):
        cols = max(1, (self.width() - 64) // 380)
        if cols == self._last_cols:
            return
        self._last_cols = cols
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for i, (key, name, desc, icon_name) in enumerate(self._cards_data):
            card = _DiscoverCard(name, desc, icon_name)
            card.clicked.connect(lambda checked=False, k=key:
                                 self.navigate_requested.emit(k))
            self._grid.addWidget(card, i // cols, i % cols)


class _DiscoverCard(QFrame):
    clicked = Signal()

    def __init__(self, title: str, desc: str, icon_name: str):
        super().__init__()
        self.setObjectName("discoverCard")
        self.setMinimumHeight(140)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(glass_card_qss("discoverCard", "elevated"))

        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        icon_lbl = QLabel()
        pix = get_pixmap(icon_name, size=44)
        if pix and not pix.isNull():
            icon_lbl.setPixmap(pix)
        icon_lbl.setFixedSize(56, 56)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet(glass_icon_slot_qss("discoIcon", size=56))
        layout.addWidget(icon_lbl)

        text_col = QVBoxLayout()
        text_col.setSpacing(4)
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(card_title_qss())
        text_col.addWidget(title_lbl)

        desc_lbl = QLabel(desc)
        desc_lbl.setStyleSheet(card_desc_qss())
        desc_lbl.setWordWrap(True)
        text_col.addWidget(desc_lbl)
        layout.addLayout(text_col, 1)
        layout.addStretch()

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)
