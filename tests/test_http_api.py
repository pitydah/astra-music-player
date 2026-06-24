"""Behavior tests for Michi HTTP API — auth, player control, library browsing.

Tests against current main branch. Documents gaps where error handling is missing.
"""
import json
from unittest.mock import MagicMock


def _request(method, path, body=None, bridge=None, db=None, store=None,
             server_token="test", auth_token="test"):
    """Simulate an HTTP request using the real handler."""
    from integrations.http_api.http_api import _AstraHandler
    import io as _io

    h = _AstraHandler.__new__(_AstraHandler)
    h._bridge = bridge
    h._db = db
    h._store = store
    h._token = server_token
    h.path = path
    h.headers = {}
    if auth_token is not None:
        h.headers["Authorization"] = f"Bearer {auth_token}"
    h.headers["Content-Length"] = "0"
    h.status_code = None
    h.response_data = None
    h.rfile = _io.BytesIO(b"")
    h.wfile = _io.BytesIO()

    def _send_json(code, data):
        h.status_code = code
        h.response_data = data
        h.send_response = lambda c: None
        h.send_header = lambda *a: None
        h.end_headers = lambda: None
    h._send_json = _send_json

    if body is not None:
        body_bytes = json.dumps(body).encode()
        h.rfile = _io.BytesIO(body_bytes)
        h.headers["Content-Length"] = str(len(body_bytes))
    h.wfile = _io.BytesIO()

    if method == "GET":
        h.do_GET()
    elif method == "POST":
        h.do_POST()
    return h.status_code, h.response_data


class TestPlayerStatus:
    def test_status_returns_200(self):
        store = MagicMock()
        store.player_snapshot.return_value = {"state": "playing", "title": "S", "artist": "A",
                                              "duration": 200, "position": 30, "volume": 70}
        code, data = _request("GET", "/api/player/status", store=store)
        assert code == 200
        assert data["state"] == "playing"
        assert data["volume"] == 70

    def test_status_no_store_returns_empty(self):
        code, data = _request("GET", "/api/player/status", store=None)
        assert code == 200
        assert data["state"] == "idle"


class TestPlayerControl:
    def test_play_no_bridge_returns_200(self):
        """DOCUMENTED GAP: POST play returns 200 even without bridge."""
        code, data = _request("POST", "/api/player/play", body={})
        assert code == 200
        assert data["status"] == "ok"

    def test_play_with_bridge(self):
        bridge = MagicMock()
        code, data = _request("POST", "/api/player/play", body={}, bridge=bridge)
        assert code == 200
        bridge.play_requested.emit.assert_called_once()

    def test_pause_with_bridge(self):
        bridge = MagicMock()
        code, data = _request("POST", "/api/player/pause", body={}, bridge=bridge)
        assert code == 200
        bridge.pause_requested.emit.assert_called_once()

    def test_next_with_bridge(self):
        bridge = MagicMock()
        code, data = _request("POST", "/api/player/next", body={}, bridge=bridge)
        assert code == 200
        bridge.next_requested.emit.assert_called_once()

    def test_stop_with_bridge(self):
        bridge = MagicMock()
        code, data = _request("POST", "/api/player/stop", body={}, bridge=bridge)
        assert code == 200
        bridge.stop_requested.emit.assert_called_once()

    def test_volume_with_bridge(self):
        bridge = MagicMock()
        code, data = _request("POST", "/api/player/volume", body={"volume": 42}, bridge=bridge)
        assert code == 200
        bridge.volume_requested.emit.assert_called_once_with(42)


class TestAuth:
    def test_no_token_returns_401(self):
        code, data = _request("GET", "/api/player/status", auth_token=None)
        assert code == 401

    def test_wrong_token_returns_403(self):
        code, data = _request("GET", "/api/player/status", auth_token="wrong")
        assert code == 403


class TestLibraryBrowse:
    def test_root_returns_children(self):
        db = MagicMock()
        store = MagicMock()
        store.player_snapshot.return_value = {}
        code, data = _request("GET", "/api/library/browse", db=db, store=store)
        assert code == 200
        assert "children" in data
        children_ids = [c["id"] for c in data["children"]]
        assert "folders" in children_ids
        assert "artists" in children_ids
        assert "favs" in children_ids
        assert "recent" in children_ids

    def test_favs_uses_db_get_all(self):
        """DOCUMENTED GAP: favs calls db.get_all(kind='fav'), not db.get_favorites()."""
        db = MagicMock()
        db.get_all.return_value = []
        store = MagicMock()
        store.player_snapshot.return_value = {}
        code, data = _request("GET", "/api/library/browse?parent_id=favs", db=db, store=store)
        assert code == 200
        db.get_all.assert_called_once()

    def test_recent_uses_db_get_all(self):
        """DOCUMENTED GAP: recent calls db.get_all(kind='recent'), not db.get_play_history()."""
        db = MagicMock()
        db.get_all.return_value = []
        store = MagicMock()
        store.player_snapshot.return_value = {}
        code, data = _request("GET", "/api/library/browse?parent_id=recent", db=db, store=store)
        assert code == 200
        db.get_all.assert_called()


class TestLibraryItem:
    """DOCUMENTED GAP: _handle_library_item vs handle_library_item name mismatch.

    do_GET calls self._handle_library_item (with underscore) but the method
    is named handle_library_item (no underscore). This causes AttributeError.
    These tests verify the handler class and document the gap.
    """

    def test_item_endpoint_raises_attribute_error(self):
        """Accessing /api/library/item/... crashes with AttributeError (known bug)."""
        db = MagicMock()
        db.get_all.return_value = []
        store = MagicMock()
        store.player_snapshot.return_value = {}
        import pytest
        with pytest.raises(AttributeError, match="has no attribute"):
            _request("GET", "/api/library/item//tmp/track.flac", db=db, store=store)

    def test_handler_method_exists_without_underscore(self):
        """handle_library_item method exists but with wrong name."""
        from integrations.http_api.http_api import _AstraHandler
        assert hasattr(_AstraHandler, 'handle_library_item')
        # DOCUMENTED GAP: call site uses _handle_library_item


class TestHandlerClass:
    def test_handler_importable(self):
        from integrations.http_api.http_api import _AstraHandler, make_handler
        assert _AstraHandler.__name__ == "_AstraHandler"
        factory = make_handler(None, None, "t", None)
        assert callable(factory)
