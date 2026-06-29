"""HubRouteController — lazy-init + fade for hub/detail pages.

Extracted from MainWindow to reduce window.py size.
Each hub page is created once on first navigation, then cached.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from ui.window import MainWindow

logger = logging.getLogger("michi.hub_route")


class HubRouteController:
    def __init__(self, window: MainWindow):
        self._win = window

    def lazy_hub(self, name: str, factory: Callable):
        w = self._win
        if not w._views.widget(name):
            w._views.register(name, factory())

    def show_audio_lab(self, key: str = ""):
        self.lazy_hub("audio_lab", lambda: __import__(
            "ui.audio_lab.audio_lab_page", fromlist=["AudioLabPage"]
        ).AudioLabPage(self._win._db, w=self._win))
        self._fade("audio_lab")

    def show_michi_disc_lab(self, key: str = ""):
        self.lazy_hub("michi_disc_lab", lambda: __import__(
            "ui.audio_lab.michi_disc_lab_page", fromlist=["MichiDiscLabPage"]
        ).MichiDiscLabPage(self._win._db, self._win))
        self._fade("michi_disc_lab")

    def show_library_hub(self, key: str = ""):
        self.lazy_hub("library_hub", self._make_library_hub_page)
        self._fade("library_hub")

    def show_mix_hub(self, key: str = ""):
        self.lazy_hub("mix_hub", lambda: __import__(
            "ui.mix_hub_page", fromlist=["MixHubPage"]
        ).MixHubPage(self._win))
        self._fade("mix_hub")

    def show_playback_hub(self, key: str = ""):
        self.lazy_hub("playback_hub", self._make_playback_hub_page)
        self._fade("playback_hub")

    def show_connections_hub(self, key: str = ""):
        self.lazy_hub("connections_hub", self._make_connections_hub_page)
        self._fade("connections_hub")

    def show_settings_hub(self, key: str = ""):
        w = self._win
        if not w._views.widget("settings_hub"):
            from ui.hubs.settings_hub_page import SettingsHubPage
            w._views.register("settings_hub", SettingsHubPage())
        self._fade("settings_hub")

    def show_devices_page(self, key: str = ""):
        w = self._win
        if key and key.startswith("dev:sync:"):
            parts = key.split(":", 2)
            target = parts[2] if len(parts) > 2 else ""
            self.lazy_hub("devices_page", lambda: __import__(
                "ui.devices_page", fromlist=["DevicesPage"]
            ).DevicesPage(w, sync_target=target))
        elif not w._views.widget("devices_page"):
            w._views.register("devices_page", self._make_devices_page())
        self._fade("devices_page")

    def show_metadata_review(self, key: str = ""):
        w = self._win
        if not w._views.widget("metadata_review"):
            from ui.metadata_review_panel import MetadataReviewPanel
            w._views.register("metadata_review", MetadataReviewPanel(w._db, parent=w))
        self._fade("metadata_review")

    # ── Internal helpers ──

    def _fade(self, name: str):
        self._win._fade_content(name)

    def _make_library_hub_page(self):
        from ui.hubs.library_hub_page import LibraryHubPage
        return LibraryHubPage(self._win._db, self._win._playback)

    def _make_playback_hub_page(self):
        from ui.hubs.playback_hub_page import PlaybackHubPage
        return PlaybackHubPage(self._win._db, self._win._playback,
                               self._win._playback_ctrl, self._win._search_ctrl)

    def _make_connections_hub_page(self):
        from ui.hubs.connections_hub_page import ConnectionsHubPage
        return ConnectionsHubPage(self._win._db, self._win._playback)

    def _make_devices_page(self):
        from ui.devices_page import DevicesPage
        return DevicesPage(self._win)
