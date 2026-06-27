#!/usr/bin/env python3
"""Michi Music Player — smoke startup validation.

Validates critical runtime components can initialize without real audio,
real user data, or external services. Designed for CI and pre-beta testing.

Usage:
    python3 scripts/smoke_startup.py

Environment (set automatically if missing):
    QT_QPA_PLATFORM=offscreen
    MICHI_TEST_DATA_DIR, MICHI_TEST_CACHE_DIR, MICHI_TEST_CONFIG_DIR
"""
import os
import sys
import tempfile

# Add repo root to path so the package can be imported when running from source
_repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)


def _ensure_env():
    """Set safe defaults for test environment if not already set."""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    tmp = tempfile.mkdtemp(prefix="michi-smoke-")
    os.environ.setdefault("MICHI_TEST_DATA_DIR", os.path.join(tmp, "data"))
    os.environ.setdefault("MICHI_TEST_CACHE_DIR", os.path.join(tmp, "cache"))
    os.environ.setdefault("MICHI_TEST_CONFIG_DIR", os.path.join(tmp, "config"))
    return tmp


def _diagnostics():
    print(f"  Python:     {sys.executable}")
    print(f"  Version:    {sys.version.split()[0]}")
    print(f"  QT_QPA:     {os.environ.get('QT_QPA_PLATFORM', 'NOT SET')}")
    print(f"  DATA_DIR:   {os.environ.get('MICHI_TEST_DATA_DIR', 'NOT SET')}")
    print(f"  CACHE_DIR:  {os.environ.get('MICHI_TEST_CACHE_DIR', 'NOT SET')}")
    print(f"  CONFIG_DIR: {os.environ.get('MICHI_TEST_CONFIG_DIR', 'NOT SET')}")


def _check_imports():
    errors = 0
    checks = [
        ("PySide6", None),
        ("mutagen", None),
        ("numpy", None),
    ]
    for name, _ in checks:
        try:
            __import__(name)
            print(f"  ✓ {name}")
        except ImportError as e:
            print(f"  ✗ {name}: {e}")
            errors += 1
    return errors


def _check_gst():
    try:
        import gi
        gi.require_version("Gst", "1.0")
        gi.require_version("GstPbutils", "1.0")
        from gi.repository import Gst, GstPbutils  # noqa: F401
        Gst.init(None)
        print(f"  ✓ GStreamer {Gst.version_string()}")
        print(f"  ✓ GstPbutils ({GstPbutils})")
        return 0
    except Exception as e:
        print(f"  ✗ PyGObject/GStreamer: {e!r}")
        return 1


def _check_paths():
    from core.paths import (
        app_data_dir, app_cache_dir, app_config_dir,
        database_path, covers_cache_dir, log_file,
    )
    for label, path_fn in [
        ("app_data_dir", app_data_dir),
        ("app_cache_dir", app_cache_dir),
        ("app_config_dir", app_config_dir),
        ("database_path", database_path),
        ("covers_cache_dir", covers_cache_dir),
        ("log_file", log_file),
    ]:
        p = path_fn()
        d = os.path.dirname(p) if "." in os.path.basename(p) else p
        os.makedirs(d, exist_ok=True)
        print(f"  ✓ {label}: {p}")
    return 0


def _check_db():
    from core.paths import database_path
    from library.library_db import LibraryDB
    db_path = database_path()
    db = LibraryDB(db_path)
    # Verify the DB file exists and is under MICHI_TEST_DATA_DIR
    assert os.path.isfile(db_path), f"DB file not created: {db_path}"
    data_dir = os.environ.get("MICHI_TEST_DATA_DIR", "")
    assert db_path.startswith(data_dir), (
        f"DB path {db_path} not under test data dir {data_dir}"
    )
    print(f"  ✓ LibraryDB created at {db_path}")
    # Quick sanity: execute a query
    result = db.get_all()
    print(f"  ✓ DB query (get_all): {len(result)} items")
    db.close()
    return 0


def _check_qt():
    from PySide6.QtWidgets import QApplication, QLabel
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    label = QLabel("Michi Smoke Test")
    label.setWindowTitle("Michi Smoke Test")
    print(f"  ✓ QApplication initialized (platform: {app.platformName()})")
    print("  ✓ QLabel created")
    return 0


def main():
    errors = 0

    print("=== Michi Music Player — Smoke Startup ===")
    print()

    tmp_root = _ensure_env()
    print("[1/7] Environment")
    _diagnostics()
    print()

    print("[2/7] Python imports")
    errors += _check_imports()
    print()

    print("[3/7] PyGObject / GStreamer")
    errors += _check_gst()
    print()

    print("[4/7] XDG paths")
    errors += _check_paths()
    print()

    print("[5/7] SQLite database")
    errors += _check_db()
    print()

    print("[6/7] Qt widgets")
    errors += _check_qt()
    print()

    print("[7/7] Summary")
    if errors:
        print(f"  ✗ {errors} error(s) detected")
    else:
        print("  ✓ All checks passed")

    # Cleanup temp dir
    import shutil
    shutil.rmtree(tmp_root, ignore_errors=True)

    sys.exit(errors)


if __name__ == "__main__":
    main()
