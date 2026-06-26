"""Centralized logger for Michi Music Player.

Logs to ~/.local/share/michi-music-player/michi.log (rotating, 5MB x 3 backups).
Console output only when MICHI_DEBUG=1 or --debug flag.
"""

import logging
import logging.handlers
import os
import sys

LOG_DIR = os.path.expanduser("~/.local/share/michi-music-player")
LOG_FILE = os.path.join(LOG_DIR, "michi.log")


def _is_debug() -> bool:
    return os.environ.get("MICHI_DEBUG") == "1" or "--debug" in sys.argv


def setup_logging():
    os.makedirs(LOG_DIR, exist_ok=True)

    logger = logging.getLogger("michi")
    logger.setLevel(logging.DEBUG if _is_debug() else logging.INFO)

    if logger.handlers:
        return

    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Rotating file handler — 5 MB, 3 backups
    fh = logging.handlers.RotatingFileHandler(
        LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    if _is_debug():
        ch = logging.StreamHandler(sys.stderr)
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(fmt)
        logger.addHandler(ch)

    # Suppress noisy third-party loggers
    logging.getLogger("PIL").setLevel(logging.WARNING)

    # Log runtime environment
    _log = logging.getLogger("michi.runtime")
    _log.info("Python %s · PySide6 %s", sys.version.split()[0], _pyside_version())
    _log.info("Log file: %s", LOG_FILE)


def _pyside_version() -> str:
    try:
        from PySide6 import __version_info__
        return ".".join(map(str, __version_info__[:3]))
    except Exception:
        return "unknown"


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"michi.{name}")


# Auto-setup on import
setup_logging()
