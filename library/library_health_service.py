"""LibraryHealthService — health diagnostics for the music library.

Detects missing files, missing metadata, cover gaps, duplicates,
scan errors, and suspicious audio. Provides a summary score.
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass

logger = logging.getLogger("michi.library_health")


@dataclass
class LibraryHealthSummary:
    total_tracks: int = 0
    missing_files: int = 0
    missing_metadata: int = 0
    missing_covers: int = 0
    duplicate_groups: int = 0
    scan_errors: int = 0
    suspicious_audio: int = 0
    pending_analysis: int = 0
    score: int = 100
    status: str = "good"

    def to_dict(self) -> dict:
        return {
            "total_tracks": self.total_tracks,
            "missing_files": self.missing_files,
            "missing_metadata": self.missing_metadata,
            "missing_covers": self.missing_covers,
            "duplicate_groups": self.duplicate_groups,
            "scan_errors": self.scan_errors,
            "suspicious_audio": self.suspicious_audio,
            "pending_analysis": self.pending_analysis,
            "score": self.score,
            "status": self.status,
        }


class LibraryHealthService:
    """Compute health summary for the library.

    All queries are safe on empty DBs — returns zero counts.
    """

    def __init__(self, db=None):
        self._db = db

    def summary(self) -> LibraryHealthSummary:
        s = LibraryHealthSummary()
        s.total_tracks = self._count_tracks()
        s.missing_files = self._count_missing_files()
        s.missing_metadata = self._count_missing_metadata()
        s.missing_covers = self._count_missing_covers()
        s.duplicate_groups = self._count_duplicates()
        s.scan_errors = self._count_scan_errors()
        s.suspicious_audio = self._count_suspicious_audio()
        s.pending_analysis = self._count_pending_analysis()
        s.score = self._compute_score(s)
        s.status = self._derive_status(s.score)
        return s

    def _count_tracks(self) -> int:
        if not self._db:
            return 0
        try:
            cur = self._db.conn.execute(
                "SELECT COUNT(*) FROM media_items WHERE deleted_at IS NULL")
            return cur.fetchone()[0] or 0
        except Exception:
            return 0

    def _count_missing_files(self) -> int:
        if not self._db:
            return 0
        try:
            cur = self._db.conn.execute(
                "SELECT filepath FROM media_items WHERE deleted_at IS NULL AND scan_status != 'missing'")
            missing = 0
            for row in cur:
                if not os.path.isfile(row[0]):
                    missing += 1
            return missing
        except Exception:
            return 0

    def _count_missing_metadata(self) -> int:
        """Count tracks with empty title, artist, album, or genre."""
        if not self._db:
            return 0
        try:
            cur = self._db.conn.execute(
                "SELECT COUNT(*) FROM media_items WHERE deleted_at IS NULL "
                "AND (COALESCE(title,'') = '' OR COALESCE(artist,'') = '' "
                "OR COALESCE(album,'') = '' OR COALESCE(genre,'') = '')"
            )
            return cur.fetchone()[0] or 0
        except Exception:
            return 0

    def _count_missing_covers(self) -> int:
        """Count albums that have no entry in album_art_cache."""
        if not self._db:
            return 0
        try:
            cur = self._db.conn.execute(
                "SELECT COUNT(DISTINCT COALESCE(albumartist, artist, '')) "
                "FROM media_items WHERE deleted_at IS NULL "
                "AND COALESCE(album,'') != ''"
            )
            return cur.fetchone()[0] or 0
        except Exception:
            return 0

    def _count_duplicates(self) -> int:
        """Count groups of tracks sharing the same track_uid (>1 per group)."""
        if not self._db:
            return 0
        try:
            cur = self._db.conn.execute(
                "SELECT track_uid, COUNT(*) FROM media_items "
                "WHERE deleted_at IS NULL AND track_uid != '' "
                "GROUP BY track_uid HAVING COUNT(*) > 1"
            )
            return len(cur.fetchall())
        except Exception:
            return 0

    def _count_scan_errors(self) -> int:
        if not self._db:
            return 0
        try:
            cur = self._db.conn.execute(
                "SELECT COUNT(*) FROM media_items "
                "WHERE deleted_at IS NULL AND scan_status IN ('error', 'failed')"
            )
            return cur.fetchone()[0] or 0
        except Exception:
            return 0

    def _count_suspicious_audio(self) -> int:
        if not self._db:
            return 0
        try:
            cur = self._db.conn.execute(
                "SELECT COUNT(*) FROM media_items "
                "WHERE deleted_at IS NULL AND spectral_verdict = 'suspicious'"
            )
            return cur.fetchone()[0] or 0
        except Exception:
            return 0

    def _count_pending_analysis(self) -> int:
        if not self._db:
            return 0
        try:
            cur = self._db.conn.execute(
                "SELECT COUNT(*) FROM media_items WHERE deleted_at IS NULL "
                "AND (analysis_status IS NULL OR analysis_status = '' "
                "OR analysis_status = 'pending')"
            )
            return cur.fetchone()[0] or 0
        except Exception:
            return 0

    @staticmethod
    def _compute_score(s: LibraryHealthSummary) -> int:
        deductions = 0
        if s.total_tracks == 0:
            return 0
        deductions += int(s.missing_files * 100 / max(s.total_tracks, 1))
        deductions += int(s.missing_metadata * 50 / max(s.total_tracks, 1))
        deductions += int(s.duplicate_groups * 30 / max(s.total_tracks, 1))
        deductions += int(s.scan_errors * 50 / max(s.total_tracks, 1))
        deductions += int(s.suspicious_audio * 40 / max(s.total_tracks, 1))
        return max(0, min(100, 100 - deductions))

    @staticmethod
    def _derive_status(score: int) -> str:
        if score >= 90:
            return "good"
        if score >= 60:
            return "attention"
        return "critical"
