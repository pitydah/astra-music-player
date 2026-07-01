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

    @Property("QVariantList", notify=dataChanged)
    def songs(self):
        result = []
        for s in self._songs[:500]:
            result.append({
                "title": getattr(s, 'title', None) or getattr(s, 'filepath', '') or '',
                "artist": getattr(s, 'artist', '') or '',
                "album": getattr(s, 'album', '') or '',
                "album_key": getattr(s, 'album_key', '') or '',
                "duration": getattr(s, 'duration', 0) or 0,
                "filepath": getattr(s, 'filepath', '') or '',
                "format": getattr(s, 'format', '') or '',
                "cover_key": getattr(s, 'album_key', '') or getattr(s, 'filepath', '') or '',
            })
        return result

    @Property("QVariantList", notify=dataChanged)
    def albums(self):
        result = []
        for a in self._albums[:200]:
            key = getattr(a, 'album_key', None) or getattr(a, 'album', '') or ''
            result.append({
                "title": getattr(a, 'album', '') or key,
                "artist": getattr(a, 'artist', '') or '',
                "album_key": key,
                "year": getattr(a, 'year', 0) or 0,
                "track_count": getattr(a, 'track_count', 0) or 0,
                "cover_key": key,
            })
        return result

    @Slot(str)
    def search(self, query: str):
        self._search_query = query
        if self._search_engine and query:
            results = self._search_engine.search(query)
            self._songs = results if results else []
        elif self._db and not query:
            if hasattr(self._db, 'fetch_all'):
                self._songs = self._db.fetch_all() or []
        self._refresh_albums()
        self.dataChanged.emit()

    @Slot()
    def refresh(self):
        if self._db and hasattr(self._db, 'fetch_all'):
            self._songs = self._db.fetch_all() or []
        self._refresh_albums()
        self.dataChanged.emit()

    def _refresh_albums(self):
        seen = {}
        self._albums = []
        for s in self._songs:
            key = getattr(s, 'album_key', None) or getattr(s, 'album', '') or ''
            if key and key not in seen:
                seen[key] = True
                self._albums.append(s)
