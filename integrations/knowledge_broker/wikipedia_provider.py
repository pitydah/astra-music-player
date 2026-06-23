"""Synchronous Wikipedia + Wikidata provider for KnowledgeBroker."""

from __future__ import annotations

import json
import logging
import urllib.request
import urllib.error

logger = logging.getLogger("michi.knowledge_broker.wikipedia")

WP_USER_AGENT = "MichiMusicPlayer/0.1 (https://github.com/pitydah/michi-music-player)"


class WikipediaSyncProvider:
    def __init__(self, timeout: int = 15, default_lang: str = "es"):
        self._timeout = timeout
        self._default_lang = default_lang

    def get_summary(self, title: str, lang: str = "") -> str:
        if not lang:
            lang = self._default_lang
        if not title.strip():
            return ""
        summary = self._fetch_summary_api(title, lang)
        if not summary and lang != "en":
            summary = self._fetch_summary_api(title, "en")
        return summary

    def _fetch_summary_api(self, title: str, lang: str) -> str:
        encoded = urllib.request.quote(title.replace(" ", "_"))
        url = (
            f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/"
            f"{encoded}"
        )
        req = urllib.request.Request(url, headers={
            "User-Agent": WP_USER_AGENT,
            "Accept": "application/json",
        })
        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                extract = data.get("extract", "")
                if extract and len(extract) > 2000:
                    extract = extract[:2000] + "..."
                return extract
        except urllib.error.HTTPError as e:
            logger.debug("Wikipedia HTTP %s for %s (%s)", e.code, title, lang)
            return ""
        except Exception as e:
            logger.debug("Wikipedia error for %s (%s): %s", title, lang, e)
            return ""

    def get_image_url(self, title: str, lang: str = "") -> str:
        if not lang:
            lang = self._default_lang
        if not title.strip():
            return ""
        image_url = self._fetch_wikidata_image(title, lang)
        if not image_url and lang != "en":
            image_url = self._fetch_wikidata_image(title, "en")
        return image_url

    def _fetch_wikidata_image(self, title: str, lang: str) -> str:
        encoded = urllib.request.quote(title.replace(" ", "_"))
        url = (
            f"https://www.wikidata.org/w/api.php"
            f"?action=wbgetentities"
            f"&sites={lang}wiki"
            f"&titles={encoded}"
            f"&props=claims"
            f"&format=json"
        )
        req = urllib.request.Request(url, headers={"User-Agent": WP_USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                entities = data.get("entities", {})
                for _qid, entity in entities.items():
                    claims = entity.get("claims", {})
                    p18 = claims.get("P18", [])
                    if p18:
                        filename = p18[0]["mainsnak"]["datavalue"]["value"]
                        return (
                            "https://commons.wikimedia.org/wiki/Special:FilePath/"
                            + urllib.request.quote(filename.replace(" ", "_"))
                            + "?width=500"
                        )
            return ""
        except Exception as e:
            logger.debug("Wikidata error for %s: %s", title, e)
            return ""

    def get_source_url(self, title: str, lang: str = "es") -> str:
        encoded = urllib.request.quote(title.replace(" ", "_"))
        return f"https://{lang}.wikipedia.org/wiki/{encoded}"
