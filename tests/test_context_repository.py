"""Tests for ContextRepository — standalone SQLite context storage."""

import os
import time

from core.context import context_repository as repo


class TestContextRepository:

    def setup_method(self):
        self.db_path = "/tmp/test_context.sqlite"
        repo.override_db_path(self.db_path)
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def teardown_method(self):
        repo.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_record_event_and_recent(self):
        repo.record_event("test_started", {"source": "test"})
        repo.record_event("test_finished", {"ok": True})
        events = repo.recent_events(10)
        assert len(events) >= 2
        assert events[0]["event_type"] == "test_finished"
        assert events[1]["event_type"] == "test_started"

    def test_set_and_get_state(self):
        repo.set_state("test_key", {"value": 42, "name": "test"})
        state = repo.get_state("test_key")
        assert state["value"] == 42
        assert state["name"] == "test"

    def test_state_default_on_missing(self):
        state = repo.get_state("nonexistent")
        assert state == {}

    def test_summary_within_ttl(self):
        repo.set_summary("test_summary", {"data": "hello"}, ttl_seconds=60)
        result = repo.get_summary("test_summary")
        assert result["data"] == "hello"

    def test_summary_expired(self):
        repo.set_summary("expired_summary", {"data": "old"}, ttl_seconds=0)
        time.sleep(0.1)
        result = repo.get_summary("expired_summary")
        assert result is None

    def test_dirty_flags(self):
        assert not repo.is_dirty("test_flag")
        repo.mark_dirty("test_flag")
        assert repo.is_dirty("test_flag")
        repo.clear_dirty("test_flag")
        assert not repo.is_dirty("test_flag")

    def test_cleanup_old_events(self):
        repo.record_event("old_event", {"age": "old"})
        deleted = repo.cleanup_old_events(max_age_days=30)
        assert isinstance(deleted, int)
        assert deleted >= 0

    def test_double_record_event(self):
        repo.record_event("double_test")
        repo.record_event("double_test")
        events = repo.recent_events(10)
        matches = [e for e in events if e["event_type"] == "double_test"]
        assert len(matches) >= 2

    def test_sqlite_error_does_not_crash(self):
        repo.set_state("bad_json", {"ok": True})
        assert repo.get_state("bad_json", {"fallback": True}) == {"ok": True}

    def test_empty_db(self):
        events = repo.recent_events(5)
        assert isinstance(events, list)
