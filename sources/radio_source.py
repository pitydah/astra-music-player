"""RadioSource — wraps RadioManager as a MusicSource."""

from sources.base_source import MusicSource, TrackRef
from streaming.radio_manager import RadioManager


class RadioSource(MusicSource):
    def __init__(self, manager: RadioManager):
        self._manager = manager

    def list_tracks(self) -> list[TrackRef]:
        return self._to_refs(self._manager.get_all())

    def search(self, query: str) -> list[TrackRef]:
        q = query.lower()
        return [t for t in self.list_tracks()
                if q in t.title.lower()]

    def _to_refs(self, stations) -> list[TrackRef]:
        return [TrackRef(
            uri=s.url,
            title=s.name,
            artist="Radio",
            duration=0.0,
        ) for s in stations]

    def can_stream(self, track: TrackRef) -> bool:
        return True
