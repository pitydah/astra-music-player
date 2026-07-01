"""Sanitizer — strip sensitive data from ecosystem diagnostics.

Safe for dicts, lists, dataclasses, and nested structures.
"""

from __future__ import annotations

from typing import Any

SENSITIVE_KEYS = frozenset({
    "path", "paths", "filepath", "filepaths", "uri", "uris",
    "token", "password", "secret", "api_key", "ha_token",
    "michi_api_token", "access_token", "refresh_token",
    "authorization", "bearer",
})

_SENSITIVE_PREFIXES = ("/", "/home/", "/Users/", "file://", "C:\\", "c:\\", "\\\\")
_MAX_STRING_LENGTH = 240
_MAX_LIST_ITEMS = 20


def sanitize_for_diagnostic(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: sanitize_for_diagnostic(v) for k, v in value.items() if k.lower() not in SENSITIVE_KEYS}
    if isinstance(value, (list, tuple)):
        return [sanitize_for_diagnostic(v) for v in value[:_MAX_LIST_ITEMS]]
    if isinstance(value, str):
        for prefix in _SENSITIVE_PREFIXES:
            if value.startswith(prefix):
                return value.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
        if len(value) > _MAX_STRING_LENGTH:
            return value[:_MAX_STRING_LENGTH] + "..."
        return value
    if hasattr(value, "__dataclass_fields__"):
        return sanitize_for_diagnostic({f.name: getattr(value, f.name) for f in value.__dataclass_fields__.values()})
    return value


def sanitize_report(report: dict[str, Any]) -> dict[str, Any]:
    return sanitize_for_diagnostic(report)
