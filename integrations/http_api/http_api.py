"""Michi HTTP API — exposes player control for Home Assistant integration."""
import json
import os
import uuid
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from urllib.parse import urlparse, parse_qs


API_PORT_DEFAULT = 8124
API_HOST_DEFAULT = "127.0.0.1"


class _MichiHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Michi API. Reads from AppStateStore, writes via MichiApiBridge."""

    def __init__(self, *args, state_store=None, bridge=None, token="", db=None, **kwargs):
        self._store = state_store
        self._bridge = bridge
        self._token = token
        self._db = db
        super().__init__(*args, **kwargs)

    # ── Auth ──

    def _check_auth(self) -> bool:
        auth = self.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            self._send_error(401, "missing_token")
            return False
        if auth[7:] != self._token:
            self._send_error(403, "invalid_token")
            return False
        return True

    # ── Response helpers ──

    def _send_json(self, code: int, data: dict):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def _send_error(self, code: int, error: str, detail: str = ""):
        payload = {"error": error}
        if detail:
            payload["detail"] = detail
        self._send_json(code, payload)

    def _require_bridge(self) -> bool:
        if self._bridge is None:
            self._send_error(503, "bridge_not_available",
                             "Michi API bridge is not initialized")
            return False
        return True

    def _require_db(self) -> bool:
        if self._db is None:
            self._send_error(503, "db_not_available",
                             "Library database is not available")
            return False
        return True

    def _safe_read_json(self) -> dict | None:
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        try:
            return json.loads(self.rfile.read(length))
        except (json.JSONDecodeError, ValueError) as e:
            self._send_error(400, "invalid_json", str(e))
            return None

    # ── GET ──

    def do_GET(self):
        path = self.path.split("?")[0]
        if not self._check_auth():
            return

        if path == "/api/player/status":
            snap = self._store.player_snapshot() if self._store else {}
            data = {
                "state": snap.get("state", "idle"),
                "title": snap.get("title", ""),
                "artist": snap.get("artist", ""),
                "album": snap.get("album", ""),
                "duration": snap.get("duration", 0),
                "position": snap.get("position", 0),
                "volume": snap.get("volume", 70),
                "source_type": snap.get("source_type", "local_file"),
                "source_label": snap.get("source_label", ""),
                "destination": snap.get("destination", "local"),
                "cover_url": snap.get("cover_url", ""),
            }
            self._send_json(200, data)

        elif path == "/api/library/browse":
            self._handle_library_browse()
            return

        elif path.startswith("/api/library/item/"):
            media_id = path[len("/api/library/item/"):]
            self._handle_library_item(media_id)
            return

        else:
            self._send_error(404, "not_found")

    # ── POST ──

    def do_POST(self):
        if not self._check_auth():
            return
        body = self._safe_read_json()
        if body is None:
            return

        if self.path == "/api/player/play":
            if not self._require_bridge():
                return
            self._bridge.play_requested.emit()
            self._send_json(202, {"status": "accepted"})

        elif self.path == "/api/player/pause":
            if not self._require_bridge():
                return
            self._bridge.pause_requested.emit()
            self._send_json(202, {"status": "accepted"})

        elif self.path == "/api/player/stop":
            if not self._require_bridge():
                return
            self._bridge.stop_requested.emit()
            self._send_json(202, {"status": "accepted"})

        elif self.path == "/api/player/next":
            if not self._require_bridge():
                return
            self._bridge.next_requested.emit()
            self._send_json(202, {"status": "accepted"})

        elif self.path == "/api/player/previous":
            if not self._require_bridge():
                return
            self._bridge.previous_requested.emit()
            self._send_json(202, {"status": "accepted"})

        elif self.path == "/api/player/volume":
            if not self._require_bridge():
                return
            try:
                vol = int(body.get("volume", -1))
            except (ValueError, TypeError):
                self._send_error(400, "invalid_volume",
                                 "Volume must be an integer")
                return
            if vol < 0 or vol > 100:
                self._send_error(400, "invalid_volume",
                                 "Volume must be between 0 and 100")
                return
            self._bridge.volume_requested.emit(vol)
            self._send_json(202, {"status": "accepted", "volume": vol})

        elif self.path == "/api/player/play_media":
            if not self._require_bridge():
                return
            self._bridge.play_media_requested.emit(body)
            self._send_json(202, {"status": "accepted"})

        elif self.path == "/api/player/select_destination":
            if not self._require_bridge():
                return
            dest_id = body.get("id") or "local"
            self._bridge.select_destination_requested.emit(dest_id)
            self._send_json(202, {"status": "accepted"})

        elif self.path == "/api/library/play":
            if not self._require_bridge():
                return
            self._bridge.library_play_requested.emit(body)
            self._send_json(202, {"status": "accepted"})

        else:
            self._send_error(404, "not_found")

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")
        self.end_headers()

    # ── Library browsing ──

    def _handle_library_browse(self):
        qs = parse_qs(urlparse(self.path).query or "")
        parent_id = (qs.get("parent_id", [None])[0] or "").strip()

        if not self._require_db():
            return

        db = self._db

        if not parent_id:
            self._send_json(200, {
                "parent_id": None,
                "children": [
                    {"id": "folders", "title": "Carpetas",
                     "media_class": "directory", "can_expand": True},
                    {"id": "artists", "title": "Artistas",
                     "media_class": "directory", "can_expand": True},
                    {"id": "albums", "title": "Albumes",
                     "media_class": "directory", "can_expand": True},
                    {"id": "playlists", "title": "Playlists",
                     "media_class": "directory", "can_expand": True},
                    {"id": "favs", "title": "Favoritos",
                     "media_class": "directory", "can_expand": True},
                    {"id": "recent", "title": "Recientes",
                     "media_class": "directory", "can_expand": True},
                ],
            })
            return

        items = []

        if parent_id == "folders":
            all_items = _cached_all(db)
            dirs = sorted(set(os.path.dirname(i.filepath) for i in all_items))
            for d in dirs[:50]:
                items.append({
                    "id": f"folder:{d}", "title": os.path.basename(d) or d,
                    "media_class": "directory",
                    "can_expand": True,
                    "thumbnail": "",
                })

        elif parent_id == "artists":
            all_items = _cached_all(db)
            artists = sorted(set(i.artist for i in all_items if i.artist))
            for a in artists[:100]:
                items.append({
                    "id": f"artist:{a}", "title": a,
                    "media_class": "directory",
                    "can_expand": True,
                    "thumbnail": "",
                })

        elif parent_id == "albums":
            all_items = _cached_all(db)
            from library.album_art import group_by_album
            groups = group_by_album(all_items)
            for album, artist, _tracks in groups[:50]:
                items.append({
                    "id": f"album:{album}",
                    "title": f"{artist} — {album}" if artist else album,
                    "media_class": "album",
                    "can_expand": True,
                    "thumbnail": "",
                })

        elif parent_id == "playlists":
            for p in db.get_playlists():
                items.append({
                    "id": f"playlist:{p['id']}", "title": p.get("name", "Playlist"),
                    "media_class": "playlist",
                    "can_expand": True,
                    "thumbnail": "",
                })

        elif parent_id == "favs":
            fav_track_ids = db.get_favorites()
            items = _resolve_track_ids(db, fav_track_ids)

        elif parent_id == "recent":
            history = db.get_play_history()
            track_ids = [h["track_id"] for h in history]
            items = _resolve_track_ids(db, track_ids)

        elif parent_id.startswith("folder:"):
            folder = parent_id[len("folder:"):]
            all_items = _cached_all(db)
            tracks = [i for i in all_items if os.path.dirname(i.filepath) == folder]
            items = _tracks_to_media_items(tracks)

        elif parent_id.startswith("artist:"):
            artist_name = parent_id[len("artist:"):]
            tracks = db.search_advanced(f"artist:{artist_name}") if hasattr(db, 'search_advanced') else []
            items = _tracks_to_media_items(tracks)

        elif parent_id.startswith("album:"):
            album_name = parent_id[len("album:"):]
            all_items = _cached_all(db)
            tracks = [i for i in all_items if i.album == album_name]
            items = _tracks_to_media_items(tracks)

        elif parent_id.startswith("playlist:"):
            pid = int(parent_id[len("playlist:"):])
            tracks = db.get_playlist_items(pid)
            items = _tracks_to_media_items(tracks)

        self._send_json(200, {"parent_id": parent_id, "children": items})

    def _handle_library_item(self, media_id: str):
        if not self._require_db():
            return
        db = self._db
        item = db.get_media_item_by_track_id(media_id)
        if item is None:
            self._send_error(404, "not_found")
            return
        self._send_json(200, _track_to_item(item))

    def log_message(self, format, *args):
        pass


# ── Static helpers ──

def _cached_all(db) -> list:
    """Load and cache full library. Called from handler via db reference."""
    return db.get_all()


def _resolve_track_ids(db, track_ids: list[str]) -> list[dict]:
    """Resolve favorite/history track_ids to API media items."""
    items = []
    for tid in track_ids:
        media = db.get_media_item_by_track_id(tid)
        if media is not None:
            items.append(_track_to_item(media))
    return items


def _tracks_to_media_items(tracks) -> list[dict]:
    return [_track_to_item(t) for t in tracks]


def _track_to_item(track) -> dict:
    fp = getattr(track, 'filepath', '')
    return {
        "media_id": fp,
        "title": getattr(track, 'title', '') or os.path.basename(fp),
        "artist": getattr(track, 'artist', ''),
        "album": getattr(track, 'album', ''),
        "duration": getattr(track, 'duration', 0) or 0,
        "media_class": "track",
        "media_content_type": "music",
        "can_play": True,
        "can_expand": False,
        "thumbnail": "",
    }


# ── Handler factory ──

def make_handler(store, bridge, token, db):
    """Factory to create handler instances with state store, bridge, token, and db."""
    def _handler(*args, **kwargs):
        return _MichiHandler(*args, state_store=store, bridge=bridge, token=token, db=db, **kwargs)
    return _handler


# ── Server manager ──

class MichiHttpApi:
    """Manages the Michi HTTP API server lifecycle."""

    def __init__(self, window, port: int = API_PORT_DEFAULT):
        self._window = window
        self._port = port
        self._host = API_HOST_DEFAULT
        self._token = ""
        self._server = None
        self._thread = None
        self._running = False
        self._store = None
        self._bridge = None

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def port(self) -> int:
        return self._port

    @property
    def host(self) -> str:
        return self._host

    @property
    def token(self) -> str:
        return self._token

    def generate_token(self) -> str:
        self._token = uuid.uuid4().hex[:32]
        from core.settings_manager import set_
        set_("home_audio/michi_api_token", self._token)
        return self._token

    def configure(self, port: int = API_PORT_DEFAULT, token: str = ""):
        self._port = port
        if token:
            self._token = token
        elif not self._token:
            from core.settings_manager import get
            saved = get("home_audio/michi_api_token") or ""
            self._token = saved or self.generate_token()
        from core.settings_manager import get
        self._host = get("home_audio/michi_api_host") or API_HOST_DEFAULT

    def set_store_and_bridge(self, store, bridge):
        self._store = store
        self._bridge = bridge

    def start(self):
        if self._running or not self._store or not self._bridge:
            return
        self._server = HTTPServer(
            (self._host, self._port),
            make_handler(self._store, self._bridge, self._token,
                        getattr(self._window, '_db', None)))
        self._thread = Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()
        self._running = True

    def stop(self):
        if self._server:
            self._server.shutdown()
            self._server = None
        self._thread = None
        self._running = False
