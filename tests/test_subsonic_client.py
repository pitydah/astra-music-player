"""Tests for Subsonic client — HTTP API wrapper for Navidrome/Jellyfin."""
import json
from unittest.mock import MagicMock, patch

import pytest

from streaming.subsonic_client import (
    SubsonicClient,
    ServerConfig,
    SubsonicError,
    AuthError,
    ServerNotFoundError,
    RemoteArtist,
    RemoteTrack,
    load_servers,
    save_servers,
)


class TestServerConfig:
    def test_to_dict(self):
        cfg = ServerConfig(name="My Server", url="http://navidrome:4533",
                           username="user", password="pass")
        d = cfg.to_dict()
        assert d["name"] == "My Server"
        assert d["url"] == "http://navidrome:4533"
        assert d["username"] == "user"
        assert d["password"] == "pass"
        assert d["type"] == "navidrome"

    def test_from_dict(self):
        d = {"name": "S", "url": "http://s:4040", "username": "u",
             "password": "p", "type": "jellyfin"}
        cfg = ServerConfig.from_dict(d)
        assert cfg.name == "S"
        assert cfg.stype == "jellyfin"

    def test_from_dict_default_type(self):
        d = {"name": "S", "url": "http://s:4040", "username": "u", "password": "p"}
        cfg = ServerConfig.from_dict(d)
        assert cfg.stype == "navidrome"


class TestSubsonicClient:
    def make_server(self):
        return ServerConfig(name="Test", url="http://localhost:4533",
                            username="user", password="secret")

    def make_client(self, server=None):
        if server is None:
            server = self.make_server()
        return SubsonicClient(server)

    def test_ping_returns_true(self):
        client = self.make_client()
        with patch.object(client, "_get") as mock_get:
            mock_get.return_value = {}
            assert client.ping() is True
            mock_get.assert_called_once_with("ping")

    def test_ping_returns_false_on_error(self):
        client = self.make_client()
        with patch.object(client, "_get") as mock_get:
            mock_get.side_effect = SubsonicError("fail")
            assert client.ping() is False

    def test_get_artists_returns_sorted_list(self):
        client = self.make_client()
        with patch.object(client, "_get") as mock_get:
            mock_get.return_value = {
                "artists": {
                    "index": [
                        {"artist": [{"id": "2", "name": "Zebra"},
                                    {"id": "1", "name": "Alpha"}]},
                        {"artist": [{"id": "3", "name": "Beta"}]},
                    ]
                }
            }
            artists = client.get_artists()
            assert len(artists) == 3
            assert artists[0].name == "Alpha"
            assert artists[1].name == "Beta"
            assert artists[2].name == "Zebra"
            assert all(isinstance(a, RemoteArtist) for a in artists)

    def test_get_albums_by_artist(self):
        client = self.make_client()
        with patch.object(client, "_get") as mock_get:
            mock_get.return_value = {
                "artist": {
                    "name": "The Artist",
                    "album": [
                        {"id": "a1", "name": "Album One", "coverArt": "c1"},
                        {"id": "a2", "name": "Album Two"},
                    ]
                }
            }
            albums = client.get_albums(artist_id="123")
            assert len(albums) == 2
            assert albums[0].name == "Album One"
            assert albums[0].artist == "The Artist"
            assert albums[0].cover_id == "c1"
            assert albums[1].cover_id == "a2"  # falls back to id

    def test_get_albums_all(self):
        client = self.make_client()
        with patch.object(client, "_get") as mock_get:
            mock_get.return_value = {
                "albumList2": {
                    "album": [
                        {"id": "a1", "name": "A1", "artist": "Ar1"},
                    ]
                }
            }
            albums = client.get_albums()
            assert len(albums) == 1
            assert albums[0].name == "A1"

    def test_get_album_tracks_sorted(self):
        client = self.make_client()
        with patch.object(client, "_get") as mock_get:
            mock_get.return_value = {
                "album": {
                    "song": [
                        {"id": "t2", "title": "Track 2", "artist": "A",
                         "album": "Al", "duration": 200, "track": 2},
                        {"id": "t1", "title": "Track 1", "artist": "A",
                         "album": "Al", "duration": 180, "track": 1},
                    ]
                }
            }
            tracks = client.get_album_tracks("album1")
            assert len(tracks) == 2
            assert tracks[0].title == "Track 1"
            assert tracks[1].title == "Track 2"
            assert all(isinstance(t, RemoteTrack) for t in tracks)

    def test_get_cover_url(self):
        client = self.make_client()
        url = client.get_cover_url("cover123", size=300)
        assert "getCoverArt" in url
        assert "id=cover123" in url
        assert "size=300" in url

    def test_get_stream_url(self):
        client = self.make_client()
        url = client.get_stream_url("track1")
        assert "stream" in url
        assert "id=track1" in url

    def test_search_returns_artists(self):
        client = self.make_client()
        with patch.object(client, "_get") as mock_get:
            mock_get.return_value = {
                "searchResult3": {
                    "artist": [
                        {"id": "1", "name": "Found Artist"},
                    ]
                }
            }
            results = client.search("query")
            assert len(results) == 1
            assert results[0].name == "Found Artist"

    def test_search_returns_empty_on_error(self):
        client = self.make_client()
        with patch.object(client, "_get") as mock_get:
            mock_get.side_effect = SubsonicError("fail")
            results = client.search("query")
            assert results == []

    def test_cancel_raises(self):
        client = self.make_client()
        client.cancel()
        with pytest.raises(SubsonicError, match="cancelled"):
            client._get("ping")

    def test_auth_raises_on_error_code_40(self):
        client = self.make_client()
        with patch.object(client, "_get", wraps=client._get):
            # Force _get to raise AuthError via the JSON error code path
            # by mocking urlopen to return 40 status
            mock_resp = MagicMock()
            mock_resp.read.return_value = json.dumps({
                "subsonic-response": {
                    "status": "failed",
                    "error": {"code": 40, "message": "Bad auth"}
                }
            }).encode()
            mock_ctx = MagicMock()
            mock_ctx.__enter__.return_value = mock_resp
            with patch("urllib.request.urlopen", return_value=mock_ctx), pytest.raises(AuthError):
                client._get("ping")

    def test_auth_raises_on_error_code_70(self):
        client = self.make_client()
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "subsonic-response": {
                "status": "failed",
                "error": {"code": 70, "message": "Server not found"}
            }
        }).encode()
        mock_ctx = MagicMock()
        mock_ctx.__enter__.return_value = mock_resp
        with patch("urllib.request.urlopen", return_value=mock_ctx), pytest.raises(ServerNotFoundError):
            client._get("ping")

    def test_get_retries_on_recoverable(self):
        client = self.make_client()
        client._timeout = 1
        call_count = 0

        def side_effect(*a, **kw):
            nonlocal call_count
            call_count += 1
            raise SubsonicError("recoverable", recoverable=True)

        with patch.object(client, "_get", side_effect=side_effect):
            client.ping()
            # ping catches exception, returns False
            assert client.ping() is False

    @patch("urllib.request.urlopen")
    def test_get_success(self, mock_urlopen):
        client = self.make_client()
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "subsonic-response": {"status": "ok", "version": "1.16.0"}
        }).encode()
        mock_ctx = MagicMock()
        mock_ctx.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_ctx

        result = client._get("ping")
        assert result["status"] == "ok"

    @patch("urllib.request.urlopen")
    def test_get_http_401_raises_auth_error(self, mock_urlopen):
        from urllib.error import HTTPError
        client = self.make_client()
        mock_urlopen.side_effect = HTTPError(
            "http://localhost", 401, "Unauthorized", {}, None)

        with pytest.raises(AuthError):
            client._get("ping")

    @patch("urllib.request.urlopen")
    def test_get_http_500_retries_then_raises(self, mock_urlopen):
        from urllib.error import HTTPError
        client = self.make_client()
        mock_urlopen.side_effect = HTTPError(
            "http://localhost", 500, "Server Error", {}, None)

        with pytest.raises(SubsonicError, match="Server error"):
            client._get("ping")
        assert mock_urlopen.call_count == 3  # MAX_RETRIES

    @patch("urllib.request.urlopen")
    def test_get_timeout_retries(self, mock_urlopen):
        from urllib.error import URLError
        client = self.make_client()
        mock_urlopen.side_effect = URLError("timed out")

        with pytest.raises(SubsonicError, match="timed out"):
            client._get("ping")
        assert mock_urlopen.call_count == 3

    @patch("urllib.request.urlopen")
    def test_get_connection_refused_retries(self, mock_urlopen):
        from urllib.error import URLError
        client = self.make_client()
        mock_urlopen.side_effect = URLError("Connection refused")

        with pytest.raises(SubsonicError, match="refused"):
            client._get("ping")

    @patch("urllib.request.urlopen")
    def test_get_dns_error(self, mock_urlopen):
        from urllib.error import URLError
        client = self.make_client()
        mock_urlopen.side_effect = URLError(
            "[Errno -2] Name or service not known")

        with pytest.raises(ServerNotFoundError):
            client._get("ping")

    @patch("urllib.request.urlopen")
    def test_get_invalid_json_retries(self, mock_urlopen):
        client = self.make_client()
        mock_resp = MagicMock()
        mock_resp.read.return_value = b"not json"
        mock_ctx = MagicMock()
        mock_ctx.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_ctx

        with pytest.raises(SubsonicError, match="Invalid response"):
            client._get("ping")

    def test_auth_constructs_params(self):
        client = self.make_client()
        auth_str = client._auth()
        assert "u=user" in auth_str
        assert "&t=" in auth_str
        assert "&s=" in auth_str
        assert "v=1.16.0" in auth_str
        assert "c=MichiMusicPlayer" in auth_str
        assert "f=json" in auth_str

    def test_auth_salt_is_stable_within_session(self):
        client = self.make_client()
        a1 = client._auth()
        a2 = client._auth()
        # Salt should be the same (cached)
        assert a1 == a2

    def test_url_construction(self):
        client = self.make_client()
        auth = client._auth()
        expected = f"http://localhost:4533/rest/ping?{auth}"
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.read.return_value = json.dumps({
                "subsonic-response": {"status": "ok"}
            }).encode()
            mock_ctx = MagicMock()
            mock_ctx.__enter__.return_value = mock_resp
            mock_urlopen.return_value = mock_ctx
            client.ping()
            actual_url = mock_urlopen.call_args[0][0].full_url
            assert actual_url == expected


class TestServerPersistence:
    def test_load_servers_not_found(self):
        with patch("os.path.exists", return_value=False):
            servers = load_servers()
            assert servers == []

    def test_load_servers(self):
        data = json.dumps([
            {"name": "S1", "url": "http://s1", "username": "u1",
             "password": "p1", "type": "navidrome"}
        ])
        with patch("os.path.exists", return_value=True), patch("builtins.open") as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = data
            servers = load_servers()
            assert len(servers) == 1
            assert servers[0].name == "S1"

    def test_save_servers(self):
        server = ServerConfig(name="S1", url="http://s1",
                              username="u1", password="p1")
        with patch("builtins.open") as mock_open, patch("os.makedirs") as mock_mkdir:
            save_servers([server])
            mock_mkdir.assert_called_once()
            handle = mock_open.return_value.__enter__.return_value
            written = "".join(c[0][0] for c in handle.write.call_args_list)
            assert "S1" in written
            assert "http://s1" in written
