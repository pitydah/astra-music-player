"""Tests for smart_mixes — verifies SQL queries work with real data."""

import sqlite3
import hashlib
import time
import pytest

from library.smart_mixes import (
    get_daily_mix, get_unplayed, get_popular,
    get_by_genre, get_favorites_recent,
)


def _make_track_id(filepath: str) -> str:
    return hashlib.sha256(filepath.encode()).hexdigest()[:16]


@pytest.fixture
def db_path(tmp_path, monkeypatch):
    """Create a test DB with media_items, play_history, favorites."""
    db = tmp_path / "test_library.db"
    conn = sqlite3.connect(str(db))

    conn.executescript("""
        CREATE TABLE media_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filepath TEXT NOT NULL,
            title TEXT,
            artist TEXT,
            album TEXT,
            genre TEXT,
            year INTEGER,
            date_added REAL
        );
        CREATE TABLE play_history (
            track_id TEXT NOT NULL,
            device TEXT NOT NULL,
            play_count INTEGER DEFAULT 0,
            last_played REAL DEFAULT 0,
            PRIMARY KEY (track_id, device)
        );
        CREATE TABLE favorites (
            track_id TEXT NOT NULL,
            device TEXT NOT NULL,
            PRIMARY KEY (track_id, device)
        );
    """)

    now = time.time()
    week_ago = now - 700000  # > 7 days (604800) to be excluded

    # Insert tracks
    tracks = [
        ("/music/a.mp3", "Song A", "Artist One", "Album X", "rock", 2020),
        ("/music/b.mp3", "Song B", "Artist Two", "Album Y", "jazz", 2021),
        ("/music/c.mp3", "Song C", "Artist One", "Album X", "pop", 2022),
        ("/music/d.mp3", "Song D", "Artist Three", "Album Z", "rock", 2019),
    ]
    for fp, title, artist, album, genre, year in tracks:
        conn.execute(
            "INSERT INTO media_items (filepath, title, artist, album, genre, year, date_added) "
            "VALUES (?,?,?,?,?,?,?)",
            (fp, title, artist, album, genre, year, now))

    # Play history
    conn.execute(
        "INSERT INTO play_history (track_id, device, play_count, last_played) "
        "VALUES (?,?,?,?)",
        (_make_track_id("/music/a.mp3"), "desktop", 10, now))
    conn.execute(
        "INSERT INTO play_history (track_id, device, play_count, last_played) "
        "VALUES (?,?,?,?)",
        (_make_track_id("/music/b.mp3"), "desktop", 5, now))
    # c.mp3 was played a long time ago
    conn.execute(
        "INSERT INTO play_history (track_id, device, play_count, last_played) "
        "VALUES (?,?,?,?)",
        (_make_track_id("/music/c.mp3"), "desktop", 2, week_ago))

    # Favorites
    conn.execute(
        "INSERT INTO favorites (track_id, device) VALUES (?,?)",
        (_make_track_id("/music/b.mp3"), "desktop"))

    conn.commit()
    conn.close()

    # Override DB_PATH
    monkeypatch.setattr("library.smart_mixes.DB_PATH", str(db))
    return db


def test_get_popular(db_path):
    results = get_popular(limit=10)
    assert len(results) == 3
    assert results[0] == "/music/a.mp3"  # play_count=10
    assert results[1] == "/music/b.mp3"  # play_count=5


def test_get_daily_mix(db_path):
    results = get_daily_mix(limit=10)
    # Only a.mp3 and b.mp3 have recent plays
    assert len(results) == 2
    assert results[0] == "/music/a.mp3"


def test_get_unplayed(db_path):
    results = get_unplayed(limit=10)
    # d.mp3 has no play history at all
    assert len(results) >= 1
    assert "/music/d.mp3" in results
    assert "/music/a.mp3" not in results  # has play history


def test_get_by_genre(db_path):
    results = get_by_genre("rock", limit=10)
    assert len(results) == 2
    assert "/music/a.mp3" in results
    assert "/music/d.mp3" in results


def test_get_favorites(db_path):
    results = get_favorites_recent(limit=10)
    assert len(results) == 1
    assert results[0] == "/music/b.mp3"


def test_empty_db(tmp_path, monkeypatch):
    """Smart mixes should return [] for empty DB, not crash."""
    empty = tmp_path / "empty.db"
    conn = sqlite3.connect(str(empty))
    conn.executescript("""
        CREATE TABLE media_items (id INTEGER, filepath TEXT);
    """)
    conn.commit()
    conn.close()
    monkeypatch.setattr("library.smart_mixes.DB_PATH", str(empty))

    assert get_daily_mix() == []
    assert get_unplayed() == []
    assert get_popular() == []
    assert get_favorites_recent() == []
    assert get_by_genre("any") == []
