"""Tests for smoke_startup.py — pre-beta startup validation."""
import os
import subprocess
import sys
from pathlib import Path

import pytest


def _script_path() -> Path:
    repo_root = Path(__file__).resolve().parent.parent
    return repo_root / "scripts" / "smoke_startup.py"


class TestSmokeStartupScript:
    def test_script_exists(self):
        """smoke_startup.py must exist."""
        assert _script_path().is_file()

    def test_script_checks_gst(self):
        """smoke_startup.py must verify GStreamer."""
        content = _script_path().read_text()
        assert 'gi.require_version("Gst", "1.0")' in content

    def test_script_checks_gst_pbutils(self):
        """smoke_startup.py must verify GstPbutils."""
        content = _script_path().read_text()
        assert 'gi.require_version("GstPbutils", "1.0")' in content

    def test_script_uses_michi_test_data_dir(self):
        """smoke_startup.py must use MICHI_TEST_DATA_DIR."""
        content = _script_path().read_text()
        assert "MICHI_TEST_DATA_DIR" in content

    def test_script_uses_qt_qpa_offscreen(self):
        """smoke_startup.py must set QT_QPA_PLATFORM=offscreen."""
        content = _script_path().read_text()
        assert "offscreen" in content

    def test_script_checks_db(self):
        """smoke_startup.py must validate LibraryDB."""
        content = _script_path().read_text()
        assert "LibraryDB" in content

    def test_script_uses_finally(self):
        """smoke_startup.py must use try/finally for cleanup."""
        content = _script_path().read_text()
        assert "finally" in content

    def test_script_calls_db_close(self):
        """smoke_startup.py must close the database."""
        content = _script_path().read_text()
        assert "db.close()" in content

    def test_script_has_error_exit_path(self):
        """smoke_startup.py must handle errors and exit non-zero."""
        content = _script_path().read_text()
        assert "errors += 1" in content

    def test_script_exits_zero_on_success(self, tmp_path):
        """smoke_startup.py must exit with code 0 when all checks pass."""
        try:
            import gi
            gi.require_version("Gst", "1.0")
            gi.require_version("GstPbutils", "1.0")
            from gi.repository import Gst  # noqa: F401
        except (ImportError, ValueError):
            pytest.skip("GI/GStreamer not available in this environment")

        env = os.environ.copy()
        env["QT_QPA_PLATFORM"] = "offscreen"
        env["PYTHONUNBUFFERED"] = "1"
        env["MICHI_TEST_DATA_DIR"] = str(tmp_path / "data")
        env["MICHI_TEST_CACHE_DIR"] = str(tmp_path / "cache")
        env["MICHI_TEST_CONFIG_DIR"] = str(tmp_path / "config")

        repo_root = str(Path(__file__).resolve().parent.parent)
        env.setdefault("PYTHONPATH", "")
        if repo_root not in env.get("PYTHONPATH", "").split(os.pathsep):
            env["PYTHONPATH"] = repo_root + os.pathsep + env.get("PYTHONPATH", "")

        result = subprocess.run(
            [sys.executable, str(_script_path())],
            capture_output=True, text=True, timeout=60, env=env,
        )
        if result.returncode != 0:
            print(result.stdout)
            print(result.stderr)
        assert result.returncode == 0, f"smoke_startup failed: {result.stderr}"
        # DB should have been created inside tmp_path/data
        db_file = tmp_path / "data" / "library.db"
        assert db_file.is_file(), f"DB file not found at {db_file}"
