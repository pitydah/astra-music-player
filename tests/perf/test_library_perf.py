"""Performance tests for library operations.

Run with: pytest tests/perf/ -m perf -v
"""

import time
import pytest

from library.library_db import LibraryDB
from tests.perf.generate_library import generate


@pytest.mark.perf
class TestLibraryPerformance:

    SAMPLE_SIZE = 5_000

    @pytest.fixture
    def perf_db(self, tmp_path):
        db_path = str(tmp_path / "perf_library.db")
        db = LibraryDB(db_path)
        generate(db, str(tmp_path / "music"), count=self.SAMPLE_SIZE)
        yield db
        db.close()

    def test_get_all_under_2_5s(self, perf_db):
        start = time.perf_counter()
        tracks = perf_db.get_all()
        elapsed = time.perf_counter() - start
        assert len(tracks) >= self.SAMPLE_SIZE * 0.9
        assert elapsed < 2.5, f"get_all took {elapsed:.2f}s (limit 2.5s)"

    def test_search_advanced_under_1_0s(self, perf_db):
        start = time.perf_counter()
        _results = perf_db.search_advanced("Artist_1")
        elapsed = time.perf_counter() - start
        assert elapsed < 1.0, f"search_advanced took {elapsed:.2f}s (limit 1.0s)"

    def test_stats_under_1_0s(self, perf_db):
        start = time.perf_counter()
        _stats = perf_db.get_stats()
        elapsed = time.perf_counter() - start
        assert elapsed < 1.0, f"get_stats took {elapsed:.2f}s (limit 1.0s)"

    def test_cleanup_missing_under_0_2s(self, perf_db, tmp_path):
        start = time.perf_counter()
        removed = perf_db.cleanup_missing_under_root(str(tmp_path / "nonexistent"))
        elapsed = time.perf_counter() - start
        assert elapsed < 0.2, f"cleanup_missing took {elapsed:.2f}s (limit 0.2s)"
        assert removed == 0
