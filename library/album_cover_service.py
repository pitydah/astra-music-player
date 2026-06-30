"""AlbumCoverService — unified cover art resolution for albums.

Order of resolution:
  1. DB/cache embedded (by album key)
  2. External file in album folder (cover.jpg, folder.jpg, etc.)
  3. Cached internal
  4. Direct extraction from first track
  5. Michi fallback
"""
from __future__ import annotations

import hashlib
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
    source: str = "fallback"  # embedded_cache | external_file | embedded_file | user_cache | fallback
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


class AlbumCoverService:
    """Unified cover art resolver for albums."""

    def resolve_cover(self, tracks: list, size: int = 280) -> AlbumCoverResult:
        """Resolve cover art for an album from its tracks."""
        from PySide6.QtGui import QPixmap

        # 1. External file in folder
        for t in tracks:
            fp = str(getattr(t, "filepath", "") or "")
            if fp:
                cover_path = _find_local_cover(os.path.dirname(fp))
                if cover_path:
                    pix = QPixmap(cover_path)
                    if not pix.isNull():
                        return AlbumCoverResult(
                            pixmap=pix, path=cover_path,
                            source="external_file",
                        )

        # 2. Embedded from first valid file
        for t in tracks:
            fp = str(getattr(t, "filepath", "") or "")
            if fp and os.path.isfile(fp):
                try:
                    from library.cover_art_service import extract_embedded_cover
                    cover_data = extract_embedded_cover(fp)
                    if cover_data:
                        pix = QPixmap()
                        if pix.loadFromData(cover_data):
                            return AlbumCoverResult(
                                pixmap=pix, source="embedded_file",
                            )
                except Exception:
                    continue

        # 3. Cache lookup
        try:
            from library.artwork_cache import get_cached
            album = str(getattr(tracks[0], "album", "") if tracks else "")
            artist = str(getattr(tracks[0], "artist", "") if tracks else "")
            cache_key = hashlib.sha256(f"{album}||{artist}".encode()).hexdigest()[:32]
            cached = get_cached(cache_key, size)
            if cached and not cached.isNull():
                return AlbumCoverResult(
                    pixmap=cached, source="embedded_cache",
                )
        except Exception:
            pass

        # 4. Fallback
        from library.album_art import make_default_cover
        fallback = make_default_cover(
            str(getattr(tracks[0], "album", "") if tracks else ""),
            size,
        )
        return AlbumCoverResult(pixmap=fallback, source="fallback")

    def make_fallback_cover(self, title: str = "", artist: str = "",
                            size: int = 280):
        from library.album_art import make_default_cover
        return make_default_cover(title, size)
