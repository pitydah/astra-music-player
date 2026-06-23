"""KnowledgeBrokerService — orchestrates cache, consent, and providers for AI Assistant."""

from __future__ import annotations

import logging
from typing import Any

from integrations.knowledge_broker.cache_repository import KnowledgeCacheRepository
from integrations.knowledge_broker.consent_manager import ConsentManager
from integrations.knowledge_broker.coverart_provider import CoverArtSyncProvider
from integrations.knowledge_broker.musicbrainz_provider import MusicBrainzSyncProvider
from integrations.knowledge_broker.sanitizer import (
    sanitize_external_text,
    wrap_for_llm,
)
from integrations.knowledge_broker.schemas import (
    ConsentState,
    KbWikiSummary,
    kb_artist_to_dict,
    kb_album_to_dict,
)
from integrations.knowledge_broker.wikipedia_provider import WikipediaSyncProvider

logger = logging.getLogger("michi.knowledge_broker.service")


class KnowledgeBrokerService:
    def __init__(self):
        self._cache = KnowledgeCacheRepository()
        self._consent = ConsentManager()
        self._mb = MusicBrainzSyncProvider()
        self._ca = CoverArtSyncProvider()
        self._wiki = WikipediaSyncProvider(default_lang=self._consent.wiki_language)

    @property
    def consent_summary(self) -> dict[str, Any]:
        return self._consent.state_summary()

    # ── Artist ──

    def lookup_artist(self, name: str, mbid: str = "") -> dict[str, Any]:
        cached = self._cache.find_artist(mbid if mbid else name)
        if cached:
            return {
                "source": "cache",
                "data": wrap_for_llm(kb_artist_to_dict(cached)),
            }

        if self._consent.can_use_musicbrainz() != ConsentState.ALLOWED:
            return {
                "source": "none",
                "status": self._consent.can_use_musicbrainz().name.lower(),
                "message": self._offline_message(),
                "data": None,
            }

        if mbid:
            artist = self._mb.get_artist_by_mbid(mbid)
            results = [artist] if artist else []
        else:
            results = self._mb.search_artist(name, limit=3)

        if not results:
            self._cache.add_negative("artist", name, "not_found_mb", source="musicbrainz")
            self._cache.log_source("musicbrainz", "search_artist", name, "empty")
            return {
                "source": "musicbrainz",
                "status": "not_found",
                "message": f"No se encontro informacion para '{name}' en MusicBrainz.",
                "data": None,
            }

        best = results[0]
        self._cache.upsert_artist(best)
        self._cache.log_source("musicbrainz", "search_artist", name, "success")

        return {
            "source": "musicbrainz",
            "data": wrap_for_llm(kb_artist_to_dict(best)),
        }

    def refresh_artist(self, name: str, mbid: str = "") -> dict[str, Any]:
        if self._consent.can_use_musicbrainz() != ConsentState.ALLOWED:
            return {
                "source": "none",
                "status": self._consent.can_use_musicbrainz().name.lower(),
                "message": self._offline_message(),
                "data": None,
            }

        if mbid:
            artist = self._mb.get_artist_by_mbid(mbid)
            if not artist:
                results = self._mb.search_artist(name, limit=1)
                artist = results[0] if results else None
        else:
            results = self._mb.search_artist(name, limit=3)
            artist = results[0] if results else None

        if artist:
            self._cache.upsert_artist(artist)
            self._cache.log_source("musicbrainz", "refresh_artist", name, "success")
            return {
                "source": "musicbrainz",
                "status": "refreshed",
                "data": wrap_for_llm(kb_artist_to_dict(artist)),
            }

        self._cache.add_negative("artist", name, "refresh_not_found", source="musicbrainz")
        self._cache.log_source("musicbrainz", "refresh_artist", name, "empty")
        return {
            "source": "musicbrainz",
            "status": "not_found",
            "message": f"No se encontro '{name}' en MusicBrainz.",
            "data": None,
        }

    def explain_artist(self, name: str, mbid: str = "",
                       wiki_lang: str = "es") -> dict[str, Any]:
        result = self.lookup_artist(name, mbid)
        artist_data = result.get("data")
        artist_name = name
        entity_key = mbid or name.lower().strip()

        if artist_data and isinstance(artist_data, dict):
            inner = artist_data.get("data", artist_data)
            artist_name = inner.get("name", name)

        cached_wiki = self._cache.find_wiki_summary("artist", entity_key, wiki_lang)
        if cached_wiki and cached_wiki.summary:
            return {
                "source": "cache",
                "provider": "wikipedia",
                "artist": artist_data,
                "summary": sanitize_external_text(cached_wiki.summary),
                "language": cached_wiki.language,
                "source_url": cached_wiki.source_url,
            }

        if self._consent.can_use_wikipedia() != ConsentState.ALLOWED:
            return {
                "source": result.get("source", "cache"),
                "artist": artist_data,
                "summary": "",
                "message": self._offline_message(),
            }

        summary_text = self._wiki.get_summary(artist_name, wiki_lang)
        if summary_text:
            cleaned = sanitize_external_text(summary_text)
            ws = KbWikiSummary(
                entity_type="artist", entity_key=entity_key, language=wiki_lang,
                title=artist_name, summary=cleaned,
                source_url=self._wiki.get_source_url(artist_name, wiki_lang),
                license="CC BY-SA 3.0",
            )
            self._cache.upsert_wiki_summary(ws)
            self._cache.log_source("wikipedia", "explain_artist", entity_key, "success")
            return {
                "source": "wikipedia",
                "provider": "wikipedia",
                "artist": artist_data,
                "summary": sanitize_external_text(cleaned),
                "language": wiki_lang,
                "source_url": ws.source_url,
            }

        self._cache.log_source("wikipedia", "explain_artist", entity_key, "empty")
        return {
            "source": result.get("source", "cache"),
            "artist": artist_data,
            "summary": "",
            "message": "No se encontro resumen en Wikipedia.",
        }

    # ── Album ──

    def lookup_album(self, title: str, artist: str = "",
                     release_group_mbid: str = "") -> dict[str, Any]:
        if release_group_mbid:
            cached = self._cache.find_album_by_mbid(release_group_mbid)
        else:
            cached = self._cache.find_album(title, artist)
        if cached:
            return {
                "source": "cache",
                "data": wrap_for_llm(kb_album_to_dict(cached)),
            }

        if self._consent.can_use_musicbrainz() != ConsentState.ALLOWED:
            return {
                "source": "none",
                "status": self._consent.can_use_musicbrainz().name.lower(),
                "message": self._offline_message(),
                "data": None,
            }

        results = self._mb.search_release_group(title, artist, limit=5)
        if not results:
            query = f"{artist} - {title}" if artist else title
            self._cache.add_negative("album", query, "not_found_mb", source="musicbrainz")
            self._cache.log_source("musicbrainz", "search_release_group", query, "empty")
            return {
                "source": "musicbrainz",
                "status": "not_found",
                "message": f"No se encontro '{title}' en MusicBrainz.",
                "data": None,
            }

        best = results[0]
        if best.release_group_mbid:
            cover_url = self._ca.get_cover_url(best.release_group_mbid)
            if cover_url:
                best.cover_url = cover_url

        self._cache.upsert_album(best)
        self._cache.log_source("musicbrainz", "search_release_group", title, "success")

        return {
            "source": "musicbrainz",
            "data": wrap_for_llm(kb_album_to_dict(best)),
        }

    def refresh_album(self, title: str, artist: str = "",
                      release_group_mbid: str = "") -> dict[str, Any]:
        if self._consent.can_use_musicbrainz() != ConsentState.ALLOWED:
            return {
                "source": "none",
                "status": self._consent.can_use_musicbrainz().name.lower(),
                "message": self._offline_message(),
                "data": None,
            }

        if release_group_mbid:
            self._cache.find_album_by_mbid(release_group_mbid)

        results = self._mb.search_release_group(title, artist, limit=5)
        if results:
            best = results[0]
            if best.release_group_mbid:
                cover_url = self._ca.get_cover_url(best.release_group_mbid)
                if cover_url:
                    best.cover_url = cover_url
            self._cache.upsert_album(best)
            self._cache.log_source("musicbrainz", "refresh_album", title, "success")
            return {
                "source": "musicbrainz",
                "status": "refreshed",
                "data": wrap_for_llm(kb_album_to_dict(best)),
            }

        self._cache.log_source("musicbrainz", "refresh_album", title, "empty")
        return {
            "source": "musicbrainz",
            "status": "not_found",
            "message": f"No se encontro '{title}' en MusicBrainz.",
            "data": None,
        }

    def explain_album(self, title: str, artist: str = "",
                      wiki_lang: str = "es") -> dict[str, Any]:
        result = self.lookup_album(title, artist)
        album_data = result.get("data")
        search_title = f"{artist} - {title}" if artist else title
        entity_key = search_title.lower().strip()

        cached_wiki = self._cache.find_wiki_summary("album", entity_key, wiki_lang)
        if cached_wiki and cached_wiki.summary:
            return {
                "source": "cache",
                "provider": "wikipedia",
                "album": album_data,
                "summary": sanitize_external_text(cached_wiki.summary),
                "language": cached_wiki.language,
                "source_url": cached_wiki.source_url,
            }

        if self._consent.can_use_wikipedia() != ConsentState.ALLOWED:
            return {
                "source": result.get("source", "cache"),
                "album": album_data,
                "summary": "",
                "message": self._offline_message(),
            }

        wiki_title = search_title if artist else title
        summary_text = self._wiki.get_summary(wiki_title, wiki_lang)
        if summary_text:
            cleaned = sanitize_external_text(summary_text)
            ws = KbWikiSummary(
                entity_type="album", entity_key=entity_key, language=wiki_lang,
                title=wiki_title, summary=cleaned,
                source_url=self._wiki.get_source_url(wiki_title, wiki_lang),
                license="CC BY-SA 3.0",
            )
            self._cache.upsert_wiki_summary(ws)
            self._cache.log_source("wikipedia", "explain_album", entity_key, "success")
            return {
                "source": "wikipedia",
                "provider": "wikipedia",
                "album": album_data,
                "summary": sanitize_external_text(cleaned),
                "language": wiki_lang,
                "source_url": ws.source_url,
            }

        self._cache.log_source("wikipedia", "explain_album", entity_key, "empty")
        return {
            "source": result.get("source", "cache"),
            "album": album_data,
            "summary": "",
            "message": "No se encontro resumen en Wikipedia.",
        }

    # ── Track / Recording ──

    def lookup_recording(self, title: str, artist: str = "",
                         recording_mbid: str = "") -> dict[str, Any]:
        if recording_mbid:
            cached = self._cache.find_recording(recording_mbid)
            if cached:
                return {
                    "source": "cache",
                    "data": wrap_for_llm({
                        "title": cached.title, "artist_name": cached.artist_name,
                        "recording_mbid": cached.recording_mbid,
                        "length_ms": cached.length_ms, "isrc": cached.isrc,
                        "source": cached.source,
                    }),
                }

        if self._consent.can_use_musicbrainz() != ConsentState.ALLOWED:
            return {
                "source": "none",
                "status": self._consent.can_use_musicbrainz().name.lower(),
                "message": self._offline_message(),
                "data": None,
            }

        results = self._mb.search_recording(title, artist, limit=3)
        if not results:
            return {
                "source": "musicbrainz",
                "status": "not_found",
                "message": f"No se encontro '{title}' en MusicBrainz.",
                "data": None,
            }

        raw = results[0]
        rec_mbid = raw.get("id", "")
        from integrations.knowledge_broker.schemas import KbRecording
        recording = KbRecording(
            title=raw.get("title", title),
            artist_name=raw.get("artist-credit", [{}])[0].get("name", artist) if raw.get("artist-credit") else artist,
            recording_mbid=rec_mbid,
            release_group_mbid=raw.get("release-group", {}).get("id", "") if raw.get("release-group") else "",
            release_mbid=raw.get("release", {}).get("id", "") if raw.get("release") else "",
            length_ms=raw.get("length", 0) or 0,
            isrc=raw.get("isrc", ""),
            tags_json="[]",
            source="musicbrainz",
            confidence=1.0,
        )
        self._cache.upsert_recording(recording)
        self._cache.log_source("musicbrainz", "search_recording", title, "success")

        return {
            "source": "musicbrainz",
            "data": wrap_for_llm({
                "title": recording.title, "artist_name": recording.artist_name,
                "recording_mbid": rec_mbid, "length_ms": recording.length_ms,
                "isrc": recording.isrc, "source": "musicbrainz",
            }),
        }

    # ── Helpers ──

    @staticmethod
    def _offline_message() -> str:
        return (
            "La informacion externa esta desactivada. "
            "Puedes activarla en Configuracion > Asistente IA."
        )
