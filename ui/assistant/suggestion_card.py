"""SuggestionCard — a single contextual suggestion widget."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QVBoxLayout


class SuggestionCard(QFrame):
    clicked = Signal(str)
    dismissed = Signal(str)

    def __init__(self, suggestion_id: str, title: str, description: str, parent=None):
        super().__init__(parent)
        self._suggestion_id = suggestion_id
        self._build_ui(title, description)

    def _build_ui(self, title: str, description: str):
        self.setObjectName("suggestionCard")
        self.setCursor(Qt.PointingHandCursor)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)

        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        title_label = QLabel(title)
        title_label.setObjectName("suggestionTitle")
        title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        title_row.addWidget(title_label)

        dismiss_btn = QPushButton("×")
        dismiss_btn.setObjectName("suggestionDismiss")
        dismiss_btn.setFixedSize(20, 20)
        dismiss_btn.setCursor(Qt.ArrowCursor)
        dismiss_btn.clicked.connect(self._on_dismiss)
        title_row.addWidget(dismiss_btn)
        layout.addLayout(title_row)

        desc_label = QLabel(description)
        desc_label.setObjectName("suggestionDesc")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.clicked.emit(self._suggestion_id)

    def _on_dismiss(self):
        self.dismissed.emit(self._suggestion_id)
