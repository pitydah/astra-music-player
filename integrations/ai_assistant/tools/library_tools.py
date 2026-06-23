"""Library search tools for Michi AI Assistant."""

from __future__ import annotations

from typing import Any

from integrations.ai_assistant.privacy_filter import sanitize_results
from integrations.ai_assistant.schemas import ToolResult


def search_library(db: Any, query: str, filters: dict | None = None,
                   limit: int = 30) -> ToolResult:
    try:
        max_items = min(limit, 100)
        items = []

        if hasattr(db, "search_advanced"):
            items = db.search_advanced(query, limit=max_items)
        elif hasattr(db, "get_all"):
            items = db.get_all(search=query)

        if filters and items:
            items = _apply_filters(items, filters)

        safe = sanitize_results(items[:max_items], max_items)
        return ToolResult(name="search_library", success=True,
                          data={"total": len(safe), "results": safe})
    except Exception as e:
        return ToolResult(name="search_library", success=False, error=str(e))


def recommend_local_tracks(db: Any, seed_text: str,
                           limit: int = 20) -> ToolResult:
    try:
        seed_lower = seed_text.lower()
        candidates: list = []
        if hasattr(db, "get_all"):
            candidates = db.get_all(search=seed_text)

        scored: list[dict] = []
        for item in candidates:
            score = _score_match(item, seed_lower)
            if score > 0:
                safe = sanitize_results([item], 1)[0]
                safe["_score"] = score
                scored.append(safe)

        scored.sort(key=lambda x: x.pop("_score", 0), reverse=True)
        max_items = min(limit, 100)
        return ToolResult(
            name="recommend_local_tracks", success=True,
            data={"total": len(scored[:max_items]),
                  "results": scored[:max_items]},
        )
    except Exception as e:
        return ToolResult(
            name="recommend_local_tracks", success=False, error=str(e),
        )


def _apply_filters(items: list, filters: dict) -> list:
    for key, value in filters.items():
        if not value:
            continue
        v = str(value).lower()
        kept: list = []
        for item in items:
            attr = getattr(item, key, None) or ""
            if v in str(attr).lower():
                kept.append(item)
        items = kept
    return items


def _score_match(item, seed_lower: str) -> int:
    score = 0
    title = str(getattr(item, "title", "")).lower()
    artist = str(getattr(item, "artist", "")).lower()
    album = str(getattr(item, "album", "")).lower()
    genre = str(getattr(item, "genre", "")).lower()

    if seed_lower in title:
        score += 5
    if seed_lower in artist:
        score += 4
    if seed_lower in album:
        score += 3
    if seed_lower in genre:
        score += 2
    if any(token in artist for token in seed_lower.split()):
        score += 2
    if any(token in title for token in seed_lower.split()):
        score += 2
    return score
