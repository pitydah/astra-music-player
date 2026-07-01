"""EcosystemDeviceCard — displays a single ecosystem device."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout

from ui.ecosystem.ecosystem_styles import ecosystem_device_card_qss


class EcosystemDeviceCard(QFrame):
    def __init__(self, device_id: str, name: str, device_type: str, status: str, parent=None):
        super().__init__(parent)
        self._device_id = device_id
        self.setObjectName("ecosystemDeviceCard")
        self.setStyleSheet(ecosystem_device_card_qss())
        self._build_ui(name, device_type, status)

    def _build_ui(self, name: str, device_type: str, status: str):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(12)

        status_indicator = QLabel("●")
        status_indicator.setObjectName("deviceStatus")
        status_indicator.setFixedSize(16, 16)
        status_indicator.setAlignment(Qt.AlignCenter)
        color = self._status_color(status)
        status_indicator.setStyleSheet(f"color: {color}; font-size: 14px;")
        layout.addWidget(status_indicator)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        name_label = QLabel(name)
        name_label.setObjectName("deviceName")
        info_layout.addWidget(name_label)

        type_label = QLabel(device_type)
        type_label.setObjectName("deviceType")
        info_layout.addWidget(type_label)

        layout.addLayout(info_layout, 1)
        layout.addStretch()

        status_label = QLabel(status.capitalize())
        status_label.setObjectName("deviceStatus")
        status_label.setStyleSheet(f"color: {color}; font-size: 11px;")
        layout.addWidget(status_label)

    def _status_color(self, status: str) -> str:
        mapping = {"online": "#4CAF50", "offline": "#ef5350", "unknown": "#9E9E9E", "pairing": "#FFA726"}
        return mapping.get(status.lower(), "#9E9E9E")
