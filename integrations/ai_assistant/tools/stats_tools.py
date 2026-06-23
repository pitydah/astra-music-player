"""Library statistics tool for Michi AI Assistant."""

from __future__ import annotations

from typing import Any

from integrations.ai_assistant.schemas import ToolResult


def get_library_stats(db: Any) -> ToolResult:
    try:
        total_songs = 0
        total_artists = 0
        total_albums = 0
        total_duration = 0.0
        genres: dict[str, int] = {}
        formats: dict[str, int] = {}
        missing_title = 0
        missing_artist = 0
        missing_album = 0
        missing_genre = 0
        missing_year = 0
        missing_cover = 0

        items = db.get_all() or [] if hasattr(db, "get_all") else []

        artists_set: set[str] = set()
        albums_set: set[str] = set()

        for item in items:
            total_songs += 1
            total_duration += getattr(item, "duration", 0) or 0

            artist = (getattr(item, "artist", "") or "").strip()
            album = (getattr(item, "album", "") or "").strip()
            genre = (getattr(item, "genre", "") or "").strip()
            year = getattr(item, "year", None)
            title = (getattr(item, "title", "") or "").strip()

            if artist:
                artists_set.add(artist.lower())
            if album and artist:
                albums_set.add(f"{artist.lower()}|{album.lower()}")
            elif album:
                albums_set.add(album.lower())
            if genre:
                g = genre.lower()
                genres[g] = genres.get(g, 0) + 1

            fmt = str(getattr(item, "ext", "") or "").lstrip(".").lower()
            if fmt:
                formats[fmt] = formats.get(fmt, 0) + 1

            if not title:
                missing_title += 1
            if not artist:
                missing_artist += 1
            if not album:
                missing_album += 1
            if not genre:
                missing_genre += 1
            if not year:
                missing_year += 1
            if not _has_cover(item):
                missing_cover += 1

        total_artists = len(artists_set)
        total_albums = len(albums_set)
        top_genres = sorted(genres.items(), key=lambda x: x[1], reverse=True)[:10]
        top_formats = sorted(formats.items(), key=lambda x: x[1], reverse=True)[:5]
        hours = int(total_duration // 3600)
        minutes = int((total_duration % 3600) // 60)

        stats = {
            "total_songs": total_songs,
            "total_artists": total_artists,
            "total_albums": total_albums,
            "total_duration": f"{hours}h {minutes}m",
            "total_duration_seconds": int(total_duration),
            "top_genres": [{"genre": g, "count": c} for g, c in top_genres],
            "top_formats": [{"format": f, "count": c} for f, c in top_formats],
            "missing_title": missing_title,
            "missing_artist": missing_artist,
            "missing_album": missing_album,
            "missing_genre": missing_genre,
            "missing_year": missing_year,
            "missing_cover": missing_cover,
        }
        return ToolResult(name="get_library_stats", success=True, data=stats)
    except Exception as e:
        return ToolResult(name="get_library_stats", success=False, error=str(e))


def _has_cover(item) -> bool:
    if hasattr(item, "cover_path") and getattr(item, "cover_path", None):
        return True
    if hasattr(item, "has_cover") and callable(getattr(item, "has_cover", None)):
        return item.has_cover()
    return False
