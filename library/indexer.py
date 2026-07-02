"""Indexer 2.0 — orchestrates full indexing pipeline.

Flow:
    FileWalker → ChangeDetector → MetadataExtractor → AlbumKeyBuilder
    → BatchWriter → Cleanup → Rebuild UI indexes → Schedule enrichment

Resilience:
    - max_errors cap prevents runaway failures from halting the scan
    - BatchWriter uses dynamic batch sizing with exponential backoff
    - Errors per file are logged to index_errors table, never crash
"""
import os
import time
import logging

from PySide6.QtCore import Signal, QObject

from library.index_state import ScanState, ScanPhase
from library.batch_writer import BatchWriter
from library.metadata_normalizer import normalize_artist_name
from library.metadata_extractor import ALL_EXTS
from library.album_key import make_artist_key

logger = logging.getLogger("michi.indexer")

_DEFAULT_BATCH_SIZE = 100
_DEFAULT_MAX_ERRORS = 100


class Indexer(QObject):
    """Main indexer — walks files, detects changes, extracts metadata,
    writes in batches, cleans up missing files, and schedules enrichment."""

    # Signals
    progress = Signal(int, int, str)           # current, total, filepath
    detail = Signal(dict)                     # full ScanState as dict
    batch_complete = Signal(int)              # records written in this batch
    cleanup_complete = Signal(int)            # records removed
    finished = Signal(int)                    # total processed (added + updated)
    enrichment_requested = Signal(str, str)   # artist_key, artist_name

    @classmethod
    def from_db_path(cls, db_path: str, root_path: str, parent=None):
        """Create an Indexer with its own LibraryDB connection from a path."""
        from library.library_db import LibraryDB
        db = LibraryDB(db_path)
        return cls(db, root_path, parent)

    def __init__(self, db, root_path: str, parent=None,
                 batch_size: int = _DEFAULT_BATCH_SIZE,
                 max_errors: int = _DEFAULT_MAX_ERRORS):
        super().__init__(parent)
        self._db = db
        self._root_path = root_path
        self._batch_size = batch_size
        self._max_errors = max_errors
        self._state = ScanState()
        self._cancelled = False
        self._force = False
        self._added_paths: list[str] = []
        self._updated_paths: list[str] = []

    # ── Public API ──

    @property
    def state(self) -> ScanState:
        return self._state

    def cancel(self):
        self._cancelled = True
        self._state.cancel()

    def run(self, force: bool = False):
        """Execute the full indexing pipeline.

        When force=True, re-extracts metadata for all files (skips change
        detection) but preserves user-data fields: play_count, rating,
        last_played, favorites, track_uid.
        """
        self._force = force
        self._state.start(self._root_path)
        self._db.update_scan_root(self._root_path, last_scan_started=time.time())

        try:
            # Phase 1: Walk files
            self._state.set_phase(ScanPhase.WALKING)
            files = list(self._walk_files())
            self._state.file_count = len(files)

            if self._cancelled:
                return self._finish()

            # Process files: detect changes, extract metadata, build album keys
            self._state.set_phase(ScanPhase.EXTRACTING)
            batch_writer = BatchWriter(self._db.conn, batch_size=self._batch_size)

            # Pre-fetch user data map when force=True to preserve play_count/rating
            preserved_fields: dict[str, dict] = {}
            if force:
                preserved_fields = self._fetch_preserved_fields(files)

            for i, fp in enumerate(files):
                if self._cancelled:
                    break

                if self._state.error_count >= self._max_errors:
                    logger.warning(
                        "Indexer hit max_errors (%d) — stopping early",
                        self._max_errors)
                    break

                self._state.current_file = fp
                pct = ((i + 1) / max(self._state.file_count, 1)) * 100
                self._state.progress_pct = pct

                # Change detection — skipped when force=True
                if not force and self._is_unchanged(fp):
                    self._state.skipped_count += 1
                    self._db._touch_last_scanned(fp)
                    self._emit_progress(i)
                    continue

                # Is this a new file or an update?
                sig = self._db.get_file_signature(fp)
                is_new = sig is None

                # Extract metadata + build record
                try:
                    record = self._build_record(fp)
                    if record is not None:
                        # Inject preserved user data when force=True
                        if force and fp in preserved_fields:
                            pf = preserved_fields[fp]
                            record["play_count"] = pf.get("play_count", 0)
                            record["rating"] = pf.get("rating", 0)
                            record["last_played"] = pf.get("last_played", 0.0)
                            record["track_uid"] = pf.get("track_uid", "")
                            # Mark as reindexed, not new
                            is_new = False

                        stat = os.stat(fp)
                        record["updated_at"] = stat.st_mtime
                        record["last_scanned"] = time.time()
                        record["scan_status"] = "ok" if is_new else "updated"
                        now = time.time()
                        if is_new:
                            record["created_at"] = now

                        tuid = self._db._compute_track_uid(
                            fp, record.get("artist"), record.get("album"),
                            record.get("title"), record.get("duration", 0),
                            record.get("mb_track_id"))
                        record["track_uid"] = tuid

                        batch_writer.add(record)
                        if is_new:
                            self._state.added_count += 1
                            self._added_paths.append(fp)
                        else:
                            self._state.updated_count += 1
                            self._updated_paths.append(fp)
                    else:
                        self._state.skipped_count += 1
                except Exception as e:
                    self._state.error_count += 1
                    self._db.log_index_error(fp, str(e), "extract")

                # Flush when buffer is ready
                if batch_writer.buffered >= batch_writer.current_batch_size:
                    self._state.set_phase(ScanPhase.WRITING)
                    n = batch_writer.flush()
                    self.batch_complete.emit(n)

                self._emit_progress(i)

            # Phase 5: Flush remaining
            self._state.set_phase(ScanPhase.WRITING)
            n = batch_writer.flush()
            if n:
                self.batch_complete.emit(n)

            # Phase 6: Cleanup missing files — scoped by FileActions after scan
            missing = 0
            self._state.missing_count = missing
            self.cleanup_complete.emit(missing)

            # Phase 7: Rebuild UI indexes
            self._state.set_phase(ScanPhase.REBUILDING)
            self._rebuild_indexes()

            # Phase 8: Schedule enrichment
            self._state.set_phase(ScanPhase.ENRICHING)
            self._schedule_enrichment()

            # Phase 9: Sync track_genres from media_items
            self._sync_track_genres()

            self._db.update_scan_root(self._root_path,
                last_scan_finished=time.time(),
                file_count=self._state.file_count,
                added_count=self._state.added_count,
                updated_count=self._state.updated_count,
                skipped_count=self._state.skipped_count,
                missing_count=self._state.missing_count)

        except Exception as e:
            logger.error(f"Indexer failed: {e}")
            self._state.error_count += 1

        self._finish()

    # ── Pipeline phases ──

    def _walk_files(self):
        """FileWalker — recursive directory walk, yield audio files."""
        for root, dirs, fnames in os.walk(self._root_path):
            if self._cancelled:
                return
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for fn in sorted(fnames):
                if self._cancelled:
                    return
                if os.path.splitext(fn)[1].lower() in ALL_EXTS:
                    yield os.path.join(root, fn)

    def _is_unchanged(self, filepath: str) -> bool:
        """ChangeDetector — skip files that haven't changed since last scan."""
        try:
            stat = os.stat(filepath)
        except OSError:
            self._state.error_count += 1
            self._db.log_index_error(filepath, "stat failed", "detect")
            return True
        from library.change_detector import is_file_unchanged
        return is_file_unchanged(self._db, filepath, stat)


    def _build_record(self, filepath: str) -> dict | None:
        """MetadataExtractor + AlbumKeyBuilder — extract and normalize metadata.

        Delegates to MediaRecordBuilder for consistent field normalization.
        """
        from library.media_record_builder import MediaRecordBuilder
        builder = MediaRecordBuilder(db=self._db)
        result = builder.build(filepath)
        if result.errors or result.record is None:
            return None
        return result.record

    def _rebuild_indexes(self):
        """Rebuild SQLite indexes and FTS5 index for fast queries."""
        try:
            self._db.conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_media_artist ON media_items(artist)")
            self._db.conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_media_album ON media_items(album)")
            self._db.conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_media_albumartist ON media_items(albumartist)")
            self._db.conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_media_genre ON media_items(genre)")
            self._db.conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_media_year ON media_items(year)")
            self._db.conn.commit()
            from library.search_index import SearchIndex
            idx = SearchIndex(self._db.conn)
            if idx.fts_exists:
                idx.rebuild_fts()
        except Exception as e:
            logger.warning(f"Index rebuild failed: {e}")

    def _analyse_new_files(self):
        """Run Audio Lab diagnostics on newly added/updated files (best-effort)."""
        if self._cancelled:
            return
        try:
            from core.audio_lab.diagnostics_service import analyse_file
            from core.audio_lab.audio_lab_sync import sync_audio_lab_result_to_media_item
        except Exception:
            return

        paths = list(self._added_paths) + list(self._updated_paths)
        if not paths:
            return
        total = len(paths)
        for i, fp in enumerate(paths):
            if self._cancelled:
                break
            try:
                result = analyse_file(fp)
                if not result.get("error"):
                    sync_audio_lab_result_to_media_item(self._db.conn, fp, result)
            except Exception:
                pass
            self._state.progress_pct = ((i + 1) / total) * 100

    def _sync_track_genres(self):
        """Sync track_genres table after indexing new/modified files."""
        try:
            from library.genre_repository import GenreRepository
            repo = GenreRepository(self._db.conn)
            count = repo.backfill_from_media_items()
            if count:
                logger.info("Synced %d track_genre entries after index", count)
        except Exception as e:
            logger.warning("track_genre sync failed: %s", e)

    def _schedule_enrichment(self):
        """Request MusicBrainz enrichment for newly indexed artists."""
        try:
            rows = self._db.conn.execute(
                "SELECT DISTINCT albumartist, artist FROM media_items "
                "WHERE albumartist != '' OR artist != ''").fetchall()
            seen = set()
            for row in rows:
                name = normalize_artist_name(row[0] or row[1] or "")
                if name and name not in seen and name.lower() not in seen:
                    seen.add(name)
                    artist_key = make_artist_key(name)
                    self.enrichment_requested.emit(artist_key, name)
        except Exception as e:
            logger.warning(f"Enrichment scheduling failed: {e}")

    def _emit_progress(self, idx: int):
        total = max(self._state.file_count, 1)
        self.progress.emit(idx + 1, total, self._state.current_file)
        self.detail.emit(self._state.to_dict())

    def _finish(self):
        state = self._state
        if not state.cancelled:
            state.finish(ScanPhase.DONE)
        self.finished.emit(state.added_count + state.updated_count)
