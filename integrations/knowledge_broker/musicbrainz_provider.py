"""Synchronous MusicBrainz provider — urllib-based, rate-limited, for KnowledgeBroker."""

from __future__ import annotations

import json
import logging
import time
import urllib.request
import urllib.error
from typing import Any

from integrations.knowledge_broker.schemas import KbArtist, KbAlbum

logger = logging.getLogger("michi.knowledge_broker.musicbrainz")

MB_BASE = "https://musicbrainz.org/ws/2"
MB_USER_AGENT = "MichiMusicPlayer/0.1 (https://github.com/pitydah/michi-music-player)"


class MusicBrainzSyncProvider:
    def __init__(self, rate_limit: float = 1.0, timeout: int = 15):
        self._rate_limit = rate_limit
        self._timeout = timeout
        self._last_call = 0.0

    def _rate_gate(self):
        elapsed = time.time() - self._last_call
        if elapsed < self._rate_limit:
            time.sleep(self._rate_limit - elapsed)
        self._last_call = time.time()

    def _get(self, path: str) -> dict:
        self._rate_gate()
        url = f"{MB_BASE}{path}"
        req = urllib.request.Request(url, headers={"User-Agent": MB_USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            logger.warning("MB HTTP %s for %s", e.code, url)
            return {}
        except Exception as e:
            logger.warning("MB error for %s: %s", url, e)
            return {}

    def search_artist(self, name: str, limit: int = 5) -> list[KbArtist]:
        encoded = urllib.request.quote(name)
        data = self._get(
            f"/artist?query=artist:{encoded}&fmt=json&limit={limit}"
        )
        artists = []
        for raw in (data.get("artists") or []):
            a = _parse_mb_artist(raw)
            if a.name:
                artists.append(a)
        return artists

    def get_artist_by_mbid(self, mbid: str) -> KbArtist | None:
        data = self._get(
            f"/artist/{mbid}?inc=tags+genres+url-rels+aliases&fmt=json"
        )
        if data.get("id"):
            return _parse_mb_artist(data)
        return None

    def get_release_groups(self, artist_mbid: str, limit: int = 50) -> list[KbAlbum]:
        data = self._get(
            f"/release-group?artist={artist_mbid}&type=Album&limit={limit}&fmt=json"
        )
        albums = []
        for raw in (data.get("release-groups") or []):
            a = _parse_mb_release_group(raw, artist_mbid)
            if a.title:
                albums.append(a)
        return albums

    def search_release_group(self, title: str, artist: str = "",
                             limit: int = 5) -> list[KbAlbum]:
        encoded = urllib.request.quote(title)
        if artist:
            encoded += f"+AND+artist:{urllib.request.quote(artist)}"
        data = self._get(
            f"/release-group?query=releasegroup:{encoded}&limit={limit}&fmt=json"
        )
        albums = []
        for raw in (data.get("release-groups") or []):
            a = _parse_mb_release_group(raw, "")
            if a.title:
                albums.append(a)
        return albums

    def search_recording(self, title: str, artist: str = "",
                         limit: int = 5) -> list[dict[str, Any]]:
        encoded = urllib.request.quote(title)
        if artist:
            encoded += f"+AND+artist:{urllib.request.quote(artist)}"
        data = self._get(
            f"/recording?query={encoded}&limit={limit}&fmt=json"
        )
        recordings = []
        for raw in (data.get("recordings") or []):
            recordings.append(raw)
        return recordings


def _parse_mb_artist(raw: dict) -> KbArtist:
    tags = [t.get("name", "") for t in (raw.get("tags") or [])]
    relations = [r.get("type", "") for r in (raw.get("relations") or [])]
    url_rels = (raw.get("url-rels") or raw.get("url_rels") or [])
    for u in url_rels:
        if u.get("type") == "wikipedia" and u.get("resource"):
            pass  # kept for future reference
    begin = raw.get("life-span", {}).get("begin", "") or ""
    end = raw.get("life-span", {}).get("end", "") or ""
    return KbArtist(
        name=raw.get("name", ""),
        sort_name=raw.get("sort-name", ""),
        mbid=raw.get("id", ""),
        country=raw.get("country", "") or raw.get("area", {}).get("name", ""),
        begin_date=begin,
        end_date=end,
        artist_type=raw.get("type", ""),
        disambiguation=raw.get("disambiguation", ""),
        tags_json=json.dumps(tags, ensure_ascii=False),
        relations_json=json.dumps(relations, ensure_ascii=False),
        source="musicbrainz",
        confidence=1.0,
    )


def _parse_mb_release_group(raw: dict, artist_mbid: str) -> KbAlbum:
    return KbAlbum(
        title=raw.get("title", ""),
        artist_mbid=artist_mbid,
        release_group_mbid=raw.get("id", ""),
        date=raw.get("first-release-date", ""),
        year=(raw.get("first-release-date", "") or "")[:4],
        primary_type=raw.get("primary-type", ""),
        secondary_types_json=json.dumps(raw.get("secondary-types") or [], ensure_ascii=False),
        tags_json=json.dumps([t.get("name", "") for t in (raw.get("tags") or [])], ensure_ascii=False),
        source="musicbrainz",
        confidence=1.0,
    )
