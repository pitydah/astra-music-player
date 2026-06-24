"""Tests for Michi HTTP API reliability."""
import json
from unittest.mock import MagicMock, patch


class _FakeHandler:
    """Minimal handler to test helper methods without starting a server."""
    def __init__(self, bridge=None, db=None, store=None, token="test"):
        self._bridge = bridge
        self._db = db
        self._store = store
        self._token = token
        self.status_code = None
        self.response_data = None

    def _check_auth(self):
        return True

    def _send_json(self, code, data):
        self.status_code = code
        self.response_data = data

    def _send_error(self, code, error, detail=""):
        self._send_json(code, {"error": error, "detail": detail} if detail else {"error": error})

    def _safe_read_json(self):
        return self._body

    def _require_bridge(self):
        if self._bridge is None:
            self._send_error(503, "bridge_not_available")
            return False
        return True

    def _require_db(self):
        if self._db is None:
            self._send_error(503, "db_not_available")
            return False
        return True


# ── Helpers ──

def _make_handler_class():
    """Build a simple HTTP handler class from the real _MichiHandler."""
    from integrations.http_api.http_api import _MichiHandler
    return _MichiHandler


def _request(method, path, body=None, bridge=None, db=None, store=None, token="test"):
    """Simulate an HTTP request using the real handler."""
    from integrations.http_api.http_api import _MichiHandler
    import io as _io

    # Build a mock request
    h = _MichiHandler.__new__(_MichiHandler)
    h._bridge = bridge
    h._db = db
    h._store = store
    h._token = token
    h.path = path
    h.headers = {"Authorization": f"Bearer {token}", "Content-Length": "0"}
    h.status_code = None
    h.response_data = None
    h.wfile = _io.BytesIO()
    h.rfile = _io.BytesIO(b"")
    h._sent_headers = False

    def _send_json(code, data):
        h.status_code = code
        h.response_data = data
        if not h._sent_headers:
            h.send_response = lambda c: setattr(h, 'status_code', c)
            h.send_header = lambda *a: None
            h.end_headers = lambda: None
            h._sent_headers = True

    h._send_json = _send_json

    if body is not None:
        body_bytes = json.dumps(body).encode()
        h.rfile = _io.BytesIO(body_bytes)
        h.headers["Content-Length"] = str(len(body_bytes))

    if method == "GET":
        h.do_GET()
    elif method == "POST":
        h.do_POST()

    return h.status_code, h.response_data


# ── Tests ──

class TestHttpApiErrors:
    def test_post_play_no_bridge_returns_503(self):
        code, data = _request("POST", "/api/player/play", body={})
        assert code == 503
        assert data["error"] == "bridge_not_available"

    def test_post_pause_no_bridge_returns_503(self):
        code, data = _request("POST", "/api/player/pause", body={})
        assert code == 503

    def test_post_stop_no_bridge_returns_503(self):
        code, data = _request("POST", "/api/player/stop", body={})
        assert code == 503

    def test_post_volume_no_bridge_returns_503(self):
        code, data = _request("POST", "/api/player/volume", body={"volume": 50})
        assert code == 503

    def test_post_play_with_bridge_returns_202(self):
        bridge = MagicMock()
        code, data = _request("POST", "/api/player/play", body={}, bridge=bridge)
        assert code == 202
        assert data["status"] == "accepted"
        bridge.play_requested.emit.assert_called_once()

    def test_post_pause_with_bridge_returns_202(self):
        bridge = MagicMock()
        code, data = _request("POST", "/api/player/pause", body={}, bridge=bridge)
        assert code == 202
        bridge.pause_requested.emit.assert_called_once()

    def test_post_next_with_bridge_returns_202(self):
        bridge = MagicMock()
        code, data = _request("POST", "/api/player/next", body={}, bridge=bridge)
        assert code == 202
        bridge.next_requested.emit.assert_called_once()

    def test_post_previous_with_bridge_returns_202(self):
        bridge = MagicMock()
        code, data = _request("POST", "/api/player/previous", body={}, bridge=bridge)
        assert code == 202
        bridge.previous_requested.emit.assert_called_once()

    def test_post_stop_with_bridge_returns_202(self):
        bridge = MagicMock()
        code, data = _request("POST", "/api/player/stop", body={}, bridge=bridge)
        assert code == 202

    def test_post_volume_0_valid(self):
        bridge = MagicMock()
        code, data = _request("POST", "/api/player/volume", body={"volume": 0}, bridge=bridge)
        assert code == 202
        bridge.volume_requested.emit.assert_called_once_with(0)

    def test_post_volume_100_valid(self):
        bridge = MagicMock()
        code, data = _request("POST", "/api/player/volume", body={"volume": 100}, bridge=bridge)
        assert code == 202
        bridge.volume_requested.emit.assert_called_once_with(100)

    def test_post_volume_negative_invalid(self):
        bridge = MagicMock()
        code, data = _request("POST", "/api/player/volume", body={"volume": -1}, bridge=bridge)
        assert code == 400
        assert data["error"] == "invalid_volume"
        bridge.volume_requested.emit.assert_not_called()

    def test_post_volume_over_100_invalid(self):
        bridge = MagicMock()
        code, data = _request("POST", "/api/player/volume", body={"volume": 101}, bridge=bridge)
        assert code == 400
        assert bridge.volume_requested.emit.call_count == 0

    def test_post_volume_not_int_invalid(self):
        bridge = MagicMock()
        code, data = _request("POST", "/api/player/volume", body={"volume": "loud"}, bridge=bridge)
        assert code == 400
        assert data["error"] == "invalid_volume"

    def test_post_volume_missing_returns_400(self):
        bridge = MagicMock()
        code, data = _request("POST", "/api/player/volume", body={}, bridge=bridge)
        assert code == 400

    def test_post_invalid_json_returns_400(self):
        bridge = MagicMock()

        from integrations.http_api.http_api import _MichiHandler
        import io as _io
        h = _MichiHandler.__new__(_MichiHandler)
        h._bridge = bridge
        h._db = None
        h._store = None
        h._token = "test"
        h.path = "/api/player/play"
        h.headers = {"Authorization": "Bearer test", "Content-Length": "10"}
        h.status_code = None
        h.response_data = None

        def _send_json(code, data):
            h.status_code = code
            h.response_data = data
            h.send_response = lambda c: None
            h.send_header = lambda *a: None
            h.end_headers = lambda: None
        h._send_json = _send_json
        h.rfile = _io.BytesIO(b"not json!!")

        h.do_POST()
        assert h.status_code == 400
        assert h.response_data["error"] == "invalid_json"


class TestHttpApiLibraryBrowse:
    def test_browse_top_level_no_db_returns_503(self):
        code, data = _request("GET", "/api/library/browse")
        assert code == 503
        assert data["error"] == "db_not_available"

    def test_browse_top_level_requires_auth(self):
        from integrations.http_api.http_api import _MichiHandler
        import io as _io
        h = _MichiHandler.__new__(_MichiHandler)
        h._token = "test"
        h.headers = {"Authorization": "Bearer wrong", "Content-Length": "0"}
        h.status_code = None
        def _send_json(code, data):
            h.status_code = code
            h.response_data = data
            h.send_response = lambda c: None
            h.send_header = lambda *a: None
            h.end_headers = lambda: None
        h._send_json = _send_json
        h.path = "/api/library/browse"
        h.rfile = _io.BytesIO(b"")
        h.do_GET()
        assert h.status_code == 403
        assert h.response_data["error"] == "invalid_token"

    def test_browse_favs_uses_get_favorites(self):
        db = MagicMock()
        db.get_favorites.return_value = ["/tmp/a.mp3"]
        db.get_media_item_by_track_id.return_value = MagicMock(
            filepath="/tmp/a.mp3", title="A", artist="B", album="", duration=120)
        store = MagicMock()
        store.player_snapshot.return_value = {}
        code, data = _request(
            "GET", "/api/library/browse?parent_id=favs", db=db, store=store)
        assert code == 200
        db.get_favorites.assert_called_once()

    def test_browse_recent_uses_get_play_history(self):
        db = MagicMock()
        db.get_play_history.return_value = [
            {"track_id": "/tmp/a.mp3", "played_at": 1234567890.0},
        ]
        db.get_media_item_by_track_id.return_value = MagicMock(
            filepath="/tmp/a.mp3", title="A", artist="B", album="", duration=120)
        store = MagicMock()
        store.player_snapshot.return_value = {}
        code, data = _request(
            "GET", "/api/library/browse?parent_id=recent", db=db, store=store)
        assert code == 200
        db.get_play_history.assert_called_once()


class TestMichiHttpApiHost:
    def test_default_host_is_localhost(self):
        from integrations.http_api.http_api import MichiHttpApi
        api = MichiHttpApi(None)
        assert api.host == "127.0.0.1"

    def test_configure_reads_host_from_settings(self):
        from integrations.http_api.http_api import MichiHttpApi
        with patch("core.settings_manager.get", return_value="0.0.0.0"):
            api = MichiHttpApi(None)
            api.configure()
            assert api.host == "0.0.0.0"

    def test_handler_class_is_michi(self):
        from integrations.http_api.http_api import _MichiHandler, make_handler
        make_handler(None, None, "t", None)
        assert _MichiHandler.__name__ == "_MichiHandler"


class TestLibraryDbResolver:
    def test_get_media_item_by_filepath(self):
        import tempfile
        import os
        import shutil
        tmpdir = tempfile.mkdtemp()
        try:
            from library.library_db import LibraryDB
            db_path = os.path.join(tmpdir, "test.db")
            db = LibraryDB(db_path)
            db._conn.execute(
                "INSERT INTO media_items (filepath,filename,directory,ext,kind) "
                "VALUES ('/tmp/x.mp3','x.mp3','/tmp','mp3','audio')")
            db._conn.commit()
            item = db.get_media_item_by_track_id("/tmp/x.mp3")
            assert item is not None
            assert item.filepath == "/tmp/x.mp3"
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_get_media_item_not_found(self):
        import tempfile
        import os
        import shutil
        tmpdir = tempfile.mkdtemp()
        try:
            from library.library_db import LibraryDB
            db_path = os.path.join(tmpdir, "test.db")
            db = LibraryDB(db_path)
            item = db.get_media_item_by_track_id("/nonexistent.mp3")
            assert item is None
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)
