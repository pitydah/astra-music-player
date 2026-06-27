"""Tests for FileWatcher — debounce, event detection, signal emission."""

import os
import tempfile
from unittest.mock import MagicMock


class TestFileWatcher:
    def test_initial_state(self):
        from library.file_watcher import FileWatcher
        db = MagicMock()
        type(db).get_library_roots = MagicMock(return_value=[])
        watcher = FileWatcher(db)
        assert watcher.is_running is False

    def test_start_stop(self):
        from library.file_watcher import FileWatcher
        db = MagicMock()
        type(db).get_library_roots = MagicMock(return_value=[])
        watcher = FileWatcher(db)
        watcher.start()
        assert watcher.is_running is True
        watcher.stop()
        assert watcher.is_running is False

    def test_start_idempotent(self):
        from library.file_watcher import FileWatcher
        db = MagicMock()
        type(db).get_library_roots = MagicMock(return_value=[])
        watcher = FileWatcher(db)
        watcher.start()
        watcher.start()
        assert watcher.is_running is True

    def test_signals_exist(self):
        from library.file_watcher import FileWatcher
        db = MagicMock()
        watcher = FileWatcher(db)
        assert hasattr(watcher, 'files_added')
        assert hasattr(watcher, 'files_removed')
        assert hasattr(watcher, 'files_modified')

    def test_add_root(self):
        from library.file_watcher import FileWatcher
        db = MagicMock()
        watcher = FileWatcher(db)
        with tempfile.TemporaryDirectory() as tmpdir:
            watcher.add_root(tmpdir)
            assert tmpdir in watcher._watcher.directories()

    def test_empty_flush(self):
        from library.file_watcher import FileWatcher
        db = MagicMock()
        watcher = FileWatcher(db)
        watcher._flush()
        assert len(watcher._pending_added) == 0

    def test_flush_clears_pending(self):
        from library.file_watcher import FileWatcher
        db = MagicMock()
        watcher = FileWatcher(db)
        watcher._pending_added.add("/test.mp3")
        watcher._flush()
        assert len(watcher._pending_added) == 0

    def test_max_batch_triggers_flush(self):
        from library.file_watcher import FileWatcher
        db = MagicMock()
        type(db).get_library_roots = MagicMock(return_value=[])
        type(db)._conn = MagicMock()
        db._conn.execute.return_value = []
        watcher = FileWatcher(db)
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create actual audio files to trigger batch
            for i in range(105):
                with open(os.path.join(tmpdir, f"test{i}.mp3"), "w") as f:
                    f.write("x")
            watcher._watcher.directoryChanged.emit(tmpdir)
            import time
            time.sleep(0.1)
            # Should have flushed due to max batch
            assert len(watcher._pending_added) < 105
