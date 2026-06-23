"""HomePage — main landing hub with continue listening, recents, servers, quick actions."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QScrollArea, QPushButton,
)

from ui.central.central_styles import glass_card_qss, glass_button_qss


class HomePage(QWidget):
    def __init__(self, db=None, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("homePage")
        self._db = db
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setObjectName("homeScroll")

        content = QWidget()
        content.setObjectName("homeContent")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(40, 32, 40, 32)
        content_layout.setSpacing(20)

        title = QLabel("Inicio")
        title.setObjectName("homeTitle")
        content_layout.addWidget(title)

        subtitle = QLabel(
            "Tu musica, tus dispositivos y tus servidores en un solo lugar."
        )
        subtitle.setObjectName("homeSubtitle")
        subtitle.setWordWrap(True)
        content_layout.addWidget(subtitle)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)

        continue_card = self._build_card(
            "continue", "Continuar escuchando",
            "Retoma donde lo dejaste. La ultima cancion o playlist que estabas reproduciendo.",
            "Reanudar",
        )
        cards_layout.addWidget(continue_card, 1)

        recent_card = self._build_card(
            "recent", "Actividad reciente",
            "Explora lo que has escuchado recientemente y redescubre tus favoritos.",
            "Ver recientes",
        )
        cards_layout.addWidget(recent_card, 1)

        content_layout.addLayout(cards_layout)

        quick_row = QHBoxLayout()
        quick_row.setSpacing(12)

        for label, target in [
            ("Buscar musica", "library"),
            ("Playlists", "playlist_hub"),
            ("Recomendaciones", "assistant"),
        ]:
            btn = QPushButton(label)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked=None, t=target: self._navigate(t))
            quick_row.addWidget(btn)

        quick_row.addStretch()
        content_layout.addLayout(quick_row)
        content_layout.addStretch()

        scroll.setWidget(content)
        layout.addWidget(scroll)

        self._apply_qss()

    def _build_card(self, key: str, title: str, description: str,
                    btn_text: str) -> QFrame:
        card = QFrame()
        card.setObjectName(f"homeCard_{key}")

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(10)

        card_title = QLabel(title)
        card_title.setObjectName("homeCardTitle")
        card_layout.addWidget(card_title)

        card_desc = QLabel(description)
        card_desc.setObjectName("homeCardDesc")
        card_desc.setWordWrap(True)
        card_layout.addWidget(card_desc)

        card_layout.addStretch()

        btn = QPushButton(btn_text)
        btn.setCursor(Qt.PointingHandCursor)
        card_layout.addWidget(btn)

        return card

    def _navigate(self, target: str):
        w = self.window()
        if w and hasattr(w, '_on_sidebar_navigate'):
            w._on_sidebar_navigate(target)

    def _apply_qss(self):
        self.setStyleSheet("""
            QWidget#homePage { background: #090B11; }
            QScrollArea#homeScroll { background: transparent; border: none; }
            QWidget#homeContent { background: transparent; }
            QLabel#homeTitle {
                color: rgba(255,255,255,0.92); font-size: 22px; font-weight: 700;
            }
            QLabel#homeSubtitle {
                color: rgba(255,255,255,0.56); font-size: 13px;
            }
        """)
        for key in ("continue", "recent"):
            card = self.findChild(QFrame, f"homeCard_{key}")
            if card:
                card.setStyleSheet(glass_card_qss(f"homeCard_{key}"))
            title_lbl = self.findChild(QLabel, "homeCardTitle")
            desc_lbl = self.findChild(QLabel, "homeCardDesc")
            if title_lbl:
                title_lbl.setStyleSheet(
                    "QLabel { color: rgba(255,255,255,0.88); font-size: 16px; "
                    "font-weight: 600; background: transparent; border: none; }"
                )
            if desc_lbl:
                desc_lbl.setStyleSheet(
                    "QLabel { color: rgba(255,255,255,0.56); font-size: 12px; "
                    "background: transparent; border: none; }"
                )
        for btn in self.findChildren(QPushButton):
            if btn.objectName():
                continue
            btn.setStyleSheet(glass_button_qss("primary"))
