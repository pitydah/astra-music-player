"""Synchronous Cover Art Archive provider for KnowledgeBroker."""

from __future__ import annotations

import logging
import urllib.request
import urllib.error

logger = logging.getLogger("michi.knowledge_broker.coverart")

CA_BASE = "https://coverartarchive.org"
CA_USER_AGENT = "MichiMusicPlayer/0.1 (CoverArtArchive)"


class CoverArtSyncProvider:
    def __init__(self, timeout: int = 15):
        self._timeout = timeout

    def get_cover_url(self, release_group_mbid: str) -> str:
        if not release_group_mbid:
            return ""
        url = f"{CA_BASE}/release-group/{release_group_mbid}/front"
        req = urllib.request.Request(url, headers={"User-Agent": CA_USER_AGENT})
        try:
            resp = urllib.request.urlopen(req, timeout=self._timeout)
            final_url = resp.geturl()
            if final_url and final_url != url:
                return final_url
            return url
        except urllib.error.HTTPError as e:
            logger.debug("CoverArt %s for %s", e.code, release_group_mbid)
            return ""
        except Exception as e:
            logger.debug("CoverArt error for %s: %s", release_group_mbid, e)
            return ""

    def get_cover_by_release_mbid(self, release_mbid: str) -> str:
        if not release_mbid:
            return ""
        url = f"{CA_BASE}/release/{release_mbid}/front"
        req = urllib.request.Request(url, headers={"User-Agent": CA_USER_AGENT})
        try:
            resp = urllib.request.urlopen(req, timeout=self._timeout)
            final_url = resp.geturl()
            if final_url and final_url != url:
                return final_url
            return url
        except urllib.error.HTTPError as e:
            logger.debug("CoverArt release %s for %s", e.code, release_mbid)
            return ""
        except Exception as e:
            logger.debug("CoverArt error for %s: %s", release_mbid, e)
            return ""
