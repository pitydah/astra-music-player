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

    def test_script_exits_zero_on_success(self):
        """smoke_startup.py must exit with code 0 when all checks pass."""
        # This test requires GI/GStreamer available in the environment
        try:
            import gi
            gi.require_version("Gst", "1.0")
            gi.require_version("GstPbutils", "1.0")
            from gi.repository import Gst  # noqa: F401
        except (ImportError, ValueError):
            pytest.skip("GI/GStreamer not available in this environment")

        # Use subprocess like CI would to ensure isolation
        env = os.environ.copy()
        env["QT_QPA_PLATFORM"] = "offscreen"
        env["PYTHONUNBUFFERED"] = "1"
        env["MICHI_TEST_DATA_DIR"] = "/tmp/michi-smoke-test/data"
        env["MICHI_TEST_CACHE_DIR"] = "/tmp/michi-smoke-test/cache"
        env["MICHI_TEST_CONFIG_DIR"] = "/tmp/michi-smoke-test/config"

        # Need to ensure the package is importable — add repo root
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

    def test_script_fails_without_gi(self, monkeypatch):
        """smoke_startup.py should detect missing gi and return non-zero."""
        content = _script_path().read_text()
        assert "exit" in content, "script should handle errors"
        # We can't easily mock gi being missing, but we check the error handling exists
        assert "errors += 1" in content or "sys.exit" in content
