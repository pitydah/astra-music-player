"""Player Service — single facade between UI and GStreamer engine."""

from PySide6.QtCore import QObject, Signal, QTimer
from audio.player import GStreamerEngine, PlaybackState


class PlayerService(QObject):
    # ── Signals (relayed from engine) ──
    track_changed = Signal(str, str)    # title, artist
    state_changed = Signal(str)         # playing/paused/stopped
    position_changed = Signal(float)    # seconds
    duration_changed = Signal(float)    # seconds
    error_occurred = Signal(str)
    queue_changed = Signal(list)        # list[dict]
    finished = Signal()

    def __init__(self, engine: GStreamerEngine, parent=None):
        super().__init__(parent)
        self._engine = engine
        self._retry_url: str | None = None
        self._retry_title: str = ""
        self._retry_artist: str = ""
        self._retry_timer = QTimer(self)
        self._retry_timer.setSingleShot(True)
        self._retry_timer.timeout.connect(self._do_retry)

        # Relay engine signals
        self._engine.position_changed.connect(
            lambda s: self.position_changed.emit(s))
        self._engine.duration_changed.connect(
            lambda s: self.duration_changed.emit(s))
        self._engine.state_changed.connect(self._on_state)
        self._engine.queue_changed.connect(
            lambda q: self.queue_changed.emit(q))
        self._engine.finished.connect(
            lambda: self.finished.emit())

        # Streaming retry — intercept errors
        self._engine.error_occurred.connect(self._on_error)

    def _on_state(self, state: PlaybackState):
        s_map = {PlaybackState.PLAYING: "playing",
                 PlaybackState.PAUSED: "paused",
                 PlaybackState.STOPPED: "stopped"}
        s = s_map.get(state, "stopped")
        if s == "playing":
            self._retry_url = None
        self.state_changed.emit(s)

    def _on_error(self, msg: str):
        if self._retry_url:
            self._retry_timer.start(2000)
        else:
            self.error_occurred.emit(msg)

    def _do_retry(self):
        url = self._retry_url
        title = self._retry_title
        artist = self._retry_artist
        self._retry_url = None
        if url:
            self._engine.play_url(url)
            if title:
                self.track_changed.emit(title, artist)
            import logging
            logging.getLogger("astra.service").info(
                "Retrying stream: %s", url)

    # ── Core playback ──

    def play(self, filepath: str, title: str = "", artist: str = ""):
        self._retry_url = None
        self._engine.play(filepath)
        if title:
            self.track_changed.emit(title, artist)

    def toggle(self):
        self._engine.toggle()

    def stop(self):
        self._engine.stop()

    def seek(self, seconds: float):
        self._engine.seek(seconds)

    def set_volume(self, vol: int):
        self._engine.set_volume(vol)

    # ── Queue ──

    def play_next(self):
        self._engine.play_next()

    def play_prev(self):
        self._engine.play_prev()

    def enqueue(self, paths: list, play_now: bool = True):
        self._retry_url = None
        clean: list[str] = []
        for p in paths:
            if not p:
                continue
            if isinstance(p, str):
                clean.append(p)
        if not clean:
            self.error_occurred.emit("No hay archivos válidos para reproducir")
            return
        self._engine.enqueue(clean, play_now)

    def clear_queue(self):
        self._engine.clear_queue()

    def get_queue(self) -> list[dict]:
        return self._engine.get_queue()

    def reorder_queue(self, filepaths: list[str]):
        self._engine.reorder_queue(filepaths)

    # ── Modes ──

    def toggle_shuffle(self):
        self._engine.toggle_shuffle()

    def toggle_repeat(self) -> str:
        """Toggle repeat. Returns new mode: 'off', 'one', 'all'."""
        return self._engine.toggle_repeat()

    # ── Streaming ──

    def play_url(self, url: str, title: str = "", artist: str = ""):
        self._retry_url = url
        self._retry_title = title
        self._retry_artist = artist
        self._engine.play_url(url)
        if title:
            self.track_changed.emit(title, artist)

    # ── Output ──

    def set_output_device(self, device):
        self._engine.set_output_device(device)

    def get_output_device(self):
        return self._engine.get_output_device()

    # ── Accessors ──

    @property
    def state(self):
        return self._engine.state

    @property
    def current(self) -> str:
        """Current playing filepath or URL."""
        return self._engine._current

    @property
    def engine(self) -> GStreamerEngine:
        return self._engine
