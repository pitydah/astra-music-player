"""Privacy guard — sanitize and validate data before sending to LLM.

Centralizes all privacy checks for the AI Assistant.
"""

from __future__ import annotations

from typing import Any

_SENSITIVE_KEYS = frozenset({
    "path", "paths", "filepath", "filepaths", "uri", "uris",
    "token", "password", "secret", "api_key", "ha_token",
    "michi_api_token", "access_token", "refresh_token",
    "authorization", "bearer",
})

_SENSITIVE_PREFIXES = ("/", "/home", "/Users", "file://", "C:\\", "c:\\", "Bearer ")


def sanitize_for_assistant(data: Any) -> Any:
    if isinstance(data, dict):
        return {k: sanitize_for_assistant(v) for k, v in data.items() if k.lower() not in _SENSITIVE_KEYS}
    if isinstance(data, (list, tuple)):
        return [sanitize_for_assistant(v) for v in data[:10]]
    if isinstance(data, str):
        for prefix in _SENSITIVE_PREFIXES:
            if data.startswith(prefix):
                return "[redacted]"
        if len(data) > 200:
            return data[:200] + "..."
        return data
    return data


def assert_no_sensitive_data(data: Any, path: str = "") -> None:
    if isinstance(data, dict):
        for k, v in data.items():
            if k.lower() in _SENSITIVE_KEYS:
                raise ValueError(f"Sensitive key '{k}' found at {path}")
            assert_no_sensitive_data(v, f"{path}.{k}")
    elif isinstance(data, (list, tuple)):
        for i, v in enumerate(data):
            assert_no_sensitive_data(v, f"{path}[{i}]")
    elif isinstance(data, str):
        for prefix in _SENSITIVE_PREFIXES:
            if data.startswith(prefix):
                raise ValueError(f"Sensitive path pattern at {path}: {data[:50]}")


def is_local_ollama_url(url: str) -> bool:
    import re
    return bool(re.match(r"^https?://(127\.0\.0\.1|localhost|::1)(:\d+)?(/.*)?$", url))
