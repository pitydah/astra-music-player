"""PodcastsTab — lista de podcasts suscritos (estructura visual)."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class PodcastsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("podcastsTab")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        placeholder = QLabel(
            "Aun no hay podcasts suscritos.\n\n"
            'Usa el boton "+ Anadir podcast RSS" para suscribirte '
            "a tu primer programa."
        )
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet(
            "color: rgba(255,255,255,0.48); font-size: 13px; "
            "background: transparent; border: none; padding: 48px;"
        )
        placeholder.setWordWrap(True)
        layout.addWidget(placeholder)
