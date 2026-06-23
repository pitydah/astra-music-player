"""Playlist tools for Michi AI Assistant — draft + create from draft."""

from __future__ import annotations

import uuid
from typing import Any

from integrations.ai_assistant.privacy_filter import sanitize_results
from integrations.ai_assistant.schemas import ToolResult


def draft_playlist(db: Any, description: str, filters: dict | None = None,
                   limit: int = 30) -> ToolResult:
    try:
        items: list = []
        if filters:
            items = _collect_filtered(db, filters, min(limit, 100))
        elif description:
            items = _collect_by_description(db, description, min(limit, 100))
        else:
            items = _collect_random(db, min(limit, 100))

        if not items:
            return ToolResult(
                name="draft_playlist", success=False,
                error="No se encontraron canciones para el borrador.",
            )

        safe = sanitize_results(items, min(limit, 100))
        title = _derive_title(description, filters)
        draft_id = str(uuid.uuid4())[:8]

        return ToolResult(
            name="draft_playlist", success=True,
            data={
                "draft_id": draft_id,
                "title": title,
                "description": description or "Borrador generado por Michi Assistant",
                "count": len(safe),
                "tracks": safe,
            },
        )
    except Exception as e:
        return ToolResult(
            name="draft_playlist", success=False, error=str(e),
        )


def _collect_filtered(db, filters: dict, limit: int) -> list:
    all_items: list = []
    if hasattr(db, "get_all"):
        all_items = db.get_all()
    kept: list = []
    for item in all_items:
        match = True
        for key, value in filters.items():
            v = str(value).lower()
            attr = str(getattr(item, key, "") or "").lower()
            if v not in attr:
                match = False
                break
        if match:
            kept.append(item)
            if len(kept) >= limit:
                break
    return kept


def _collect_by_description(db, description: str, limit: int) -> list:
    desc_lower = description.lower()
    # Extract genre/artist/mood hints from description
    genre_hint = _extract_hint(desc_lower, _GENRE_KEYWORDS)
    artist_hint = _extract_hint(desc_lower, [])
    mood_hint = _extract_hint(desc_lower, _MOOD_KEYWORDS)

    all_items: list = []
    if hasattr(db, "get_all"):
        all_items = db.get_all()

    scored: list[tuple[float, Any]] = []
    for item in all_items:
        score = 0.0
        title_s = str(getattr(item, "title", "") or "").lower()
        artist_s = str(getattr(item, "artist", "") or "").lower()
        album_s = str(getattr(item, "album", "") or "").lower()
        genre_s = str(getattr(item, "genre", "") or "").lower()

        for token in desc_lower.split():
            if token in title_s:
                score += 3
            if token in artist_s:
                score += 4
            if token in album_s:
                score += 2
            if token in genre_s or any(t in genre_s for t in token):
                score += 2

        if genre_hint and genre_hint in genre_s:
            score += 5
        if mood_hint and mood_hint in genre_s:
            score += 3
        if artist_hint and artist_hint in artist_s:
            score += 5

        if score > 0:
            scored.append((score, item))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in scored[:limit]]


def _collect_random(db, limit: int) -> list:
    import random
    all_items: list = []
    if hasattr(db, "get_all"):
        all_items = db.get_all()
    sample_size = min(limit, len(all_items))
    return random.sample(all_items, sample_size) if sample_size else []


def _extract_hint(description: str, keywords: dict[str, list[str]]) -> str:
    for hint, synonyms in keywords.items():
        for syn in synonyms:
            if syn in description:
                return hint
    return ""


def _derive_title(description: str, filters: dict | None) -> str:
    if filters:
        parts = [f"{k}={v}" for k, v in filters.items()]
        return f"Borrador: {', '.join(parts)}"
    if description:
        words = description.strip().split()
        prefix = " ".join(words[:5])
        return f"Borrador: {prefix}"
    return "Borrador de playlist"


_GENRE_KEYWORDS = {
    "rock": ["rock", "rockero", "guitarra", "banda"],
    "pop": ["pop", "popero", "comercial", "mainstream"],
    "electronic": ["electronica", "electronico", "electro", "synth", "beat", "techno", "house"],
    "classical": ["clasica", "clasico", "orquesta", "sinfonica", "piano solo"],
    "jazz": ["jazz", "blues", "saxo", "improvisacion"],
    "metal": ["metal", "heavy", "distorsion"],
    "hiphop": ["hip hop", "rap", "trap", "beatmaker"],
    "latin": ["latina", "latino", "salsa", "reggaeton", "bachata"],
    "ambient": ["ambiente", "ambiental", "relax", "meditacion", "chill"],
    "folk": ["folk", "acustico", "cantautor"],
}


_MOOD_KEYWORDS = {
    "energetic": ["energetica", "animada", "fiesta", "bailar", "movida", "power"],
    "calm": ["tranquila", "relajada", "suave", "calma", "chill", "descanso"],
    "melancholic": ["melancolica", "triste", "nostalgica", "profunda"],
    "happy": ["alegre", "feliz", "positiva", "optimista", "buena onda"],
}


def create_playlist_from_draft(db: Any, draft_id: str = "",
                                playlist_name: str = "",
                                draft_tracks: list | None = None,
                                max_tracks: int = 50) -> ToolResult:
    try:
        tracks = draft_tracks or []
        if not tracks:
            return ToolResult(
                name="create_playlist_from_draft", success=False,
                error="No hay canciones para crear la playlist.",
            )
        if not playlist_name.strip():
            playlist_name = f"Playlist {draft_id}" if draft_id else "Nueva playlist"

        name = playlist_name.strip()[:120]
        if hasattr(db, "create_playlist"):
            pid = db.create_playlist(name)
        else:
            return ToolResult(
                name="create_playlist_from_draft", success=False,
                error="No se pudo crear la playlist en la base de datos.",
            )

        added = 0
        for track in tracks[:min(len(tracks), max_tracks, 100)]:
            track_id = track.get("id") if isinstance(track, dict) else getattr(track, "id", None)
            if track_id and hasattr(db, "get_all"):
                all_items = db.get_all() or []
                id_map = {item.id: item.filepath for item in all_items if getattr(item, "id", None)}
                fp = id_map.get(track_id)
                if fp and hasattr(db, "add_to_playlist"):
                    db.add_to_playlist(pid, fp)
                    added += 1

        return ToolResult(
            name="create_playlist_from_draft", success=True,
            data={
                "playlist_id": pid,
                "playlist_name": name,
                "track_count": added,
                "status": "created",
            },
        )
    except Exception as e:
        return ToolResult(
            name="create_playlist_from_draft", success=False, error=str(e),
        )
