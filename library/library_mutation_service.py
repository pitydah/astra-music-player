"""LibraryMutationService — canonical mutation API for the library.

Single entry point for add, remove, update operations.
Produces structured results, syncs genres, and rebuilds FTS.
"""
from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass, field
from typing import Callable

from library.media_record_builder import MediaRecordBuilder

logger = logging.getLogger("michi.library_mutation")


@dataclass
class LibraryMutationResult:
    added: int = 0
    updated: int = 0
    removed: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)
    changed_paths: list[str] = field(default_factory=list)

    def merge(self, other: LibraryMutationResult) -> LibraryMutationResult:
        return LibraryMutationResult(
            added=self.added + other.added,
            updated=self.updated + other.updated,
            removed=self.removed + other.removed,
            skipped=self.skipped + other.skipped,
            errors=self.errors + other.errors,
            changed_paths=self.changed_paths + other.changed_paths,
        )


class LibraryMutationService:
    def __init__(self, db, file_actions=None, on_change: Callable | None = None):
        self._db = db
        self._file_actions = file_actions
        self._on_change = on_change
        self._builder = MediaRecordBuilder(db=db)

    def add_file(self, filepath: str) -> LibraryMutationResult:
        result = LibraryMutationResult()
        if not os.path.isfile(filepath):
            result.errors.append(f"Not a file: {filepath}")
            return result
        build = self._builder.build(filepath)
        if build.errors:
            result.errors.extend(build.errors)
            return result
        if build.record is None:
            result.skipped += 1
            return result
        record = build.record
        now = time.time()
        record["created_at"] = now
        record["updated_at"] = now
        record["last_scanned"] = now
        record["scan_status"] = "ok"
        result.added = 1
        try:
            from library.batch_writer import BatchWriter
            writer = BatchWriter(self._db.conn, batch_size=1)
            writer.add(record)
            writer.flush()
            result.changed_paths.append(filepath)
        except Exception as e:
            result.errors.append(f"DB write failed for {filepath}: {e}")
            result.added = 0
            return result
        self._post_mutation(result)
        return result

    def add_files(self, filepaths: list[str]) -> LibraryMutationResult:
        result = LibraryMutationResult()
        records = []
        for fp in filepaths:
            if not os.path.isfile(fp):
                result.skipped += 1
                continue
            build = self._builder.build(fp)
            if build.errors or build.record is None:
                result.skipped += 1
                continue
            now = time.time()
            build.record["created_at"] = now
            build.record["updated_at"] = now
            build.record["last_scanned"] = now
            build.record["scan_status"] = "ok"
            records.append(build.record)
        if not records:
            return result
        try:
            from library.batch_writer import BatchWriter
            writer = BatchWriter(self._db.conn, batch_size=100)
            for rec in records:
                writer.add(rec)
            n = writer.flush()
            result.added = n
            result.changed_paths = [r["filepath"] for r in records if "filepath" in r]
        except Exception as e:
            result.errors.append(f"Batch write failed: {e}")
            for fp in filepaths:
                sub = self.add_file(fp)
                result = result.merge(sub)
        self._post_mutation(result)
        return result

    def remove_paths(self, paths: list[str]) -> LibraryMutationResult:
        result = LibraryMutationResult()
        if not paths:
            return result
        try:
            placeholders = ",".join("?" for _ in paths)
            sql = f"UPDATE media_items SET deleted_at = ?, scan_status = 'missing' WHERE filepath IN ({placeholders})"
            self._db.conn.execute(sql, [time.time()] + paths)
            self._db.conn.commit()
            result.removed = len(paths)
            result.changed_paths = paths
        except Exception as e:
            result.errors.append(f"Remove failed: {e}")
        self._post_mutation(result)
        return result

    def update_filepath(self, old_path: str, new_path: str) -> LibraryMutationResult:
        result = LibraryMutationResult()
        try:
            cur = self._db.conn.execute(
                "SELECT * FROM media_items WHERE filepath = ?", (old_path,)
            )
            row = cur.fetchone()
            if row is None:
                result.errors.append(f"Not in DB: {old_path}")
                return result
            preserve = {
                "play_count": row[42] if len(row) > 42 else 0,
                "rating": row[44] if len(row) > 44 else 0,
                "last_played": row[43] if len(row) > 43 else 0.0,
                "track_uid": row[48] if len(row) > 48 else "",
            }
            build = self._builder.build(new_path, preserve=preserve)
            if build.record is None:
                result.errors.append(f"Build failed for {new_path}")
                return result
            record = build.record
            self._db.conn.execute(
                "UPDATE media_items SET filepath=?, filename=?, directory=?,"
                " ext=?, size=?, mtime=?, duration=?,"
                " title=?, artist=?, album=?, albumartist=?,"
                " genre=?, year=?, track_number=?, track_total=?,"
                " disc_number=?, disc_total=?, composer=?,"
                " mb_track_id=?, mb_album_id=?, mb_albumartist_id=?,"
                " bit_depth=?, bpm=?, bitrate=?, sample_rate=?, channels=?,"
                " replaygain_track=?, replaygain_album=?, replaygain_track_peak=?,"
                " replaygain_album_peak=?, r128_track_gain=?, r128_album_gain=?,"
                " isrc=?, label=?, conductor=?, compilation=?,"
                " media_type=?, encoder=?, copyright=?, originaldate=?,"
                " remixer=?, grouping=?, mood=?, comment=?, lyricist=?,"
                " mb_artist_id=?, mb_releasegroup_id=?,"
                " acoustid_id=?, acoustid_fingerprint=?, content_hash=?,"
                " updated_at=?, last_scanned=?"
                " WHERE filepath = ?",
                (record["filepath"], record["filename"], record["directory"],
                 record["ext"], record["size"], record["mtime"], record["duration"],
                 record["title"], record["artist"], record["album"], record["albumartist"],
                 record["genre"], record["year"], record["track_number"], record["track_total"],
                 record["disc_number"], record["disc_total"], record["composer"],
                 record["mb_track_id"], record["mb_album_id"], record["mb_albumartist_id"],
                 record["bit_depth"], record["bpm"], record["bitrate"], record["sample_rate"],
                 record["channels"],
                 record["replaygain_track"], record["replaygain_album"], record["replaygain_track_peak"],
                 record.get("replaygain_album_peak", 0.0), record.get("r128_track_gain", 0.0),
                 record.get("r128_album_gain", 0.0),
                 record.get("isrc", ""), record.get("label", ""), record.get("conductor", ""),
                 record.get("compilation", 0), record.get("media_type", ""), record.get("encoder", ""),
                 record.get("copyright", ""), record.get("originaldate", ""),
                 record.get("remixer", ""), record.get("grouping", ""), record.get("mood", ""),
                 record.get("comment", ""), record.get("lyricist", ""),
                 record.get("mb_artist_id", ""), record.get("mb_releasegroup_id", ""),
                 record.get("acoustid_id", ""), record.get("acoustid_fingerprint", ""),
                 record.get("content_hash", ""),
                 time.time(), time.time(), old_path))
            self._db.conn.commit()
            result.updated = 1
            result.changed_paths = [old_path, new_path]
        except Exception as e:
            result.errors.append(f"Update filepath failed {old_path} -> {new_path}: {e}")
        self._post_mutation(result)
        return result

    def sync_genres(self) -> int:
        from library.genre_repository import GenreRepository
        conn = getattr(self._db, 'conn', self._db)
        repo = GenreRepository(conn)
        return repo.backfill_from_media_items()

    def rebuild_fts(self) -> bool:
        try:
            from library.search_index import SearchIndex
            idx = SearchIndex(self._db.conn)
            if idx.fts_exists:
                idx.rebuild_fts()
                return True
            return False
        except Exception as e:
            logger.warning("FTS rebuild failed: %s", e)
            return False

    def _post_mutation(self, result: LibraryMutationResult):
        if not result.errors and result.changed_paths:
            try:
                self.sync_genres()
            except Exception as e:
                logger.debug("Genre sync after mutation: %s", e)
        if self._on_change:
            try:
                self._on_change(result)
            except Exception as e:
                logger.warning("on_change callback failed: %s", e)
