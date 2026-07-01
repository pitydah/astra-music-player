"""EcosystemPlanCard — displays a single configuration plan."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

from ui.ecosystem.ecosystem_styles import ecosystem_plan_card_qss


class EcosystemPlanCard(QFrame):
    clicked = Signal(str)

    def __init__(self, plan_id: str, title: str, description: str, changes_count: int, parent=None):
        super().__init__(parent)
        self._plan_id = plan_id
        self.setObjectName("ecosystemPlanCard")
        self.setStyleSheet(ecosystem_plan_card_qss())
        self.setCursor(Qt.PointingHandCursor)
        self._build_ui(title, description, changes_count)

    def _build_ui(self, title: str, description: str, changes_count: int):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)

        title_label = QLabel(title)
        title_label.setObjectName("planTitle")
        layout.addWidget(title_label)

        desc_label = QLabel(description)
        desc_label.setObjectName("planDescription")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        changes_label = QLabel(f"Cambios: {changes_count}")
        changes_label.setObjectName("planChanges")
        layout.addWidget(changes_label)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.clicked.emit(self._plan_id)
