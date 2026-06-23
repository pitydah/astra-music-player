"""Sidebar controller — rebuilds sidebar sections with hub-focused navigation."""

from PySide6.QtCore import QObject, Signal



class SidebarController(QObject):
    navigation_requested = Signal(str)

    def __init__(self, sidebar_widget, db, parent=None):
        super().__init__(parent)
        self._sidebar = sidebar_widget
        self._db = db
        sidebar_widget.item_clicked.connect(self._on_item_click)

    def _on_item_click(self, key: str):
        self.navigation_requested.emit(key)

    def rebuild(self, servers: list):
        self._sidebar._clear()

        # ── Hubs principales ──
        self._sidebar.add_section("hub", "Michi Music", "sidebar_mix")
        self._sidebar.add_item("hub", "home", "Inicio", "sidebar_library")
        self._sidebar.add_item("hub", "library_hub", "Biblioteca", "sidebar_library")
        self._sidebar.add_item("hub", "mix_hub", "Mix", "sidebar_mix")
        self._sidebar.add_item("hub", "playback_hub", "Reproduccion", "warm_play")
        self._sidebar.add_item("hub", "connections_hub", "Conexiones", "sidebar_servers")
        self._sidebar.add_item("hub", "audio_lab", "Audio Lab", "sidebar_mix")
        self._sidebar.add_item("hub", "settings_hub", "Configuracion", "warm_settings")
        self._sidebar.add_item("hub", "home_audio", "Home Audio", "home_audio")

        self._sidebar.set_active("home")
