"""EpisodesTab — list of podcast episodes."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class EpisodesTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("episodesTab")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        placeholder = QLabel(
            "No hay episodios recientes.\n\n"
            "Suscribete a un podcast para ver sus episodios aqui."
        )
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet(
            "color: rgba(255,255,255,0.48); font-size: 13px; "
            "background: transparent; border: none; padding: 48px;"
        )
        placeholder.setWordWrap(True)
        layout.addWidget(placeholder)
