"""LocalSource — wraps LibraryDB as a MusicSource, with FTS5 search engine."""
from sources.base_source import MusicSource, TrackRef
from library.library_db import LibraryDB


class LocalSource(MusicSource):
    def __init__(self, db: LibraryDB):
        self._db = db
        self._engine = None  # lazy SearchEngine

    def list_tracks(self) -> list[TrackRef]:
        items = self._db.get_all()
        return self._to_refs(items)

    def search(self, query: str) -> list[TrackRef]:
        engine = self._get_engine()
        if engine:
            results = engine.search(query, limit=200)
            return self._dicts_to_refs(results)
        # Fallback to LIKE-based search when SearchEngine unavailable
        return self._to_refs(self._db.get_all(search=query))

    def _get_engine(self):
        if self._engine is None:
            try:
                from library.search_engine import SearchEngine
                self._engine = SearchEngine(self._db._conn)
            except Exception:
                pass
        return self._engine

    def _to_refs(self, items) -> list[TrackRef]:
        return [TrackRef(
            uri=i.filepath,
            title=i.title,
            artist=i.artist,
            album=i.album,
            duration=i.duration,
            cover_path="",
            track_number=i.track_number,
            year=i.year,
            genre=i.genre,
        ) for i in items]

    def _dicts_to_refs(self, rows: list[dict]) -> list[TrackRef]:
        return [TrackRef(
            uri=row.get("filepath", ""),
            title=row.get("title", ""),
            artist=row.get("artist", ""),
            album=row.get("album", ""),
            duration=row.get("duration", 0.0),
            cover_path="",
            track_number=row.get("track_number", 0),
            year=row.get("year", 0),
            genre=row.get("genre", ""),
        ) for row in rows]

    def get_artwork(self, track: TrackRef) -> str | None:
        return track.cover_path or None
