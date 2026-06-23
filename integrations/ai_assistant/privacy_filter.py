"""Privacy filter — strips sensitive fields before sending data to the LLM."""

from __future__ import annotations

import hashlib
import re
from typing import Any

SAFE_KEYS = frozenset({
    "id", "title", "artist", "album", "year", "genre",
    "duration", "format", "track_number", "disc_number",
    "composer", "albumartist", "bitrate", "sample_rate",
    "channels", "bit_depth", "bpm",
    "play_count", "mood", "grouping",
    "score", "reasons", "strategy",
})

FORBIDDEN_KEYS = frozenset({
    "filepath", "filename", "directory", "server_url",
    "token", "password", "secret", "local_ip", "api_key",
    "path", "file", "uri", "url",
    "access_token", "refresh_token", "bearer", "secret_key",
})

_IP_PATTERN = re.compile(
    r"(?:127\.\d+\.\d+\.\d+|10\.\d+\.\d+\.\d+|172\.(?:1[6-9]|2\d|3[01])\.\d+\.\d+|192\.168\.\d+\.\d+)"  # noqa: E501
)
_PATH_PATTERN = re.compile(r"/home/[^\s\"']+")
_URL_PATTERN = re.compile(r"https?://[^\s\"']+")


def hash_path(path: str) -> str:
    return "file_" + hashlib.sha256(path.encode()).hexdigest()[:12]


def sanitize_media_item(item: Any) -> dict[str, Any]:
    if isinstance(item, dict):
        data = item
    elif hasattr(item, "__dict__"):
        data = item.__dict__
    elif hasattr(item, "_asdict"):
        data = item._asdict()
    elif hasattr(item, "to_dict"):
        data = item.to_dict()
    else:
        data = {}

    safe: dict[str, Any] = {}
    for key in SAFE_KEYS:
        if key in data and data[key] is not None:
            safe[key] = data[key]
    if "ext" in data:
        safe["format"] = str(data["ext"]).lstrip(".")
    if "kind" in data and data["kind"] not in ("audio", None):
        safe["kind"] = data["kind"]
    return safe


def sanitize_text(text: str) -> str:
    text = _PATH_PATTERN.sub("[ruta local]", text)
    text = _IP_PATTERN.sub("[direccion local]", text)
    text = _URL_PATTERN.sub("[url omitida]", text)
    return text


def sanitize_results(results: list, limit: int = 30) -> list[dict[str, Any]]:
    return [sanitize_media_item(r) for r in results[:limit]]


def sanitize_for_prompt(data: dict | list) -> dict | list:
    if isinstance(data, list):
        return [sanitize_for_prompt(item) for item in data]
    if isinstance(data, dict):
        return {
            k: sanitize_for_prompt(v) if isinstance(v, (dict, list)) else v
            for k, v in data.items()
            if k not in FORBIDDEN_KEYS
        }
    return data
