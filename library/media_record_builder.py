"""MediaRecordBuilder — canonical path from file to DB record.

Reusable by Indexer, LibraryDB.add_file, backfill, and organize.
"""
from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass, field
from typing import Any, Mapping

from library.metadata_extractor import extract_metadata_combined
from library.metadata_normalizer import (
    normalize_artist_name, normalize_bpm, normalize_disc_track,
    normalize_genre, normalize_mb_id, normalize_text, normalize_year,
)
from library.media_item import media_kind
from library.album_key import make_album_key
from library.track_identity import TrackIdentityService

logger = logging.getLogger("michi.media_builder")


@dataclass
class MediaBuildResult:
    record: dict | None = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class MediaRecordBuilder:
    def __init__(self, db=None):
        self._db = db

    def build(self, filepath: str, preserve: Mapping[str, Any] | None = None,
              compute_hashes: bool = True) -> MediaBuildResult:
        result = MediaBuildResult()

        if not os.path.exists(filepath):
            result.errors.append(f"File not found: {filepath}")
            return result

        ext = os.path.splitext(filepath)[1].lower()
        kind = media_kind(ext)
        if kind == "unknown":
            result.warnings.append(f"Skipped unknown extension: {ext}")
            return result

        try:
            stat = os.stat(filepath)
        except OSError as e:
            result.errors.append(f"stat failed: {e}")
            return result

        meta = extract_metadata_combined(filepath)
        if not meta:
            result.warnings.append(f"No metadata extracted from {filepath}")

        fname = os.path.basename(filepath)
        dname = os.path.dirname(filepath)
        title = normalize_text(meta.get("title") or "", 256)
        artist = normalize_artist_name(meta.get("artist", ""))
        album = normalize_text(meta.get("album", ""), 256)
        genre = normalize_genre(meta.get("genre", ""))
        year = normalize_year(meta.get("year"))
        albumartist = normalize_artist_name(meta.get("albumartist", ""))
        composer = normalize_text(meta.get("composer", ""), 256)
        disc_number, disc_total = normalize_disc_track(
            f"{meta.get('disc_number', 0)}/{meta.get('disc_total', 0)}")
        track_number = meta.get("track_number", 0)
        track_total = meta.get("track_total", 0)
        mb_track_id = normalize_mb_id(meta.get("mb_track_id", ""))
        mb_album_id = normalize_mb_id(meta.get("mb_album_id", ""))
        mb_albumartist_id = normalize_mb_id(meta.get("mb_albumartist_id", ""))
        bit_depth = meta.get("bit_depth", 0) or 0
        bpm = normalize_bpm(meta.get("bpm"))

        record: dict[str, Any] = {
            "filepath": filepath, "filename": fname, "directory": dname,
            "ext": ext, "kind": kind, "size": stat.st_size, "mtime": stat.st_mtime,
            "duration": meta.get("duration", 0.0), "channels": meta.get("channels", 0),
            "sample_rate": meta.get("sample_rate", 0), "bitrate": meta.get("bitrate", 0),
            "title": title, "artist": artist, "album": album,
            "albumartist": albumartist, "year": year, "genre": genre,
            "track_number": track_number, "track_total": track_total,
            "disc_number": disc_number, "disc_total": disc_total,
            "composer": composer,
            "mb_track_id": mb_track_id, "mb_album_id": mb_album_id,
            "mb_albumartist_id": mb_albumartist_id,
            "bit_depth": bit_depth, "bpm": bpm,
            "replaygain_track": meta.get("replaygain_track", 0.0),
            "replaygain_album": meta.get("replaygain_album", 0.0),
            "replaygain_track_peak": meta.get("replaygain_track_peak", 0.0),
            "replaygain_album_peak": meta.get("replaygain_album_peak", 0.0),
            "r128_track_gain": meta.get("r128_track_gain", 0.0),
            "r128_album_gain": meta.get("r128_album_gain", 0.0),
            "isrc": normalize_text(meta.get("isrc", ""), 128),
            "label": normalize_text(meta.get("label", ""), 256),
            "conductor": normalize_text(meta.get("conductor", ""), 256),
            "compilation": meta.get("compilation", 0),
            "media_type": normalize_text(meta.get("media_type", ""), 128),
            "encoder": normalize_text(meta.get("encoder", ""), 256),
            "copyright": normalize_text(meta.get("copyright", ""), 512),
            "originaldate": normalize_text(meta.get("originaldate", ""), 32),
            "remixer": normalize_text(meta.get("remixer", ""), 256),
            "grouping": normalize_text(meta.get("grouping", ""), 256),
            "mood": normalize_text(meta.get("mood", ""), 128),
            "comment": normalize_text(meta.get("comment", ""), 512),
            "lyricist": normalize_text(meta.get("lyricist", ""), 256),
            "mb_artist_id": meta.get("mb_artist_id", ""),
            "mb_releasegroup_id": meta.get("mb_releasegroup_id", ""),
            "acoustid_id": meta.get("acoustid_id", ""),
            "acoustid_fingerprint": meta.get("acoustid_fingerprint", ""),
        }

        if compute_hashes:
            record["content_hash"] = TrackIdentityService.compute_quick_hash(filepath)

        if preserve and preserve.get("track_uid"):
            record["track_uid"] = preserve["track_uid"]
        else:
            record["track_uid"] = TrackIdentityService.compute_track_uid(record)

        if preserve:
            for key in ("play_count", "rating", "last_played"):
                if key in preserve:
                    record[key] = preserve[key]

        now = time.time()
        record["updated_at"] = stat.st_mtime
        record["last_scanned"] = now
        record["created_at"] = preserve.get("created_at", now) if preserve else now

        cover_data = meta.get("cover_data", b"")
        if cover_data and album and self._db:
            try:
                ak = make_album_key(albumartist or artist, artist, album)
                cover_mime = meta.get("cover_mime", "image/jpeg")
                self._db.conn.execute(
                    "INSERT OR REPLACE INTO album_art_cache "
                    "(album_hash, mime, data) VALUES (?,?,?)",
                    (ak, cover_mime, cover_data),
                )
            except Exception as e:
                logger.debug("Failed to cache cover for %s: %s", filepath, e)

        result.record = record
        return result

    @staticmethod
    def record_to_media_item(record: dict):
        from library.media_item import MediaItem
        return MediaItem.from_dict(record)
