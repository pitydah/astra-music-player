"""AlbumCoverService — unified cover art resolution for albums.

Order of resolution:
  1. album_art_cache by album_key (make_album_key via album_art)
  2. External file in album folder (cover.jpg, folder.jpg, etc.)
  3. Embedded extraction via cover_art_service
  4. Michi fallback (make_default_cover)
All keys use make_album_key from library.album_key for consistency with grid, detail, CoverFlow, and API.
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger("michi.album_cover")

COVER_FILENAMES = [
    "cover.jpg", "cover.png", "folder.jpg", "folder.png",
    "front.jpg", "front.png", "albumart.jpg", "albumart.png",
    "AlbumArt.jpg", "AlbumArt.png", "album.jpg", "album.png",
]


@dataclass
class AlbumCoverResult:
    pixmap: Any = None
    path: str = ""
    source: str = "fallback"
    missing: bool = False
    error: str = ""


def _find_local_cover(dirpath: str) -> str | None:
    if not dirpath or not os.path.isdir(dirpath):
        return None
    for name in COVER_FILENAMES:
        path = os.path.join(dirpath, name)
        if os.path.isfile(path):
            return path
    for f in sorted(os.listdir(dirpath)):
        low = f.lower()
        if low.endswith((".jpg", ".jpeg", ".png")) and any(
            x in low for x in ("cover", "folder", "front", "album", "art", "portada")):
            return os.path.join(dirpath, f)
    return None


def _album_key_for_tracks(tracks: list) -> str:
    """Compute a stable album key from tracks using make_album_key."""
    from library.album_key import make_album_key
    if not tracks:
        return ""
    t = tracks[0]
    albumartist = str(getattr(t, "albumartist", "") or "")
    artist = str(getattr(t, "artist", "") or "")
    album = str(getattr(t, "album", "") or "")
    return make_album_key(albumartist, artist, album)


class AlbumCoverService:
    """Unified cover art resolver for albums — keyed by make_album_key."""

    def resolve_cover(self, tracks: list, size: int = 280) -> AlbumCoverResult:
        """Resolve cover art for an album from its tracks."""
        from PySide6.QtGui import QPixmap

        album_key = _album_key_for_tracks(tracks)

        # 1. album_art cache by album key
        try:
            from library.album_art import load_cover_pixmap
            cached = load_cover_pixmap(album_key, size, lazy=True) if album_key else None
            if cached and not cached.isNull():
                return AlbumCoverResult(pixmap=cached, source="embedded_cache")
        except Exception:
            pass

        # 2. External file in first track's folder
        for t in tracks:
            fp = str(getattr(t, "filepath", "") or "")
            if fp:
                cover_path = _find_local_cover(os.path.dirname(fp))
                if cover_path:
                    pix = QPixmap(cover_path)
                    if not pix.isNull():
                        return AlbumCoverResult(
                            pixmap=pix, path=cover_path, source="external_file",
                        )

        # 3. Embedded from first valid file
        for t in tracks:
            fp = str(getattr(t, "filepath", "") or "")
            if fp and os.path.isfile(fp):
                try:
                    from library.cover_art_service import extract_embedded_cover
                    cover_data = extract_embedded_cover(fp)
                    if cover_data:
                        pix = QPixmap()
                        if pix.loadFromData(cover_data):
                            return AlbumCoverResult(pixmap=pix, source="embedded_file")
                except Exception:
                    continue

        # 4. Fallback
        from library.album_art import make_default_cover
        fallback = make_default_cover(
            str(getattr(tracks[0], "album", "") if tracks else ""), size)
        return AlbumCoverResult(pixmap=fallback, source="fallback")

    def make_fallback_cover(self, title: str = "", artist: str = "",
                            size: int = 280):
        from library.album_art import make_default_cover
        return make_default_cover(title, size)
