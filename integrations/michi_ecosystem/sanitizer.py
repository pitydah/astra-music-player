"""Sanitizer — strip sensitive data from ecosystem diagnostics."""

from __future__ import annotations

from typing import Any

SENSITIVE_KEYS = frozenset({
    "path", "paths", "filepath", "filepaths", "uri", "uris",
    "token", "password", "secret", "api_key", "ha_token",
    "michi_api_token", "access_token", "refresh_token",
})

_MAX_STRING_LENGTH = 300
_MAX_LIST_ITEMS = 10


def sanitize_for_diagnostic(value: Any) -> Any:
    if isinstance(value, dict):
        clean = {}
        for k, v in value.items():
            if k.lower() in SENSITIVE_KEYS:
                continue
            clean[k] = sanitize_for_diagnostic(v)
        return clean
    if isinstance(value, list):
        return [sanitize_for_diagnostic(v) for v in value[:_MAX_LIST_ITEMS]]
    if isinstance(value, str):
        if any(value.startswith(p) for p in ("/", "file://", "C:\\", "c:\\")):
            return value.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
        if len(value) > _MAX_STRING_LENGTH:
            return value[:_MAX_STRING_LENGTH] + "..."
        return value
    return value


def sanitize_report(report: dict[str, Any]) -> dict[str, Any]:
    return sanitize_for_diagnostic(report)
