"""EcosystemHealthPanel — displays ecosystem health overview."""

from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout

from ui.ecosystem.ecosystem_styles import ecosystem_health_panel_qss


class EcosystemHealthPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ecosystemHealthPanel")
        self.setStyleSheet(ecosystem_health_panel_qss())
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        header = QLabel("Estado del Ecosistema")
        header.setObjectName("healthLabel")
        layout.addWidget(header)

        self._status_label = QLabel("---")
        self._status_label.setObjectName("healthStatus")
        layout.addWidget(self._status_label)

        metrics_grid = QGridLayout()
        metrics_grid.setSpacing(16)

        self._node_count_label = QLabel("0")
        self._node_count_label.setObjectName("healthValue")
        metrics_grid.addWidget(QLabel("Nodos"), 0, 0)
        metrics_grid.addWidget(self._node_count_label, 1, 0)

        self._edge_count_label = QLabel("0")
        self._edge_count_label.setObjectName("healthValue")
        metrics_grid.addWidget(QLabel("Conexiones"), 0, 1)
        metrics_grid.addWidget(self._edge_count_label, 1, 1)

        self._warning_count_label = QLabel("0")
        self._warning_count_label.setObjectName("healthValue")
        metrics_grid.addWidget(QLabel("Advertencias"), 0, 2)
        metrics_grid.addWidget(self._warning_count_label, 1, 2)

        layout.addLayout(metrics_grid)

    def set_health(self, health_data: dict[str, Any]) -> None:
        overall = health_data.get("overall_health", "unknown")
        self._status_label.setText(overall.capitalize())
        self._status_label.setStyleSheet(f"color: {self._health_color(overall)};")

        node_count = health_data.get("node_count", 0)
        edge_count = health_data.get("edge_count", 0)
        warning_count = health_data.get("warning_count", 0)

        self._node_count_label.setText(str(node_count))
        self._edge_count_label.setText(str(edge_count))
        self._warning_count_label.setText(str(warning_count))

    def _health_color(self, status: str) -> str:
        mapping = {"healthy": "#4CAF50", "degraded": "#FFA726", "critical": "#ef5350", "unknown": "#9E9E9E"}
        return mapping.get(status.lower(), "#9E9E9E")
