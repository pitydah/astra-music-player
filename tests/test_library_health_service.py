"""Tests for LibraryHealthService."""
from unittest.mock import MagicMock

import pytest

from library.library_health_service import LibraryHealthService, LibraryHealthSummary


@pytest.fixture
def empty_db():
    """Return a MagicMock db that acts as an empty library."""
    mock = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (0,)
    mock_cursor.fetchall.return_value = []
    mock.conn.execute.return_value = mock_cursor
    return mock


@pytest.fixture
def populated_db():
    """Return a MagicMock db with 100 tracks, all healthy."""
    mock = MagicMock()

    results = {
        "SELECT COUNT(*) FROM media_items WHERE deleted_at IS NULL": [(100,)],
        "SELECT filepath FROM media_items WHERE deleted_at IS NULL AND scan_status != 'missing'": [],
        "SELECT COUNT(*) FROM media_items WHERE deleted_at IS NULL AND (COALESCE(title,'') = ''": [(0,)],
        "COUNT(DISTINCT COALESCE(albumartist, artist, ''))": [(0,)],
        "GROUP BY track_uid HAVING COUNT(*) > 1": [],
        "scan_status IN ('error', 'failed')": [(0,)],
        "spectral_verdict = 'suspicious'": [(0,)],
        "analysis_status IS NULL OR analysis_status = ''": [(0,)],
    }

    def execute(sql, params=None):
        mock_cursor = MagicMock()
        for pattern, result in results.items():
            if pattern in sql:
                mock_cursor.fetchone.return_value = result[0] if result else (0,)
                mock_cursor.fetchall.return_value = result
                return mock_cursor
        mock_cursor.fetchone.return_value = (0,)
        mock_cursor.fetchall.return_value = []
        return mock_cursor

    mock.conn.execute = execute
    return mock


class TestLibraryHealthSummary:
    def test_defaults(self):
        s = LibraryHealthSummary()
        assert s.total_tracks == 0
        assert s.score == 100
        assert s.status == "good"

    def test_to_dict(self):
        s = LibraryHealthSummary(total_tracks=50, missing_files=2, score=85, status="attention")
        d = s.to_dict()
        assert d["total_tracks"] == 50
        assert d["score"] == 85
        assert d["status"] == "attention"


class TestEmptyLibrary:
    def test_empty_summary(self, empty_db):
        svc = LibraryHealthService(db=empty_db)
        s = svc.summary()
        assert s.total_tracks == 0
        assert s.score == 0  # score is 0 for empty
        assert s.missing_files == 0
        assert s.missing_metadata == 0

    def test_empty_no_db(self):
        svc = LibraryHealthService(db=None)
        s = svc.summary()
        assert s.total_tracks == 0
        # Score is 0 because no tracks means no data


class TestScore:
    def test_perfect_score(self):
        assert LibraryHealthService._derive_status(100) == "good"

    def test_attention_score(self):
        assert LibraryHealthService._derive_status(75) == "attention"

    def test_critical_score(self):
        assert LibraryHealthService._derive_status(30) == "critical"

    def test_score_deduction_missing_files(self):
        s = LibraryHealthSummary(total_tracks=100, missing_files=10)
        score = LibraryHealthService._compute_score(s)
        assert score < 100
        assert score >= 0

    def test_score_zero_when_empty(self):
        s = LibraryHealthSummary(total_tracks=0)
        score = LibraryHealthService._compute_score(s)
        assert score == 0

    def test_score_floor(self):
        s = LibraryHealthSummary(total_tracks=100, missing_files=200)
        score = LibraryHealthService._compute_score(s)
        assert score == 0


class TestCountMethods:
    def test_count_tracks(self, empty_db):
        svc = LibraryHealthService(db=empty_db)
        assert svc._count_tracks() == 0

    def test_count_missing_files(self, empty_db):
        svc = LibraryHealthService(db=empty_db)
        assert svc._count_missing_files() == 0

    def test_count_missing_metadata(self, empty_db):
        svc = LibraryHealthService(db=empty_db)
        assert svc._count_missing_metadata() == 0

    def test_count_duplicates(self, empty_db):
        svc = LibraryHealthService(db=empty_db)
        assert svc._count_duplicates() == 0

    def test_count_scan_errors(self, empty_db):
        svc = LibraryHealthService(db=empty_db)
        assert svc._count_scan_errors() == 0

    def test_count_suspicious_audio(self, empty_db):
        svc = LibraryHealthService(db=empty_db)
        assert svc._count_suspicious_audio() == 0

    def test_count_pending_analysis(self, empty_db):
        svc = LibraryHealthService(db=empty_db)
        assert svc._count_pending_analysis() == 0
