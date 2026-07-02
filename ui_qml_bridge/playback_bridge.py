from PySide6.QtCore import QObject, Signal, Property, Slot


class PlaybackBridge(QObject):
    stateChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._track_title = "—"
        self._track_artist = "—"
        self._track_album = "—"
        self._is_playing = False
        self._position = 0
        self._duration = 0
        self._volume = 80
        self._queue = []
        self._history = []

    @Property(str, notify=stateChanged)
    def trackTitle(self): return self._track_title

    @Property(str, notify=stateChanged)
    def trackArtist(self): return self._track_artist

    @Property(str, notify=stateChanged)
    def trackAlbum(self): return self._track_album

    @Property(bool, notify=stateChanged)
    def isPlaying(self): return self._is_playing

    @Property(int, notify=stateChanged)
    def position(self): return self._position

    @Property(int, notify=stateChanged)
    def duration(self): return self._duration

    @Property(int, notify=stateChanged)
    def volume(self): return self._volume

    @Property("QVariantList", notify=stateChanged)
    def queue(self): return self._queue

    @Property("QVariantList", notify=stateChanged)
    def history(self): return self._history

    @Slot()
    def togglePlay(self):
        self._is_playing = not self._is_playing
        self.stateChanged.emit()

    @Slot()
    def next(self):
        self.stateChanged.emit()

    @Slot()
    def previous(self):
        self.stateChanged.emit()

    @Slot(int)
    def setVolume(self, vol: int):
        self._volume = max(0, min(100, vol))
        self.stateChanged.emit()

    @Slot(int)
    def seek(self, pos: int):
        self._position = pos
        self.stateChanged.emit()
