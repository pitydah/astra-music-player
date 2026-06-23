"""LibraryHubPage — music library hub with tabs for songs, albums, artists, genres, folders."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QFrame, QTabWidget, QPushButton,
)

from ui.central.central_styles import glass_card_qss, glass_button_qss


class LibraryHubPage(QWidget):
    def __init__(self, window=None, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("libraryHubPage")
        self._win = window
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QFrame()
        header.setObjectName("libraryHubHeader")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(20, 12, 20, 12)

        title = QLabel("Biblioteca")
        title.setObjectName("libraryHubTitle")
        header_layout.addWidget(title)

        subtitle = QLabel("Musica local, servidores remotos y archivos disponibles offline.")
        subtitle.setObjectName("libraryHubSubtitle")
        subtitle.setWordWrap(True)
        header_layout.addWidget(subtitle)

        layout.addWidget(header)

        self._tabs = QTabWidget()
        self._tabs.setObjectName("libraryHubTabs")

        tabs_data = [
            ("canciones", "Canciones", "Toda tu musica local en una tabla"),
            ("albums", "Albumes", "Caratulas y navegacion visual"),
            ("artists", "Artistas", "Explora por artista y album"),
            ("genres", "Generos", "Atlas de estilos musicales"),
            ("folders", "Carpetas", "Explorador musical local"),
        ]

        for key, label, desc in tabs_data:
            tab = self._build_tab_placeholder(key, label, desc)
            self._tabs.addTab(tab, label)

        layout.addWidget(self._tabs, 1)

        self._apply_qss()

    def _build_tab_placeholder(self, key: str, label: str, desc: str) -> QWidget:
        w = QWidget()
        w_layout = QVBoxLayout(w)
        w_layout.setContentsMargins(20, 20, 20, 20)
        w_layout.setSpacing(12)

        card = QFrame()
        card.setObjectName(f"libTabCard_{key}")
        c_layout = QVBoxLayout(card)
        c_layout.setContentsMargins(20, 20, 20, 20)
        c_layout.setSpacing(8)

        c_title = QLabel(label)
        c_title.setStyleSheet(
            "QLabel { color: rgba(255,255,255,0.88); font-size: 14px; font-weight: 600; "
            "background: transparent; border: none; }"
        )
        c_layout.addWidget(c_title)

        c_desc = QLabel(desc)
        c_desc.setWordWrap(True)
        c_desc.setStyleSheet(
            "QLabel { color: rgba(255,255,255,0.52); font-size: 12px; "
            "background: transparent; border: none; }"
        )
        c_layout.addWidget(c_desc)

        btn = QPushButton(f"Abrir {label}")
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(lambda checked=None, k=key: self._navigate(k))
        c_layout.addWidget(btn)

        card.setStyleSheet(glass_card_qss(f"libTabCard_{key}"))
        btn.setStyleSheet(glass_button_qss("primary"))

        w_layout.addWidget(card)
        w_layout.addStretch()
        return w

    def _navigate(self, target: str):
        w = self.window()
        if w and hasattr(w, '_on_sidebar_navigate'):
            w._on_sidebar_navigate(target)

    def _apply_qss(self):
        self.setStyleSheet("""
            QWidget#libraryHubPage { background: #090B11; }
            QFrame#libraryHubHeader { background: transparent; border-bottom: 1px solid rgba(255,255,255,0.03); }
            QLabel#libraryHubTitle { color: rgba(255,255,255,0.92); font-size: 22px; font-weight: 700; }
            QLabel#libraryHubSubtitle { color: rgba(255,255,255,0.56); font-size: 13px; }
            QTabWidget#libraryHubTabs::pane { border: none; background: transparent; }
            QTabBar::tab {
                background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.04);
                border-radius: 8px; padding: 8px 20px; color: rgba(255,255,255,0.52);
                font-size: 13px; margin-right: 4px;
            }
            QTabBar::tab:selected {
                background: rgba(143,183,255,0.08); border: 1px solid rgba(143,183,255,0.12);
                color: rgba(143,183,255,0.85);
            }
        """)
