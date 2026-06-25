"""Tag writer — reads and writes metadata tags to audio files using mutagen.

Supports FLAC, MP3 (ID3), Ogg Vorbis/Opus, and M4A (MP4).
"""

from __future__ import annotations

import logging
import os

import mutagen
from mutagen.flac import FLAC, Picture
from mutagen.id3 import ID3, APIC
from mutagen.oggvorbis import OggVorbis
from mutagen.oggopus import OggOpus
from mutagen.mp4 import MP4, MP4Cover

logger = logging.getLogger("michi.tag_writer")

_SUPPORTED = frozenset({".flac", ".mp3", ".ogg", ".oga", ".opus", ".m4a", ".mp4"})

# ── Map our metadata keys to mutagen tag names per format ──

_FLAC_TAGS = {
    "title": "title",
    "artist": "artist",
    "album": "album",
    "albumartist": "albumartist",
    "tracknumber": "tracknumber",
    "track_total": "tracktotal",
    "discnumber": "discnumber",
    "disc_total": "disctotal",
    "genre": "genre",
    "date": "date",
    "year": "date",
    "composer": "composer",
    "comment": "description",
}

_ID3_TAGS = {
    "title": "TIT2",
    "artist": "TPE1",
    "album": "TALB",
    "albumartist": "TPE2",
    "tracknumber": "TRCK",
    "discnumber": "TPOS",
    "genre": "TCON",
    "date": "TDRC",
    "year": "TDRC",
    "composer": "TCOM",
    "comment": "COMM",
}

_VORBIS_TAGS = {
    "title": "title",
    "artist": "artist",
    "album": "album",
    "albumartist": "albumartist",
    "tracknumber": "tracknumber",
    "track_total": "tracktotal",
    "discnumber": "discnumber",
    "disc_total": "disctotal",
    "genre": "genre",
    "date": "date",
    "year": "date",
    "composer": "composer",
    "comment": "comment",
}

_MP4_TAGS = {
    "title": "\xa9nam",
    "artist": "\xa9ART",
    "album": "\xa9alb",
    "albumartist": "aART",
    "tracknumber": "trkn",
    "discnumber": "disk",
    "genre": "\xa9gen",
    "date": "\xa9day",
    "year": "\xa9day",
    "composer": "\xa9wrt",
    "comment": "\xa9cmt",
}


class TagWriter:
    """Real metadata tag reader/writer using mutagen."""

    @property
    def available(self) -> bool:
        return True

    # ── Read ──

    def read_tags(self, path: str) -> dict:
        """Read all known metadata tags from an audio file."""
        if not os.path.isfile(path):
            logger.debug("read_tags: file not found: %s", path)
            return {}
        ext = os.path.splitext(path)[1].lower()
        if ext not in _SUPPORTED:
            logger.debug("read_tags: unsupported format: %s", ext)
            return {}
        try:
            tags = self._read_impl(path, ext)
            tags["duration"] = mutagen.File(path).info.length if mutagen.File(path) else 0.0
        except Exception as e:
            logger.warning("read_tags failed for %s: %s", path, e)
            return {}
        return tags

    def _read_impl(self, path: str, ext: str) -> dict:
        tags = {}
        if ext == ".flac":
            f = FLAC(path)
            for key, fkey in _FLAC_TAGS.items():
                val = f.get(fkey)
                if val:
                    tags[key] = val[0] if isinstance(val, list) else str(val)
        elif ext == ".mp3":
            f = ID3(path)
            for key, fkey in _ID3_TAGS.items():
                frame = f.get(fkey)
                if frame:
                    tags[key] = str(frame.text[0]) if hasattr(frame, 'text') else str(frame)
        elif ext in (".ogg", ".oga", ".opus"):
            f = OggOpus(path) if ext == ".opus" else OggVorbis(path)
            for key, fkey in _VORBIS_TAGS.items():
                val = f.get(fkey)
                if val:
                    tags[key] = val[0] if isinstance(val, list) else str(val)
        elif ext in (".m4a", ".mp4"):
            f = MP4(path)
            for key, fkey in _MP4_TAGS.items():
                val = f.get(fkey)
                if val:
                    tags[key] = str(val[0]) if isinstance(val, list) else str(val)
        return tags

    # ── Write ──

    def write_tags(self, path: str, metadata: dict):
        """Write metadata tags to a single file. Raises on failure."""
        if not os.path.isfile(path):
            raise FileNotFoundError(f"File not found: {path}")
        ext = os.path.splitext(path)[1].lower()
        if ext not in _SUPPORTED:
            raise ValueError(f"Unsupported format: {ext}")
        self._write_impl(path, ext, metadata)

    def write_batch(self, paths: list[str], metadata: dict) -> dict:
        """Write metadata to multiple files.

        Returns {"ok": [...], "failed": [{"path":..., "error":...}, ...]}.
        Does not stop on individual failures.
        """
        ok = []
        failed = []
        for path in paths:
            try:
                self.write_tags(path, metadata)
                ok.append(path)
            except Exception as e:
                logger.warning("write_batch failed for %s: %s", path, e)
                failed.append({"path": path, "error": str(e)})
        return {"ok": ok, "failed": failed}

    def _write_impl(self, path: str, ext: str, metadata: dict):
        if ext == ".flac":
            self._write_flac(path, metadata)
        elif ext == ".mp3":
            self._write_mp3(path, metadata)
        elif ext in (".ogg", ".oga", ".opus"):
            self._write_vorbis(path, metadata)
        elif ext in (".m4a", ".mp4"):
            self._write_mp4(path, metadata)

    def _write_flac(self, path: str, metadata: dict):
        f = FLAC(path)
        for key, fkey in _FLAC_TAGS.items():
            val = metadata.get(key)
            if val is not None:
                f[fkey] = str(val)
        f.save()

    def _write_mp3(self, path: str, metadata: dict):
        f = ID3(path)
        for key, fkey in _ID3_TAGS.items():
            val = metadata.get(key)
            if val is not None:
                cls = mutagen.id3.Frames.get(fkey)
                if cls:
                    f[fkey] = cls(encoding=3, text=str(val))
        f.save()

    def _write_vorbis(self, path: str, metadata: dict):
        try:
            f = OggOpus(path)
        except mutagen.oggopus.OggOpusHeaderError:
            f = OggVorbis(path)
        for key, fkey in _VORBIS_TAGS.items():
            val = metadata.get(key)
            if val is not None:
                f[fkey] = str(val)
        f.save()

    def _write_mp4(self, path: str, metadata: dict):
        f = MP4(path)
        for key, fkey in _MP4_TAGS.items():
            val = metadata.get(key)
            if val is not None:
                f[fkey] = [str(val)]
        # Handle track number specially — MP4 uses (track, total) tuples
        tn = metadata.get("tracknumber")
        if tn is not None:
            tt = metadata.get("track_total") or 0
            f["trkn"] = [(int(tn), int(tt))]
        dn = metadata.get("discnumber")
        if dn is not None:
            dt = metadata.get("disc_total") or 0
            f["disk"] = [(int(dn), int(dt))]
        f.save()

    # ── Cover art ──

    def embed_cover(self, path: str, cover_path: str):
        """Embed cover art into an audio file."""
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Audio file not found: {path}")
        if not os.path.isfile(cover_path):
            raise FileNotFoundError(f"Cover image not found: {cover_path}")
        ext = os.path.splitext(path)[1].lower()
        if ext not in _SUPPORTED:
            raise ValueError(f"Unsupported format: {ext}")
        cover_ext = os.path.splitext(cover_path)[1].lower()
        mime_map = {
            ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".png": "image/png", ".gif": "image/gif",
        }
        mime = mime_map.get(cover_ext, "image/jpeg")
        with open(cover_path, "rb") as cf:
            cover_data = cf.read()

        if ext == ".flac":
            self._embed_flac_cover(path, cover_data, mime)
        elif ext == ".mp3":
            self._embed_mp3_cover(path, cover_data, mime)
        elif ext in (".m4a", ".mp4"):
            self._embed_mp4_cover(path, cover_data, mime)
        elif ext in (".ogg", ".oga", ".opus"):
            self._embed_vorbis_cover(path, cover_data)
        else:
            raise ValueError(f"Cover embedding not supported for: {ext}")

    def _embed_flac_cover(self, path: str, data: bytes, mime: str):
        f = FLAC(path)
        f.clear_pictures()
        pic = Picture()
        pic.type = 3  # front cover
        pic.mime = mime
        pic.data = data
        f.add_picture(pic)
        f.save()

    def _embed_mp3_cover(self, path: str, data: bytes, mime: str):
        f = ID3(path)
        f.delall("APIC")
        f["APIC"] = APIC(encoding=3, mime=mime, type=3, desc="Cover", data=data)
        f.save()

    def _embed_mp4_cover(self, path: str, data: bytes, mime: str):
        f = MP4(path)
        fmt = MP4Cover.FORMAT_JPEG if "jpeg" in mime else MP4Cover.FORMAT_PNG
        f["covr"] = [MP4Cover(data, imageformat=fmt)]
        f.save()

    def _embed_vorbis_cover(self, path: str, data: bytes):
        import base64
        try:
            f = OggOpus(path)
        except mutagen.oggopus.OggOpusHeaderError:
            f = OggVorbis(path)
        f["metadata_block_picture"] = []
        f["coverart"] = base64.b64encode(data).decode("ascii")
        f.save()
