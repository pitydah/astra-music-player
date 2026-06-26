"""Artwork Cache — disk-based scaled cover art cache.

Sizes: thumb (96), medium (260), large (512).
Key: SHA256(filepath + mtime + size).
Cache dir: ~/.cache/michi-music-player/covers/local/ (via core.paths)
"""

import hashlib
import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

MAX_CACHE_SIZE_MB = 200
SIZES = {"thumb": 96, "medium": 260, "large": 512}


def _cache_dir() -> str:
    from core.paths import covers_cache_dir
    return covers_cache_dir()


def _ensure_cache_dir():
    os.makedirs(_cache_dir(), exist_ok=True)


def _cache_key(filepath: str) -> str:
    try:
        st = os.stat(filepath)
        raw = f"{filepath}|{st.st_mtime}|{st.st_size}".encode()
    except OSError:
        raw = filepath.encode()
    return hashlib.sha256(raw).hexdigest()[:32]


def _cache_path(filepath: str, size_name: str) -> str:
    key = _cache_key(filepath)
    return os.path.join(_cache_dir(), f"{key}_{size_name}.png")


def get_cached(filepath: str, size_name: str = "medium") -> QPixmap | None:
    if size_name not in SIZES:
        return None
    path = _cache_path(filepath, size_name)
    if os.path.exists(path):
        pix = QPixmap(path)
        if not pix.isNull():
            return pix
    return None


def cache_cover(filepath: str, pix: QPixmap, size_name: str = "medium"):
    if size_name not in SIZES:
        return
    target = SIZES[size_name]
    scaled = pix.scaled(target, target, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    path = _cache_path(filepath, size_name)
    tmp = path + ".tmp"
    _ensure_cache_dir()
    scaled.save(tmp, "PNG")
    try:
        os.replace(tmp, path)
    except OSError:
        with __import__("contextlib").suppress(OSError):
            os.unlink(tmp)


def cache_origin(filepath: str, pix: QPixmap):
    cache_cover(filepath, pix, "large")


def cleanup_cache(max_count: int = 500):
    """Remove oldest cache entries if exceeding count limit."""
    d = _cache_dir()
    if not os.path.isdir(d):
        return
    files = sorted(
        (os.path.join(d, f) for f in os.listdir(d) if f.endswith(".png")),
        key=os.path.getmtime)
    for f in files[max_count:]:
        with __import__("contextlib").suppress(OSError):
            os.unlink(f)
