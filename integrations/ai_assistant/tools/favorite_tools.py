"""Favorite tools — mark/unmark tracks as favorites. REVERSIBLE, requires confirmation."""

from __future__ import annotations

from typing import Any

from integrations.ai_assistant.schemas import ToolResult


def _resolve_filepaths(db: Any, track_ids: list[int]) -> list[str]:
    filepaths: list[str] = []
    if not hasattr(db, "get_all") or not track_ids:
        return filepaths
    all_items = db.get_all() or []
    id_map = {item.id: item.filepath for item in all_items if getattr(item, "id", None)}
    for tid in track_ids:
        fp = id_map.get(tid)
        if fp:
            filepaths.append(fp)
    return filepaths


def mark_favorite(db: Any, track_ids: list[int]) -> ToolResult:
    try:
        if not track_ids:
            return ToolResult(
                name="mark_favorite", success=False,
                error="No se especificaron canciones.",
            )
        filepaths = _resolve_filepaths(db, track_ids)
        if not filepaths:
            return ToolResult(
                name="mark_favorite", success=False,
                error="No se encontraron las canciones en la biblioteca.",
            )
        changed = 0
        for fp in filepaths:
            if hasattr(db, "toggle_favorite"):
                result = db.toggle_favorite(fp)
                if result:
                    changed += 1
                    db.toggle_favorite(fp)  # toggle back, then force ON

        # Force favorite ON for all specified tracks
        changed = 0
        if hasattr(db, "toggle_favorite"):
            current = set(db.get_favorites() or [])
            for fp in filepaths:
                if fp not in current:
                    db.toggle_favorite(fp)
                    changed += 1

        return ToolResult(
            name="mark_favorite", success=True,
            data={
                "changed_count": changed,
                "total_requested": len(filepaths),
                "status": "favorites_updated",
            },
        )
    except Exception as e:
        return ToolResult(
            name="mark_favorite", success=False, error=str(e),
        )


def unmark_favorite(db: Any, track_ids: list[int]) -> ToolResult:
    try:
        if not track_ids:
            return ToolResult(
                name="unmark_favorite", success=False,
                error="No se especificaron canciones.",
            )
        filepaths = _resolve_filepaths(db, track_ids)
        if not filepaths:
            return ToolResult(
                name="unmark_favorite", success=False,
                error="No se encontraron las canciones en la biblioteca.",
            )
        changed = 0
        if hasattr(db, "toggle_favorite"):
            current = set(db.get_favorites() or [])
            for fp in filepaths:
                if fp in current:
                    db.toggle_favorite(fp)
                    changed += 1

        return ToolResult(
            name="unmark_favorite", success=True,
            data={
                "changed_count": changed,
                "total_requested": len(filepaths),
                "status": "favorites_updated",
            },
        )
    except Exception as e:
        return ToolResult(
            name="unmark_favorite", success=False, error=str(e),
        )
