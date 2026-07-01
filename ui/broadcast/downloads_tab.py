"""DownloadsTab — offline podcast episodes."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class DownloadsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("downloadsTab")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        placeholder = QLabel(
            "No hay episodios descargados.\n\n"
            "Descarga episodios de tus podcasts para escucharlos sin conexion."
        )
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet(
            "color: rgba(255,255,255,0.48); font-size: 13px; "
            "background: transparent; border: none; padding: 48px;"
        )
        placeholder.setWordWrap(True)
        layout.addWidget(placeholder)
