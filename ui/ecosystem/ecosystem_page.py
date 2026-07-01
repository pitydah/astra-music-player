"""EcosystemPage — main ecosystem view with health, devices, issues, and plans."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ui.ecosystem.ecosystem_device_card import EcosystemDeviceCard
from ui.ecosystem.ecosystem_health_panel import EcosystemHealthPanel
from ui.ecosystem.ecosystem_issue_card import EcosystemIssueCard
from ui.ecosystem.ecosystem_plan_card import EcosystemPlanCard
from ui.ecosystem.ecosystem_styles import ecosystem_page_qss


class EcosystemPage(QFrame):
    diagnose_requested = Signal()
    plan_requested = Signal()
    assistant_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ecosystemPage")
        self.setStyleSheet(ecosystem_page_qss())
        self._build_ui()

    def _build_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(24, 16, 24, 16)
        outer_layout.setSpacing(16)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        title_column = QVBoxLayout()
        title_column.setSpacing(2)
        title_label = QLabel("Ecosistema Michi")
        title_label.setObjectName("pageTitle")
        title_column.addWidget(title_label)
        subtitle_label = QLabel("Dispositivos, sincronizacion y configuracion")
        subtitle_label.setObjectName("pageSubtitle")
        title_column.addWidget(subtitle_label)
        header_layout.addLayout(title_column, 1)

        diagnose_btn = QPushButton("Diagnosticar")
        diagnose_btn.setObjectName("actionBtn")
        diagnose_btn.clicked.connect(self.diagnose_requested.emit)
        header_layout.addWidget(diagnose_btn)

        plan_btn = QPushButton("Plan de configuracion")
        plan_btn.setObjectName("actionBtn")
        plan_btn.clicked.connect(self.plan_requested.emit)
        header_layout.addWidget(plan_btn)

        ask_btn = QPushButton("Preguntar a Michi")
        ask_btn.setObjectName("actionBtn")
        ask_btn.clicked.connect(lambda: self.assistant_requested.emit("ecosystem"))
        header_layout.addWidget(ask_btn)

        outer_layout.addLayout(header_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setObjectName("ecosystemScroll")

        content = QWidget()
        content.setObjectName("ecosystemContent")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(16)

        self._health_panel = EcosystemHealthPanel(content)
        content_layout.addWidget(self._health_panel)

        self._device_section = self._make_section("Dispositivos")
        self._device_container = self._device_section.findChildren(QFrame, "sectionContent")[0] if self._device_section.findChildren(QFrame, "sectionContent") else QFrame()
        content_layout.addWidget(self._device_section)

        self._issues_section = self._make_section("Problemas")
        self._issues_container = self._issues_section.findChildren(QFrame, "sectionContent")[0] if self._issues_section.findChildren(QFrame, "sectionContent") else QFrame()
        content_layout.addWidget(self._issues_section)

        self._plans_section = self._make_section("Planes disponibles")
        self._plans_container = self._plans_section.findChildren(QFrame, "sectionContent")[0] if self._plans_section.findChildren(QFrame, "sectionContent") else QFrame()
        content_layout.addWidget(self._plans_section)

        content_layout.addStretch()
        scroll.setWidget(content)
        outer_layout.addWidget(scroll, 1)

    def _make_section(self, title: str) -> QFrame:
        card = QFrame()
        card.setObjectName("sectionCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        header = QLabel(title)
        header.setObjectName("sectionTitle")
        layout.addWidget(header)

        container = QFrame()
        container.setObjectName("sectionContent")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(8)
        layout.addWidget(container)

        return card

    def set_health(self, health_data: dict[str, Any]) -> None:
        self._health_panel.set_health(health_data)

    def set_devices(self, devices: list[dict[str, Any]]) -> None:
        layout = self._device_container.layout()
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        if not devices:
            layout.addWidget(QLabel("No hay dispositivos conectados"))
            return
        for d in devices:
            card = EcosystemDeviceCard(
                device_id=d.get("node_id", ""),
                name=d.get("label", "Desconocido"),
                device_type=d.get("node_type", "unknown"),
                status=d.get("status", "unknown"),
            )
            layout.addWidget(card)

    def set_issues(self, issues: list[dict[str, Any]]) -> None:
        layout = self._issues_container.layout()
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        if not issues:
            layout.addWidget(QLabel("No hay problemas detectados"))
            return
        for i in issues:
            card = EcosystemIssueCard(
                issue_id=i.get("issue_code", ""),
                problem=i.get("problem", ""),
                cause=i.get("cause", ""),
                fix=i.get("fix", ""),
            )
            layout.addWidget(card)

    def set_plans(self, plans: list[dict[str, Any]]) -> None:
        layout = self._plans_container.layout()
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        if not plans:
            layout.addWidget(QLabel("No hay planes disponibles"))
            return
        for p in plans:
            card = EcosystemPlanCard(
                plan_id=p.get("plan_id", ""),
                title=p.get("title", ""),
                description=p.get("description", ""),
                changes_count=p.get("change_count", 0),
            )
            layout.addWidget(card)
