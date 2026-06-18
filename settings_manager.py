"""Settings Manager — unified QSettings for Astra Music Player."""

import os
import json
from PySide6.QtCore import QSettings


SETTINGS = QSettings("Astra", "MusicPlayer")

DEFAULTS = {
    "general/start_minimized": False,
    "general/confirm_exit": False,
    "general/remember_session": True,
    "general/music_folder": os.path.expanduser("~/Música"),
    "general/download_folder": os.path.expanduser("~/Descargas"),
    "interface/show_menubar": True,
    "interface/show_quality_badge": True,
    "interface/cover_size": 260,
    "interface/compact_mode": False,
    "library/auto_scan": False,
    "library/exclude_hidden": True,
    "library/covers_cache_size": 100,
    "playback/default_volume": 70,
    "playback/repeat_mode": "none",
    "playback/shuffle_default": False,
    "playback/replaygain": False,
    "playback/crossfade": 0,
    "playback/gapless": True,
    "audio/device": "default",
    "audio/mode": "standard",
    "audio/sample_rate": 0,
    "audio/buffer_ms": 100,
    "eq/enabled": False,
    "eq/mode": "graphic",
    "eq/preamp": 0.0,
    "eq/preset": "Flat",
    "eq/show_spectrum": False,
    "transmit/quality": "320",
    "transmit/latency": 0,
    "transmit/keep_local": True,
    "sync/auto_start": False,
    "sync/port": 53318,
    "sync/alias": "Astra PC",
    "sync/discovery_enabled": True,
    "sync/announce_interval": 5,
    "radio/auto_update": True,
    "radio/auto_reconnect": True,
    "radio/reconnect_interval": 5,
    "radio/record_streams": False,
    "radio/record_folder": os.path.expanduser("~/Música/Grabaciones"),
    "shortcuts/global_enabled": False,
    "advanced/debug_log": False,
    "advanced/log_level": "Error",
    "advanced/thread_limit": 4,
}


def get(key: str):
    return SETTINGS.value(key, DEFAULTS.get(key))


def set_(key: str, value):
    SETTINGS.setValue(key, value)


def export_to_file(path: str):
    data = {k: get(k) for k in DEFAULTS}
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def import_from_file(path: str):
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    with open(path) as f:
        data = json.load(f)
    for k, v in data.items():
        if k in DEFAULTS:
            set_(k, v)


def restore_defaults():
    for k in DEFAULTS:
        set_(k, DEFAULTS[k])
