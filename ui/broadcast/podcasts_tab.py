"""PodcastsTab — grid of subscribed podcast shows."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QFrame, QScrollArea, QGridLayout,
)

from ui.central.central_styles import glass_card_qss
from streaming.podcast_manager import PodcastManager
from streaming.podcast_models import PodcastShow


class PodcastsTab(QWidget):
    add_feed_requested = Signal()

    def __init__(self, podcast_manager: PodcastManager | None = None, parent=None):
        super().__init__(parent)
        self.setObjectName("podcastsTab")
        self._pm = podcast_manager
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        self._cl = QVBoxLayout(content)
        self._cl.setContentsMargins(0, 0, 0, 0)
        self._cl.setSpacing(12)

        self._empty_state = QLabel(
            "No hay podcasts suscritos.\n\n"
            'Usa el botón "+ Añadir podcast RSS" para suscribirte '
            "a tu primer programa."
        )
        self._empty_state.setAlignment(Qt.AlignCenter)
        self._empty_state.setStyleSheet(
            "color: rgba(255,255,255,0.48); font-size: 13px; "
            "background: transparent; border: none; padding: 48px;"
        )
        self._empty_state.setWordWrap(True)
        self._cl.addWidget(self._empty_state)

        self._grid = QGridLayout()
        self._grid.setSpacing(14)
        self._cl.addLayout(self._grid)

        self._cl.addStretch()

        scroll.setWidget(content)
        layout.addWidget(scroll)

        self.reload()

    def reload(self):
        if self._pm is None:
            self._empty_state.setVisible(True)
            return

        shows = self._pm.get_shows()
        if not shows:
            self._empty_state.setVisible(True)
            self._clear_grid()
            return

        self._empty_state.setVisible(False)
        self._clear_grid()
        for i, show in enumerate(shows):
            card = _build_show_card(show)
            self._grid.addWidget(card, i // 2, i % 2)

    def set_filter(self, text: str):
        if self._pm is None:
            return
        shows = self._pm.get_shows()
        self._clear_grid()
        idx = 0
        for show in shows:
            if text.lower() in show.title.lower() or text.lower() in show.author.lower():
                card = _build_show_card(show)
                self._grid.addWidget(card, idx // 2, idx % 2)
                idx += 1
        self._empty_state.setVisible(idx == 0)

    def _clear_grid(self):
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


def _build_show_card(show: PodcastShow) -> QFrame:
    card = QFrame()
    card.setStyleSheet(glass_card_qss("podcastCard"))
    card.setMinimumHeight(140)
    layout = QVBoxLayout(card)
    layout.setContentsMargins(16, 16, 16, 16)
    layout.setSpacing(6)

    title = QLabel(show.title)
    title.setStyleSheet(
        "color: rgba(255,255,255,0.88); font-size: 14px; font-weight: 600; "
        "background: transparent; border: none;"
    )
    title.setWordWrap(True)
    layout.addWidget(title)

    if show.author:
        author = QLabel(show.author)
        author.setStyleSheet(
            "color: rgba(255,255,255,0.50); font-size: 11px; "
            "background: transparent; border: none;"
        )
        layout.addWidget(author)

    meta = QLabel(
        f"{show.episode_count} episodio(s)"
        + (f", {show.unread_count} nuevo(s)" if show.unread_count else "")
    )
    meta.setStyleSheet(
        "color: rgba(255,255,255,0.42); font-size: 10px; "
        "background: transparent; border: none;"
    )
    layout.addWidget(meta)

    if show.unread_count:
        badge = QLabel(f"{show.unread_count} NUEVO(S)")
        badge.setStyleSheet(
            "color: rgba(100,220,100,0.90); font-size: 9px; font-weight: 700; "
            "background: rgba(100,220,100,0.10); border: 1px solid rgba(100,220,100,0.15); "
            "border-radius: 4px; padding: 2px 8px;"
        )
        layout.addWidget(badge)

    layout.addStretch()
    return card
