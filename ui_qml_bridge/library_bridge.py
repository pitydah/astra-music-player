from PySide6.QtCore import QObject, Signal, Property, Slot


class LibraryBridge(QObject):
    dataChanged = Signal()

    def __init__(self, db=None, search_engine=None, playback_ctrl=None, parent=None):
        super().__init__(parent)
        self._db = db
        self._search_engine = search_engine
        self._playback_ctrl = playback_ctrl
        self._songs = []
        self._albums = []
        self._search_query = ""

    @Property(int, notify=dataChanged)
    def songCount(self):
        return len(self._songs)

    @Property(int, notify=dataChanged)
    def albumCount(self):
        return len(self._albums)

    @Slot(str)
    def search(self, query: str):
        self._search_query = query
        if self._search_engine and query:
            results = self._search_engine.search(query)
            self._songs = results if results else []
        elif self._db and not query:
            self._songs = self._db.fetch_all() if hasattr(self._db, 'fetch_all') else []
        self._refresh_albums()
        self.dataChanged.emit()

    @Slot()
    def refresh(self):
        if self._db:
            self._songs = self._db.fetch_all() if hasattr(self._db, 'fetch_all') else []
        self._refresh_albums()
        self.dataChanged.emit()

    @Slot(str)
    def play_song(self, filepath: str):
        if self._playback_ctrl and hasattr(self._playback_ctrl, 'play_file'):
            self._playback_ctrl.play_file(filepath)

    def _refresh_albums(self):
        seen = set()
        self._albums = []
        for s in self._songs:
            key = getattr(s, 'album_key', None) or getattr(s, 'album', '')
            if key and key not in seen:
                seen.add(key)
                self._albums.append(s)
