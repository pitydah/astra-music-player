"""TrackIdentityService — stable, multi-strategy track identity.

Priority chain:
1. MusicBrainz Track ID (mb_track_id)
2. AcoustID
3. content_hash + duration + size (content stable across moves)
4. file_hash (SHA-256 of file content)
5. Normalized (artist, album, title, duration) tuple
6. File path hash (FP) — fallback only, flagged as path-based
"""
from __future__ import annotations

import hashlib
from typing import Any, Mapping

FP_PREFIX = "fp:"
MB_PREFIX = "mb:"
ACOUSTID_PREFIX = "ac:"
CONTENT_PREFIX = "ch:"
FILEHASH_PREFIX = "fh:"
NORMALIZED_PREFIX = "nm:"


class TrackIdentityService:
    @staticmethod
    def compute_track_uid(record: Mapping[str, Any]) -> str:
        mb_id = _get_str(record, "mb_track_id") or _get_str(record, "musicbrainz_track_id")
        if mb_id:
            return f"{MB_PREFIX}{mb_id}"
        acoustid = _get_str(record, "acoustid_id")
        if acoustid:
            return f"{ACOUSTID_PREFIX}{acoustid}"
        ch = _get_str(record, "content_hash")
        dur = _get_float(record, "duration", 0.0)
        sz = _get_int(record, "size", 0)
        if ch and dur > 0 and sz > 0:
            raw = f"{ch}:{dur}:{sz}"
            h = hashlib.sha256(raw.encode()).hexdigest()[:16]
            return f"{CONTENT_PREFIX}{h}"
        fh = _get_str(record, "file_hash")
        if fh:
            h = hashlib.sha256(fh.encode()).hexdigest()[:16]
            return f"{FILEHASH_PREFIX}{h}"
        artist = (_get_str(record, "artist") or "").strip().lower()
        album = (_get_str(record, "album") or "").strip().lower()
        title = (_get_str(record, "title") or "").strip().lower()
        if artist and title and dur > 0:
            raw = f"{artist}|{album}|{title}|{dur}"
            h = hashlib.sha256(raw.encode()).hexdigest()[:16]
            return f"{NORMALIZED_PREFIX}{h}"
        fp = _get_str(record, "filepath") or ""
        fp_hash = hashlib.sha256(fp.encode()).hexdigest()[:16]
        return f"{FP_PREFIX}{fp_hash}"

    @staticmethod
    def is_path_based_uid(uid: str) -> bool:
        return uid.startswith(FP_PREFIX) if uid else True

    @staticmethod
    def needs_identity_upgrade(uid: str, record: Mapping[str, Any]) -> bool:
        if not uid:
            return True
        if not TrackIdentityService.is_path_based_uid(uid):
            return False
        better = TrackIdentityService.compute_track_uid(record)
        return not better.startswith(FP_PREFIX) and better != uid

    @staticmethod
    def find_duplicates(items: list[Mapping[str, Any]]) -> list[list[Mapping[str, Any]]]:
        from collections import defaultdict
        groups: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
        for item in items:
            uid = TrackIdentityService.compute_track_uid(item)
            groups[uid].append(item)
        return [g for g in groups.values() if len(g) > 1]

    @staticmethod
    def compute_quick_hash(filepath: str) -> str:
        try:
            with open(filepath, "rb") as f:
                first = f.read(65536)
                f.seek(-65536, 2)
                last = f.read(65536)
            raw = first + last
            return hashlib.sha256(raw).hexdigest()[:32]
        except (OSError, PermissionError):
            return ""

    @staticmethod
    def compute_file_hash(filepath: str) -> str:
        try:
            h = hashlib.sha256()
            with open(filepath, "rb") as f:
                while chunk := f.read(65536):
                    h.update(chunk)
            return h.hexdigest()
        except (OSError, PermissionError):
            return ""

    @staticmethod
    def compute_metadata_hash(record: Mapping[str, Any]) -> str:
        fields = [
            _get_str(record, "title"),
            _get_str(record, "artist"),
            _get_str(record, "album"),
            _get_str(record, "tracknumber"),
            _get_str(record, "genre"),
            _get_str(record, "duration", "0"),
            _get_str(record, "sample_rate", "0"),
            _get_str(record, "bitrate", "0"),
        ]
        raw = "|".join(str(f) for f in fields)
        return hashlib.sha256(raw.encode()).hexdigest()[:32]


def _get_str(record: Mapping[str, Any], key: str, default: str = "") -> str:
    val = record.get(key, default)
    return str(val) if val is not None else default


def _get_float(record: Mapping[str, Any], key: str, default: float = 0.0) -> float:
    val = record.get(key, default)
    try:
        return float(val) if val is not None else default
    except (ValueError, TypeError):
        return default


def _get_int(record: Mapping[str, Any], key: str, default: int = 0) -> int:
    val = record.get(key, default)
    try:
        return int(val) if val is not None else default
    except (ValueError, TypeError):
        return default
