"""Navigation tools — open internal Michi views. READ_ONLY, no data modification."""

from __future__ import annotations

from typing import Any

from integrations.ai_assistant.schemas import ToolResult


def open_artist_view(db: Any, artist_name: str) -> ToolResult:
    try:
        if not artist_name.strip():
            return ToolResult(
                name="open_artist_view", success=False,
                error="Nombre de artista no especificado.",
            )
        return ToolResult(
            name="open_artist_view", success=True,
            data={
                "_navigate": "artists",
                "artist_name": artist_name.strip(),
            },
        )
    except Exception as e:
        return ToolResult(
            name="open_artist_view", success=False, error=str(e),
        )


def open_album_view(db: Any, album_name: str, artist_name: str = "") -> ToolResult:
    try:
        if not album_name.strip():
            return ToolResult(
                name="open_album_view", success=False,
                error="Nombre de album no especificado.",
            )
        return ToolResult(
            name="open_album_view", success=True,
            data={
                "_navigate": "albums",
                "album_name": album_name.strip(),
                "artist_name": artist_name.strip(),
            },
        )
    except Exception as e:
        return ToolResult(
            name="open_album_view", success=False, error=str(e),
        )


def open_genre_view(db: Any, genre_name: str) -> ToolResult:
    try:
        if not genre_name.strip():
            return ToolResult(
                name="open_genre_view", success=False,
                error="Nombre de genero no especificado.",
            )
        return ToolResult(
            name="open_genre_view", success=True,
            data={
                "_navigate": "genres",
                "genre_name": genre_name.strip(),
            },
        )
    except Exception as e:
        return ToolResult(
            name="open_genre_view", success=False, error=str(e),
        )


def open_playlist_view(db: Any, playlist_id: int = 0,
                       playlist_name: str = "") -> ToolResult:
    try:
        if playlist_id:
            return ToolResult(
                name="open_playlist_view", success=True,
                data={
                    "_navigate": "playlist",
                    "playlist_id": playlist_id,
                },
            )
        if playlist_name.strip():
            return ToolResult(
                name="open_playlist_view", success=True,
                data={
                    "_navigate": "playlist_hub",
                    "search_term": playlist_name.strip(),
                },
            )
        return ToolResult(
            name="open_playlist_view", success=True,
            data={"_navigate": "playlist_hub"},
        )
    except Exception as e:
        return ToolResult(
            name="open_playlist_view", success=False, error=str(e),
        )


def show_track_in_library(db: Any, track_id: int) -> ToolResult:
    try:
        if not track_id:
            return ToolResult(
                name="show_track_in_library", success=False,
                error="ID de cancion no especificado.",
            )
        return ToolResult(
            name="show_track_in_library", success=True,
            data={
                "_navigate": "library",
                "track_id": track_id,
            },
        )
    except Exception as e:
        return ToolResult(
            name="show_track_in_library", success=False, error=str(e),
        )
