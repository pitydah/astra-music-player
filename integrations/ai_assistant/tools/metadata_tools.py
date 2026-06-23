"""Metadata gap detection tool for Michi AI Assistant."""

from __future__ import annotations

from typing import Any

from integrations.ai_assistant.privacy_filter import sanitize_media_item
from integrations.ai_assistant.schemas import ToolResult


def find_metadata_gaps(db: Any, limit: int = 50) -> ToolResult:
    try:
        items = db.get_all() or [] if hasattr(db, "get_all") else []

        gaps: list[dict] = []
        max_items = min(limit, 200)

        for item in items:
            if len(gaps) >= max_items:
                break

            missing = _missing_fields(item)
            if missing:
                safe = sanitize_media_item(item)
                safe["missing_fields"] = missing
                gaps.append(safe)

        summary = _summarize_gaps(items)
        return ToolResult(
            name="find_metadata_gaps", success=True,
            data={
                "total_with_gaps": len(gaps),
                "results": gaps,
                "summary": summary,
            },
        )
    except Exception as e:
        return ToolResult(
            name="find_metadata_gaps", success=False, error=str(e),
        )


def _missing_fields(item) -> list[str]:
    missing = []
    title = (getattr(item, "title", "") or "").strip()
    artist = (getattr(item, "artist", "") or "").strip()
    album = (getattr(item, "album", "") or "").strip()
    genre = (getattr(item, "genre", "") or "").strip()
    year = getattr(item, "year", None)
    duration = getattr(item, "duration", None)

    if not title:
        missing.append("title")
    if not artist:
        missing.append("artist")
    if not album:
        missing.append("album")
    if not genre:
        missing.append("genre")
    if not year:
        missing.append("year")
    if not duration:
        missing.append("duration")
    return missing


def _summarize_gaps(items: list) -> dict:
    counts = {
        "title": 0, "artist": 0, "album": 0,
        "genre": 0, "year": 0, "duration": 0,
    }
    for item in items:
        for field in _missing_fields(item):
            counts[field] += 1
    return counts
