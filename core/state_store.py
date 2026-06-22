"""AppStateStore — thread-safe snapshots of player state for API consumption."""
from dataclasses import dataclass, asdict
from PySide6.QtCore import QObject, Signal


@dataclass
class PlayerSnapshot:
    state: str = "idle"
    title: str = ""
    artist: str = ""
    album: str = ""
    duration: int = 0
    position: int = 0
    volume: int = 70
    source_type: str = "local_file"
    source_label: str = ""
    destination: str = "local"
    cover_url: str = ""


class AppStateStore(QObject):
    """Thread-safe state store. Updated from main thread, read from any thread."""

    snapshot_updated = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._player = PlayerSnapshot()
        self._destinations: list[dict] = []
        self._ha_connected = False
        self._ha_devices: list[dict] = []

    def player_snapshot(self) -> dict:
        return asdict(self._player)

    def destinations_snapshot(self) -> list[dict]:
        return list(self._destinations)

    def update_player(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self._player, k):
                setattr(self._player, k, v)

    def update_destinations(self, dests: list[dict]):
        self._destinations = list(dests)

    def update_ha_state(self, connected: bool, devices: list[dict] = None):
        self._ha_connected = connected
        if devices is not None:
            self._ha_devices = list(devices)
