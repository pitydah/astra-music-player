from PySide6.QtCore import QObject, Signal, Property, Slot


class PlaylistsBridge(QObject):
    dataChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._playlists = []

    @Property("QVariantList", notify=dataChanged)
    def playlists(self):
        return self._playlists

    @Slot()
    def refresh(self):
        self._playlists = [
            {"title": "Favoritas", "track_count": 12, "duration": "45:30", "cover_key": "fav"},
            {"title": "Descubrimientos", "track_count": 8, "duration": "32:15", "cover_key": "disc"},
            {"title": "Clásicos", "track_count": 20, "duration": "1:15:20", "cover_key": "classic"},
            {"title": "Para entrenar", "track_count": 15, "duration": "52:00", "cover_key": "gym"},
        ]
        self.dataChanged.emit()
