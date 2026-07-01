"""HistoryTab — timeline of radio and podcast listening."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class HistoryTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("historyTab")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        placeholder = QLabel(
            "No hay historial todavia.\n\n"
            "El historial registrara las emisoras que escuches "
            "y los episodios de podcast que reproduzcas."
        )
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet(
            "color: rgba(255,255,255,0.48); font-size: 13px; "
            "background: transparent; border: none; padding: 48px;"
        )
        placeholder.setWordWrap(True)
        layout.addWidget(placeholder)
