"""Tests for RadioManager."""
import json
import os
import tempfile
from streaming.radio_manager import RadioManager


def test_load_empty():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump([], f)
        path = f.name
    try:
        import streaming.radio_manager as rm
        orig = rm.RADIO_FILE
        rm.RADIO_FILE = path
        mgr = RadioManager()
        assert mgr.count() == 0
        rm.RADIO_FILE = orig
    finally:
        os.unlink(path)


def test_add_station():
    mgr = RadioManager()
    mgr._stations = []
    s = mgr.add("BBC Radio 1", "http://bbc.co.uk/stream")
    assert s.name == "BBC Radio 1"
    assert s.url == "http://bbc.co.uk/stream"
    assert s.id > 0
    assert mgr.count() == 1


def test_remove_station():
    mgr = RadioManager()
    mgr._stations = []
    s = mgr.add("Test", "http://test.com/stream")
    assert mgr.count() == 1
    assert mgr.remove(s.id) is True
    assert mgr.count() == 0


def test_update_station():
    mgr = RadioManager()
    mgr._stations = []
    s = mgr.add("Test", "http://test.com/stream")
    mgr.update(s.id, "Updated", "http://updated.com/stream")
    stations = mgr.get_all()
    assert stations[0].name == "Updated"


def test_duplicate():
    mgr = RadioManager()
    mgr._stations = []
    s = mgr.add("Test", "http://test.com/stream")
    dup = mgr.duplicate(s.id)
    assert dup is not None
    assert dup.name == "Test (copia)"
    assert dup.url == s.url
    assert dup.id != s.id


def test_toggle_favorite():
    mgr = RadioManager()
    mgr._stations = []
    s = mgr.add("Test", "http://test.com/stream")
    assert s.favorite is False
    result = mgr.toggle_favorite(s.id)
    assert result is True
    assert mgr.get_all()[0].favorite is True


def test_find_by_url():
    mgr = RadioManager()
    mgr._stations = []
    mgr.add("BBC", "http://bbc.co.uk/stream")
    found = mgr.find_by_url("http://bbc.co.uk/stream")
    assert found is not None
    assert found.name == "BBC"
    not_found = mgr.find_by_url("http://nonexistent.com")
    assert not_found is None


def test_mark_played():
    mgr = RadioManager()
    mgr._stations = []
    s = mgr.add("Test", "http://test.com/stream")
    assert s.play_count == 0
    mgr.mark_played(s.id)
    updated = mgr.get_all()[0]
    assert updated.play_count == 1
    assert updated.last_played != ""


def test_load_old_json_without_new_fields():
    old_data = [{"name": "Old", "url": "http://old.com", "id": 1}]
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(old_data, f)
        path = f.name
    try:
        import streaming.radio_manager as rm
        orig = rm.RADIO_FILE
        rm.RADIO_FILE = path
        mgr = RadioManager()
        stations = mgr.get_all()
        assert len(stations) == 1
        s = stations[0]
        assert s.name == "Old"
        assert s.tags == []
        assert s.favorite is False
        assert s.play_count == 0
        rm.RADIO_FILE = orig
    finally:
        os.unlink(path)
