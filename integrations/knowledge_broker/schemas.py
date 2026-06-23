"""Type schemas for the Michi Knowledge Broker."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any


class ConsentState(Enum):
    ALLOWED = auto()
    OFFLINE_STRICT = auto()
    CACHE_ONLY = auto()
    SOURCE_DISABLED = auto()
    DENIED = auto()


@dataclass(slots=True)
class SourceInfo:
    name: str
    enabled: bool = False
    requires_consent: bool = True
    base_url: str = ""
    rate_limit: float = 1.0
    supports_offline_cache: bool = True
    license_note: str = ""


@dataclass
class KbArtist:
    id: int | None = None
    name: str = ""
    sort_name: str = ""
    mbid: str = ""
    wikidata_id: str = ""
    country: str = ""
    begin_date: str = ""
    end_date: str = ""
    artist_type: str = ""
    disambiguation: str = ""
    tags_json: str = "[]"
    relations_json: str = "[]"
    source: str = ""
    confidence: float = 1.0
    updated_at: str = ""


@dataclass
class KbAlbum:
    id: int | None = None
    title: str = ""
    artist_name: str = ""
    artist_mbid: str = ""
    release_group_mbid: str = ""
    release_mbid: str = ""
    date: str = ""
    year: str = ""
    country: str = ""
    primary_type: str = ""
    secondary_types_json: str = "[]"
    tags_json: str = "[]"
    cover_url: str = ""
    cover_path: str = ""
    source: str = ""
    confidence: float = 1.0
    updated_at: str = ""


@dataclass
class KbRecording:
    id: int | None = None
    title: str = ""
    artist_name: str = ""
    artist_mbid: str = ""
    recording_mbid: str = ""
    release_group_mbid: str = ""
    release_mbid: str = ""
    length_ms: int = 0
    isrc: str = ""
    tags_json: str = "[]"
    source: str = ""
    confidence: float = 1.0
    updated_at: str = ""


@dataclass
class KbWikiSummary:
    id: int | None = None
    entity_type: str = ""
    entity_key: str = ""
    language: str = ""
    title: str = ""
    summary: str = ""
    source_url: str = ""
    license: str = ""
    updated_at: str = ""


def dict_to_kb_artist(d: dict) -> KbArtist:
    return KbArtist(
        id=d.get("id"), name=str(d.get("name") or ""),
        sort_name=str(d.get("sort_name") or ""),
        mbid=str(d.get("mbid") or ""),
        wikidata_id=str(d.get("wikidata_id") or ""),
        country=str(d.get("country") or ""),
        begin_date=str(d.get("begin_date") or ""),
        end_date=str(d.get("end_date") or ""),
        artist_type=str(d.get("type") or ""),
        disambiguation=str(d.get("disambiguation") or ""),
        tags_json=str(d.get("tags_json") or "[]"),
        relations_json=str(d.get("relations_json") or "[]"),
        source=str(d.get("source") or ""),
        confidence=float(d.get("confidence", 1.0)),
        updated_at=str(d.get("updated_at") or ""),
    )


def dict_to_kb_album(d: dict) -> KbAlbum:
    return KbAlbum(
        id=d.get("id"), title=str(d.get("title") or ""),
        artist_name=str(d.get("artist_name") or ""),
        artist_mbid=str(d.get("artist_mbid") or ""),
        release_group_mbid=str(d.get("release_group_mbid") or ""),
        release_mbid=str(d.get("release_mbid") or ""),
        date=str(d.get("date") or ""), year=str(d.get("year") or ""),
        country=str(d.get("country") or ""),
        primary_type=str(d.get("primary_type") or ""),
        secondary_types_json=str(d.get("secondary_types_json") or "[]"),
        tags_json=str(d.get("tags_json") or "[]"),
        cover_url=str(d.get("cover_url") or ""),
        cover_path=str(d.get("cover_path") or ""),
        source=str(d.get("source") or ""),
        confidence=float(d.get("confidence", 1.0)),
        updated_at=str(d.get("updated_at") or ""),
    )


def kb_artist_to_dict(a: KbArtist) -> dict[str, Any]:
    return {
        "name": a.name, "sort_name": a.sort_name, "mbid": a.mbid,
        "country": a.country, "begin_date": a.begin_date,
        "end_date": a.end_date, "type": a.artist_type,
        "disambiguation": a.disambiguation,
        "source": a.source, "confidence": a.confidence,
    }


def kb_album_to_dict(a: KbAlbum) -> dict[str, Any]:
    return {
        "title": a.title, "artist_name": a.artist_name,
        "release_group_mbid": a.release_group_mbid,
        "date": a.date, "year": a.year, "country": a.country,
        "primary_type": a.primary_type, "cover_url": a.cover_url,
        "source": a.source, "confidence": a.confidence,
    }
