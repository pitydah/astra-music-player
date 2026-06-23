"""ConnectionsHubPage — real servers, Home Audio, devices, diagnostics."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QFrame, QScrollArea, QPushButton,
)

from ui.central.central_styles import glass_card_qss, glass_button_qss


class ConnectionsHubPage(QWidget):
    def __init__(self, db=None, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("connectionsHubPage")
        self._db = db
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setObjectName("connectionsHubScroll")

        content = QWidget()
        content.setObjectName("connectionsHubContent")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(40, 32, 40, 32)
        content_layout.setSpacing(20)

        title = QLabel("Conexiones")
        title.setObjectName("connectionsHubTitle")
        content_layout.addWidget(title)

        servers = self._get_servers()
        subtitle = QLabel(
            f"Servidores musicales, Home Audio, dispositivos y diagnostico de red. "
            f"{len(servers)} servidores configurados."
        )
        subtitle.setObjectName("connectionsHubSubtitle")
        subtitle.setWordWrap(True)
        content_layout.addWidget(subtitle)

        if servers:
            server_card = QFrame()
            server_card.setObjectName("connectionsCard_servers")
            sc_layout = QVBoxLayout(server_card)
            sc_layout.setContentsMargins(20, 16, 20, 16)
            sc_layout.setSpacing(8)

            for srv in servers:
                srv_label = QLabel(f"{srv.get('name', 'Servidor')} ({srv.get('stype', 'navidrome')})")
                srv_label.setStyleSheet(
                    "QLabel { color: rgba(143,183,255,0.72); font-size: 13px; "
                    "background: transparent; border: none; }"
                )
                sc_layout.addWidget(srv_label)

            server_card.setStyleSheet(
                "QFrame { background: rgba(143,183,255,0.04); border: 1px solid rgba(143,183,255,0.08); "
                "border-radius: 12px; }"
            )
            content_layout.addWidget(server_card)

        actions = [
            ("add_server", "Añadir servidor musical",
             "Conecta Navidrome, Jellyfin o Subsonic para acceder a tu musica remota."),
            ("home_audio", "Home Audio",
             "Audio multiroom, parlantes Snapcast y Home Assistant."),
        ]

        for key, label, desc in actions:
            card = self._build_card(key, label, desc)
            content_layout.addWidget(card)

        content_layout.addStretch()

        scroll.setWidget(content)
        layout.addWidget(scroll)

        self._apply_qss()

    def _get_servers(self) -> list:
        try:
            import json
            import os
            path = os.path.expanduser("~/.local/share/michi-music-player/subsonic_servers.json")
            if os.path.exists(path):
                with open(path) as f:
                    return json.load(f)
        except Exception:
            pass
        return []

    def _build_card(self, key: str, title: str, description: str) -> QFrame:
        card = QFrame()
        card.setObjectName(f"connectionsCard_{key}")

        c_layout = QVBoxLayout(card)
        c_layout.setContentsMargins(20, 20, 20, 20)
        c_layout.setSpacing(8)

        c_title = QLabel(title)
        c_layout.addWidget(c_title)

        c_desc = QLabel(description)
        c_desc.setWordWrap(True)
        c_layout.addWidget(c_desc)

        btn = QPushButton(f"Abrir {title}")
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(lambda checked=None, k=key: self._navigate(k))
        c_layout.addWidget(btn)

        card.setStyleSheet(glass_card_qss(f"connectionsCard_{key}"))
        return card

    def _navigate(self, target: str):
        w = self.window()
        if w and hasattr(w, '_on_sidebar_navigate'):
            w._on_sidebar_navigate(target)

    def _apply_qss(self):
        self.setStyleSheet("""
            QWidget#connectionsHubPage { background: #090B11; }
            QScrollArea#connectionsHubScroll { background: transparent; border: none; }
            QWidget#connectionsHubContent { background: transparent; }
            QLabel#connectionsHubTitle { color: rgba(255,255,255,0.92); font-size: 22px; font-weight: 700; }
            QLabel#connectionsHubSubtitle { color: rgba(255,255,255,0.56); font-size: 13px; }
        """)
        for key in ("add_server", "home_audio"):
            card = self.findChild(QFrame, f"connectionsCard_{key}")
            if card:
                for lbl in card.findChildren(QLabel):
                    if "font-size" not in (lbl.styleSheet() or ""):
                        lbl.setStyleSheet(
                            "QLabel { color: rgba(255,255,255,0.62); font-size: 12px; "
                            "background: transparent; border: none; }"
                        )
                for btn in card.findChildren(QPushButton):
                    btn.setStyleSheet(glass_button_qss("primary"))
