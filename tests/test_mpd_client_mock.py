"""Tests for MpdClient with mocked sockets."""

import pytest
from unittest.mock import MagicMock, patch


class TestMpdClientMock:
    def test_greeting_parsed_correctly(self):
        from audio.mpd.mpd_client import MpdClient
        client = MpdClient()
        with patch.object(client, '_read_line', return_value="OK MPD 0.23.12\n"):
            version = client._read_greeting()
            assert version == "0.23.12"

    def test_greeting_invalid_raises(self):
        from audio.mpd.mpd_client import MpdClient
        from audio.mpd.mpd_errors import MpdProtocolError
        client = MpdClient()
        with patch.object(client, '_read_line', return_value="INVALID\n"):
            with pytest.raises(MpdProtocolError, match="Invalid MPD greeting"):
                client._read_greeting()

    def test_greeting_empty_raises(self):
        from audio.mpd.mpd_client import MpdClient
        from audio.mpd.mpd_errors import MpdProtocolError
        client = MpdClient()
        with patch.object(client, '_read_line', return_value=None):
            with pytest.raises(MpdProtocolError, match="Empty MPD greeting"):
                client._read_greeting()

    def test_connect_sends_password_after_greeting(self):
        from audio.mpd.mpd_client import MpdClient
        with patch("audio.mpd.mpd_client.socket.create_connection") as mock_conn:
            mock_sock = MagicMock()
            greeting_bytes = [bytes([b]) for b in b"OK MPD 0.23.12\n"]
            ok_bytes = [bytes([b]) for b in b"OK\n"]
            mock_sock.recv.side_effect = greeting_bytes + ok_bytes
            mock_conn.return_value = mock_sock
            client = MpdClient(password="secret", timeout=2.0)
            client.connect()
            calls = [c[0][0] for c in mock_sock.sendall.call_args_list]
            assert any(b"password" in c for c in calls)

    def test_connect_connection_refused_raises(self):
        from audio.mpd.mpd_client import MpdClient
        from audio.mpd.mpd_errors import MpdConnectionError
        with patch("audio.mpd.mpd_client.socket.create_connection") as mock_conn:
            mock_conn.side_effect = ConnectionRefusedError()
            client = MpdClient()
            with pytest.raises(MpdConnectionError):
                client.connect()

    def test_ping_returns_true(self):
        from audio.mpd.mpd_client import MpdClient
        client = MpdClient()
        client._sock = MagicMock()
        client._connected = True
        client._sock.recv.side_effect = [b"O", b"K", b"\n"]
        assert client.ping() is True

    def test_ping_returns_false_on_error(self):
        from audio.mpd.mpd_client import MpdClient
        client = MpdClient()
        client._sock = MagicMock()
        client._connected = True
        client._sock.sendall.side_effect = OSError("broken")
        assert client.ping() is False

    def test_ensure_connected_when_not_connected(self):
        from audio.mpd.mpd_client import MpdClient
        with patch("audio.mpd.mpd_client.socket.create_connection") as mock_conn:
            mock_sock = MagicMock()
            mock_sock.recv.side_effect = [b"O", b"K", b" ", b"M", b"P", b"D", b" ", b"x", b"\n"]
            mock_conn.return_value = mock_sock
            client = MpdClient()
            client.ensure_connected()
            assert client.connected is True

    def test_ensure_connected_when_already_connected(self):
        from audio.mpd.mpd_client import MpdClient
        client = MpdClient()
        client._connected = True
        client.ensure_connected()
        assert client.connected is True
