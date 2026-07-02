from PySide6.QtCore import QObject, Signal, Property, Slot


MIX_CATEGORIES = [
    {"id": "daily_mix", "title": "Mix diario", "icon": "MX", "desc": "Recomendaciones basadas en tu historial reciente"},
    {"id": "favorites", "title": "Favoritos", "icon": "FV", "desc": "Tus canciones marcadas como favoritas"},
    {"id": "recent", "title": "Escuchadas recientemente", "icon": "RC", "desc": "Canciones que has reproducido"},
    {"id": "most_played", "title": "Más escuchadas", "icon": "MP", "desc": "Tus canciones con más reproducciones"},
    {"id": "discover", "title": "Hallazgos", "icon": "DI", "desc": "Canciones que no has escuchado en tu biblioteca"},
    {"id": "ai_recommended", "title": "Recomendaciones IA", "icon": "AI", "desc": "Sugerencias inteligentes basadas en patrones"},
]


class MixBridge(QObject):
    dataChanged = Signal()

    def __init__(self, db=None, parent=None):
        super().__init__(parent)
        self._db = db
        self._current_mix_id = ""
        self._current_mix_title = ""
        self._current_songs = []

    @Property("QVariantList", notify=dataChanged)
    def categories(self):
        return MIX_CATEGORIES

    @Property("QVariantList", notify=dataChanged)
    def currentSongs(self):
        return self._current_songs

    @Property(str, notify=dataChanged)
    def currentMixTitle(self):
        return self._current_mix_title

    @Slot(str)
    def loadMix(self, mix_id: str):
        self._current_mix_id = mix_id
        category = next((c for c in MIX_CATEGORIES if c["id"] == mix_id), None)
        self._current_mix_title = category["title"] if category else "Mix"
        self._current_songs = self._fetch_mock_songs(mix_id)
        self.dataChanged.emit()

    @Slot()
    def refresh(self):
        if self._current_mix_id:
            self.loadMix(self._current_mix_id)
        else:
            self.dataChanged.emit()

    def _fetch_mock_songs(self, mix_id: str):
        songs = []
        if self._db and hasattr(self._db, 'fetch_all'):
            all_items = self._db.fetch_all() or []
            if mix_id == "favorites":
                songs = all_items[:20]
            elif mix_id == "recent":
                songs = all_items[:15]
            elif mix_id == "most_played":
                songs = sorted(all_items, key=lambda x: getattr(x, 'play_count', 0) or 0, reverse=True)[:20]
            elif mix_id == "discover":
                songs = all_items[10:30] if len(all_items) > 30 else all_items
            elif mix_id in ("daily_mix", "ai_recommended"):
                songs = all_items[:25]
            else:
                songs = all_items[:15]
        return songs
