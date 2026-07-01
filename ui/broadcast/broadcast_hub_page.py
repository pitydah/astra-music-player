"""BroadcastHubPage — main hub for radio and podcasts (Transmisiones)."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QLineEdit,
    QStackedWidget,
)

from ui.central.central_styles import (
    glass_button_qss, glass_input_qss,
)
from ui.broadcast.broadcast_cards import summary_card
from streaming.radio_manager import RadioManager


class BroadcastHubPage(QWidget):
    navigate_requested = Signal(str)

    def __init__(self, radio_manager: RadioManager | None = None, parent=None):
        super().__init__(parent)
        self.setObjectName("broadcastHubPage")
        self._radio_manager = radio_manager
        self._tabs: list[str] = ["live", "podcasts", "episodes", "downloads", "history"]
        self._tab_widgets: dict[str, QWidget] = {}
        self._current_tab = "live"
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        cl = QVBoxLayout(content)
        cl.setContentsMargins(40, 32, 40, 32)
        cl.setSpacing(16)

        title = QLabel("Transmisiones")
        title.setStyleSheet(
            "color: rgba(255,255,255,0.92); font-size: 22px; "
            "font-weight: 700; background: transparent; border: none;"
        )
        cl.addWidget(title)

        sub = QLabel(
            "Radio en vivo, podcasts y episodios para escuchar, guardar o continuar."
        )
        sub.setStyleSheet(
            "color: rgba(255,255,255,0.56); font-size: 13px; "
            "background: transparent; border: none;"
        )
        sub.setWordWrap(True)
        cl.addWidget(sub)

        action_row = QHBoxLayout()
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Buscar en transmisiones...")
        self._search_input.setStyleSheet(glass_input_qss())
        self._search_input.textChanged.connect(self._on_search)
        action_row.addWidget(self._search_input, 1)

        self._add_radio_btn = QPushButton("+ Anadir emisora")
        self._add_radio_btn.setCursor(Qt.PointingHandCursor)
        self._add_radio_btn.setStyleSheet(glass_button_qss("secondary"))
        self._add_radio_btn.clicked.connect(self._add_station)
        action_row.addWidget(self._add_radio_btn)

        self._add_podcast_btn = QPushButton("+ Anadir podcast RSS")
        self._add_podcast_btn.setCursor(Qt.PointingHandCursor)
        self._add_podcast_btn.setStyleSheet(glass_button_qss("secondary"))
        self._add_podcast_btn.setVisible(False)
        action_row.addWidget(self._add_podcast_btn)

        cl.addLayout(action_row)

        summary_row = QHBoxLayout()
        summary_row.setSpacing(10)
        live_count = self._radio_manager.count() if self._radio_manager else 0
        summary_row.addWidget(summary_card("En vivo", str(live_count)))
        summary_row.addWidget(summary_card("Podcasts", "0"))
        summary_row.addWidget(summary_card("Nuevos", "0", "#FFB347"))
        summary_row.addWidget(summary_card("Descargas", "0", "#64DC64"))
        cl.addLayout(summary_row)

        tab_row = QHBoxLayout()
        tab_row.setSpacing(4)
        tab_labels = {
            "live": "En vivo",
            "podcasts": "Podcasts",
            "episodes": "Episodios",
            "downloads": "Descargas",
            "history": "Historial",
        }
        self._tab_btns: dict[str, QPushButton] = {}
        for tab_key, tab_label in tab_labels.items():
            btn = QPushButton(tab_label)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setCheckable(True)
            btn.setChecked(tab_key == self._current_tab)
            btn.clicked.connect(lambda checked=False, k=tab_key: self._switch_tab(k))
            btn.setStyleSheet(self._tab_qss(tab_key == self._current_tab))
            self._tab_btns[tab_key] = btn
            tab_row.addWidget(btn)
        tab_row.addStretch()
        cl.addLayout(tab_row)

        self._stack = QStackedWidget()
        self._stack.setStyleSheet("background: transparent; border: none;")

        from ui.broadcast.radio_live_tab import RadioLiveTab
        live_tab = RadioLiveTab(self._radio_manager)
        self._tab_widgets["live"] = live_tab
        self._stack.addWidget(live_tab)

        from ui.broadcast.podcasts_tab import PodcastsTab
        podcasts_tab = PodcastsTab()
        self._tab_widgets["podcasts"] = podcasts_tab
        self._stack.addWidget(podcasts_tab)

        from ui.broadcast.episodes_tab import EpisodesTab
        ep_tab = EpisodesTab()
        self._tab_widgets["episodes"] = ep_tab
        self._stack.addWidget(ep_tab)

        from ui.broadcast.downloads_tab import DownloadsTab
        dl_tab = DownloadsTab()
        self._tab_widgets["downloads"] = dl_tab
        self._stack.addWidget(dl_tab)

        from ui.broadcast.history_tab import HistoryTab
        hist_tab = HistoryTab()
        self._tab_widgets["history"] = hist_tab
        self._stack.addWidget(hist_tab)

        self._stack.setCurrentIndex(0)
        cl.addWidget(self._stack, 1)

        scroll.setWidget(content)
        layout.addWidget(scroll)

    def _switch_tab(self, tab_key: str):
        self._current_tab = tab_key
        idx = self._tabs.index(tab_key)
        self._stack.setCurrentIndex(idx)
        for k, btn in self._tab_btns.items():
            checked = k == tab_key
            btn.setChecked(checked)
            btn.setStyleSheet(self._tab_qss(checked))

    def _on_search(self, text: str):
        if self._current_tab == "live" and "live" in self._tab_widgets:
            self._tab_widgets["live"].set_filter(text)

    def _add_station(self):
        if self._current_tab == "live" and "live" in self._tab_widgets:
            self._tab_widgets["live"].add_station()

    @staticmethod
    def _tab_qss(active: bool) -> str:
        if active:
            return (
                "QPushButton { background: rgba(143,183,255,0.12); "
                "border: 1px solid rgba(143,183,255,0.20); border-radius: 8px; "
                "color: rgba(255,255,255,0.90); font-size: 12px; font-weight: 600; "
                "padding: 6px 16px; }"
            )
        return (
            "QPushButton { background: rgba(255,255,255,0.03); "
            "border: 1px solid rgba(255,255,255,0.04); border-radius: 8px; "
            "color: rgba(255,255,255,0.56); font-size: 12px; font-weight: 500; "
            "padding: 6px 16px; }"
            "QPushButton:hover { background: rgba(255,255,255,0.06); }"
        )
