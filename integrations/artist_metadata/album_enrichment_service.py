"""Album Enrichment Service — queries MusicBrainz + Cover Art Archive for album data."""
import time

from PySide6.QtCore import QObject, Signal, QTimer

from integrations.musicbrainz.client import MusicBrainzClient
from integrations.coverart.client import CoverArtClient
from integrations.artist_metadata.album_cache import AlbumCache
from metadata.album_summary import AlbumSummary


class _AlbumEnrichmentJob:
    """Tracks a single enrichment request through the async pipeline."""
    __slots__ = ("album_key", "artist", "album", "artist_mbid",
                 "release_group_mbid", "release_mbid", "created_at")

    def __init__(self, album_key, artist, album, mbid=""):
        self.album_key = album_key
        self.artist = artist
        self.album = album
        self.artist_mbid = mbid
        self.release_group_mbid = ""
        self.release_mbid = ""
        self.created_at = time.time()


def _match_album(local_title: str, remote_title: str) -> float:
    """Score how well a remote release-group title matches a local album name.
    Returns 0.0 (no match) to 1.0 (exact match)."""
    import re
    a = local_title.lower().strip()
    b = remote_title.lower().strip()
    # Remove basic punctuation for comparison
    a_clean = re.sub(r"[.,;:!?'\"()\[\]{}]", "", a)
    b_clean = re.sub(r"[.,;:!?'\"()\[\]{}]", "", b)
    if a_clean == b_clean:
        return 1.0
    if a in b or b in a:
        return 0.85
    # Word overlap
    a_words = set(a_clean.split())
    b_words = set(b_clean.split())
    if a_words and b_words:
        overlap = len(a_words & b_words) / len(a_words | b_words)
        if overlap > 0.6:
            return 0.65 + overlap * 0.2
    return 0.0


class AlbumEnrichmentService(QObject):
    album_enriched = Signal(str, object)     # album_key, AlbumSummary
    enrichment_failed = Signal(str, str)      # album_key, error
    enrichment_progress = Signal(int, int)    # current, total

    def __init__(self, parent=None):
        super().__init__(parent)
        self._client = MusicBrainzClient(self)
        self._cover = CoverArtClient(self)
        self._cache = AlbumCache(self)
        self._pending: list[_AlbumEnrichmentJob] = []
        self._active_job: _AlbumEnrichmentJob | None = None
        self._rate_limit = 1.0
        self._last_call = 0.0
        self._enabled = True

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._process_queue)
        self._timer.setInterval(600)

        self._client.artists_found.connect(self._on_album_info)
        self._client.albums_found.connect(self._on_release_groups)
        self._client.error_occurred.connect(self._on_error)
        self._cover.cover_found.connect(self._on_cover_found)

    def _is_online_allowed(self) -> bool:
        from core.settings_manager import get_bool
        if get_bool("artist_enrichment/offline_strict"):
            return False
        return get_bool("artist_enrichment/online_enabled")

    def _is_coverart_allowed(self) -> bool:
        from core.settings_manager import get_bool
        if not self._is_online_allowed():
            return False
        return get_bool("artist_enrichment/coverart_enabled")

    def enrich_album(self, album_key: str, artist: str, album: str, mbid: str = ""):
        if not self._enabled or not artist or not album:
            return
        if self._cache.is_negative(album_key):
            return  # skip known misses
        if not self._cache.is_stale(album_key, days=30):
            cached = self._cache.get_metadata(album_key)
            if cached and not cached.get("_not_found"):
                from metadata.album_info_repository import _dict_to_summary
                s = _dict_to_summary(cached)
                if s:
                    self.album_enriched.emit(album_key, s)
                    return
        # Check not already pending
        for j in self._pending:
            if j.album_key == album_key:
                return
        job = _AlbumEnrichmentJob(album_key, artist, album, mbid)
        self._pending.append(job)
        if not self._timer.isActive():
            self._timer.start()

    def enrich_visible(self, albums: list, limit: int = 12):
        for a in albums[:limit]:
            self.enrich_album(
                album_key=a.get("key", ""),
                artist=a.get("artist", ""),
                album=a.get("album", ""),
                mbid=a.get("mbid", ""))

    def _process_queue(self):
        if not self._pending:
            self._timer.stop()
            return
        now = time.time()
        if now - self._last_call < self._rate_limit:
            return

        self._active_job = self._pending.pop(0)
        self._last_call = time.time()

        if not self._is_online_allowed():
            self._cache.cache_not_found(self._active_job.album_key)
            self.enrichment_failed.emit(self._active_job.album_key, "Modo offline")
            self._active_job = None
            return

        mbid = self._active_job.artist_mbid
        if mbid:
            self._client.get_release_groups(mbid)
        else:
            self._client.search_artist(self._active_job.artist)
        self.enrichment_progress.emit(1, 1 + len(self._pending))

    def _on_album_info(self, results):
        job = self._active_job
        self._active_job = None
        if not job or not results:
            return
        info = results[0] if isinstance(results, list) and results else None
        if not info:
            self._cache.cache_not_found(job.album_key)
            return
        artist_name = info.get("name", job.artist)
        genre = info.get("genre", "")

        summary = AlbumSummary(
            album_key=job.album_key,
            title=job.album,
            artist=artist_name,
            genre=genre,
            style=info.get("style", ""),
            mood=info.get("mood", ""),
            source="musicbrainz",
        )
        self._cache.save_metadata(job.album_key, {
            "album_key": job.album_key, "album": job.album,
            "artist": artist_name, "genre": genre,
            "style": info.get("style", ""), "mood": info.get("mood", ""),
            "source": "musicbrainz",
        })
        self.album_enriched.emit(job.album_key, summary)

    def _on_release_groups(self, release_groups: list):
        job = self._active_job
        self._active_job = None
        if not job or not release_groups:
            return

        best_match = None
        best_score = 0.0
        for rg in release_groups:
            score = _match_album(job.album, rg.get("title", ""))
            if score > best_score:
                best_score = score
                best_match = rg

        if best_match and best_score >= 0.60:
            rg_mbid = best_match.get("id", "")
            # Enrich the original album_key, not a synthetic one
            self._cache.save_metadata(job.album_key, {
                "album_key": job.album_key,
                "album": job.album,
                "artist": job.artist,
                "musicbrainz_release_group_mbid": rg_mbid,
                "match_confidence": best_score,
                "source": "musicbrainz",
            })
            # Fetch cover art for the matched release-group
            if rg_mbid and self._is_coverart_allowed():
                self._cover.fetch_cover(job.album_key, rg_mbid)

            # Emit basic summary
            summary = AlbumSummary(
                album_key=job.album_key,
                title=job.album,
                artist=job.artist,
                source="musicbrainz",
                match_confidence=best_score,
            )
            self.album_enriched.emit(job.album_key, summary)
        else:
            self._cache.cache_not_found(job.album_key)

    def _on_cover_found(self, album_key: str, image_url: str):
        if not image_url:
            return
        cached = self._cache.get_metadata(album_key)
        cover_data = cached or {}
        cover_data["album_key"] = album_key
        cover_data["cover_url"] = image_url
        cover_data["cover_source"] = "coverartarchive"
        self._cache.save_metadata(album_key, cover_data)
        from metadata.album_info_repository import _dict_to_summary
        s = _dict_to_summary(cover_data)
        if s:
            self.album_enriched.emit(album_key, s)

    def _on_error(self, msg):
        job = self._active_job
        self._active_job = None
        if job:
            self._cache.cache_not_found(job.album_key)
            self.enrichment_failed.emit(job.album_key, msg)
