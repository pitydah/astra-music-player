"""Tests for recognition providers — ShazamIO, AudD, AcoustID."""
import json
import sys
import types
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ── ShazamProvider ──

# Helper: install fake shazamio module in sys.modules so tests can import it
@pytest.fixture(autouse=True)
def _mock_shazamio():
    module_name = "shazamio"
    already_there = module_name in sys.modules
    if not already_there:
        mock_mod = types.ModuleType(module_name)
        mock_mod.Shamir = MagicMock()
        mock_mod.Shazam = MagicMock()
        sys.modules[module_name] = mock_mod
    yield
    if not already_there:
        sys.modules.pop(module_name, None)


class TestShazamProvider:
    def make_provider(self):
        with patch("importlib.util.find_spec", return_value=True):
            from recognition.providers.shazam import ShazamProvider
            p = ShazamProvider()
            p._available = True
            return p

    def test_name(self):
        with patch("importlib.util.find_spec", return_value=True):
            from recognition.providers.shazam import ShazamProvider
            assert ShazamProvider.name == "shazamio"

    def test_requires_api_key_false(self):
        from recognition.providers.shazam import ShazamProvider
        assert ShazamProvider.requires_api_key is False

    def test_is_configured_true_when_available(self):
        p = self.make_provider()
        assert p.is_configured() is True

    def test_is_configured_false_when_unavailable(self):
        with patch("importlib.util.find_spec", return_value=False):
            from recognition.providers.shazam import ShazamProvider
            p = ShazamProvider()
            p._available = False
            assert p.is_configured() is False

    def test_identify_returns_none_when_unavailable(self):
        with patch("importlib.util.find_spec", return_value=False):
            from recognition.providers.shazam import ShazamProvider
            p = ShazamProvider()
            p._available = False
            assert p.identify(b"data") is None

    def test_identify_success(self):
        p = self.make_provider()
        p._identify_async = AsyncMock(return_value={
            "title": "Test Song", "artist": "Test Artist",
            "album": "Test Album", "year": 2024, "genre": "Rock",
            "confidence": 0.8, "provider": "shazamio", "source": "shazam",
            "external_url": "", "artwork_url": "",
            "raw_json": {},
        })
        result = p.identify(filepath="/path/to/song.mp3")
        assert result is not None
        assert result["title"] == "Test Song"
        assert result["artist"] == "Test Artist"
        assert result["album"] == "Test Album"

    def test_identify_returns_none_on_exception(self):
        p = self.make_provider()
        p._identify_async = AsyncMock(side_effect=Exception("API error"))
        result = p.identify(filepath="/path/to/song.mp3")
        assert result is None

    def test_identify_async_no_input(self):
        p = self.make_provider()
        import asyncio
        result = asyncio.run(p._identify_async(None, None))
        assert result is None

    def test_identify_async_with_filepath(self):
        async def test():
            p = self.make_provider()
            from shazamio import Shazam
            shazam_instance = MagicMock()
            Shazam.return_value = shazam_instance
            shazam_instance.recognize = AsyncMock(return_value={
                "track": {
                    "title": "Song",
                    "subtitle": "Artist",
                    "sections": [],
                    "images": {},
                    "url": "",
                }
            })
            result = await p._identify_async(None, "/path/f.mp3")
            assert result["title"] == "Song"
            assert result["artist"] == "Artist"

        import asyncio
        asyncio.run(test())

    def test_identify_async_with_samples(self):
        async def test():
            p = self.make_provider()
            from shazamio import Shazam
            shazam_instance = MagicMock()
            Shazam.return_value = shazam_instance
            shazam_instance.recognize = AsyncMock(return_value={
                "track": {
                    "title": "Song",
                    "subtitle": "Artist",
                    "sections": [],
                    "images": {},
                    "url": "",
                }
            })
            result = await p._identify_async(b"\x00\x01\x02", None)
            assert result["title"] == "Song"

        import asyncio
        asyncio.run(test())

    def test_identify_async_extracts_metadata(self):
        async def test():
            p = self.make_provider()
            from shazamio import Shazam
            shazam_instance = MagicMock()
            Shazam.return_value = shazam_instance
            shazam_instance.recognize = AsyncMock(return_value={
                "track": {
                    "title": "S",
                    "subtitle": "A",
                    "sections": [{
                        "type": "SONG",
                        "metadata": [
                            {"title": "Album", "text": "Al"},
                            {"title": "Genre", "text": "Rock"},
                            {"title": "Released", "text": "2023"},
                        ]
                    }],
                    "images": {"coverarthq": "http://img.url/cover.jpg"},
                    "url": "http://shazam.com/track/1",
                }
            })
            result = await p._identify_async(b"data", None)
            assert result["album"] == "Al"
            assert result["genre"] == "Rock"
            assert result["year"] == 2023
            assert result["artwork_url"] == "http://img.url/cover.jpg"
            assert result["external_url"] == "http://shazam.com/track/1"

        import asyncio
        asyncio.run(test())

    def test_test_connection_when_available(self):
        p = self.make_provider()
        ok, msg = p.test_connection()
        assert ok is True
        assert "ready" in msg.lower()

    def test_test_connection_when_unavailable(self):
        from recognition.providers.shazam import ShazamProvider
        p = ShazamProvider()
        p._available = False
        ok, msg = p.test_connection()
        assert ok is False
        assert "not installed" in msg.lower()


# ── AudDProvider ──

class TestAudDProvider:
    def make_provider(self):
        from recognition.providers.audd import AudDProvider
        p = AudDProvider()
        p.api_key = "test_audd_key"
        return p

    def test_name(self):
        from recognition.providers.audd import AudDProvider
        assert AudDProvider.name == "audd"

    def test_requires_api_key_true(self):
        from recognition.providers.audd import AudDProvider
        assert AudDProvider.requires_api_key is True

    def test_is_configured_with_key(self):
        p = self.make_provider()
        assert p.is_configured() is True

    def test_is_configured_without_key(self):
        from recognition.providers.audd import AudDProvider
        p = AudDProvider()
        p.api_key = ""
        assert p.is_configured() is False

    def test_identify_returns_none_without_key(self):
        from recognition.providers.audd import AudDProvider
        p = AudDProvider()
        p.api_key = ""
        assert p.identify(b"data") is None

    def test_identify_returns_none_without_input(self):
        p = self.make_provider()
        assert p.identify() is None

    @patch("urllib.request.urlopen")
    def test_identify_success_with_bytes(self, mock_urlopen):
        p = self.make_provider()
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "status": "success",
            "result": {
                "title": "Test Song",
                "artist": "Test Artist",
                "album": "Test Album",
                "song_link": "http://audd.io/song/1",
                "isrc": "USABC1234567",
            }
        }).encode()
        mock_ctx = MagicMock()
        mock_ctx.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_ctx

        result = p.identify(sample_bytes=b"\x00\x01\x02")
        assert result is not None
        assert result["title"] == "Test Song"
        assert result["artist"] == "Test Artist"
        assert result["album"] == "Test Album"
        assert result["isrc"] == "USABC1234567"
        assert result["external_url"] == "http://audd.io/song/1"
        assert result["confidence"] == 0.9

    @patch("urllib.request.urlopen")
    def test_identify_with_filepath(self, mock_urlopen):
        p = self.make_provider()
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "status": "success",
            "result": {"title": "T", "artist": "A", "album": "Al"}
        }).encode()
        mock_ctx = MagicMock()
        mock_ctx.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_ctx

        with patch("os.path.getsize", return_value=1000), patch("builtins.open") as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = b"fake_data"
            result = p.identify(filepath="/path/to/song.mp3")
            assert result is not None
            assert result["title"] == "T"

    def test_identify_file_too_large(self):
        p = self.make_provider()
        with patch("os.path.getsize", return_value=20 * 1024 * 1024):
            result = p.identify(filepath="/path/to/big.mp3")
            assert result is None

    @patch("urllib.request.urlopen")
    def test_identify_returns_none_when_status_not_success(self, mock_urlopen):
        p = self.make_provider()
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "status": "error",
            "result": None,
        }).encode()
        mock_ctx = MagicMock()
        mock_ctx.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_ctx

        result = p.identify(sample_bytes=b"data")
        assert result is None

    @patch("urllib.request.urlopen")
    def test_identify_returns_none_when_no_result(self, mock_urlopen):
        p = self.make_provider()
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "status": "success",
            "result": None,
        }).encode()
        mock_ctx = MagicMock()
        mock_ctx.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_ctx

        result = p.identify(sample_bytes=b"data")
        assert result is None

    @patch("urllib.request.urlopen")
    def test_identify_handles_http_error(self, mock_urlopen):
        from urllib.error import HTTPError
        p = self.make_provider()
        mock_urlopen.side_effect = HTTPError(
            "http://api.audd.io", 500, "Error", {}, None)

        result = p.identify(sample_bytes=b"data")
        assert result is None

    @patch("urllib.request.urlopen")
    def test_identify_handles_timeout(self, mock_urlopen):
        p = self.make_provider()
        mock_urlopen.side_effect = Exception("timed out")

        result = p.identify(sample_bytes=b"data")
        assert result is None

    def test_test_connection_with_key(self):
        p = self.make_provider()
        ok, msg = p.test_connection()
        assert ok is True
        assert "configured" in msg.lower()

    def test_test_connection_without_key(self):
        from recognition.providers.audd import AudDProvider
        p = AudDProvider()
        p.api_key = ""
        ok, msg = p.test_connection()
        assert ok is False
        assert "no api key" in msg.lower()


# ── AcoustIDProvider ──

class TestAcoustIDProvider:
    def make_provider(self, fpcalc_path="/usr/bin/fpcalc"):
        with patch("recognition.providers.acoustid.AcoustIDProvider._find_fpcalc",
                   return_value=fpcalc_path):
            from recognition.providers.acoustid import AcoustIDProvider
            p = AcoustIDProvider()
            p._fpcalc_path = fpcalc_path
            p._client_key = "test_key"
            return p

    def test_name(self):
        from recognition.providers.acoustid import AcoustIDProvider
        assert AcoustIDProvider.name == "acoustid"

    def test_requires_api_key_false(self):
        from recognition.providers.acoustid import AcoustIDProvider
        assert AcoustIDProvider.requires_api_key is False

    def test_is_configured_with_fpcalc(self):
        p = self.make_provider()
        assert p.is_configured() is True

    def test_is_configured_without_fpcalc(self):
        p = self.make_provider(fpcalc_path=None)
        assert p.is_configured() is False

    def test_identify_returns_none_without_fpcalc(self):
        p = self.make_provider(fpcalc_path=None)
        result = p.identify(filepath="/path/to/song.mp3")
        assert result is None

    def test_identify_returns_none_without_input(self):
        p = self.make_provider()
        result = p.identify()
        assert result is None

    @patch("urllib.request.urlopen")
    def test_identify_success(self, mock_urlopen):
        p = self.make_provider()
        p._fingerprint = MagicMock(return_value=("fp123", 180.0))

        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "status": "ok",
            "results": [{
                "score": 0.85,
                "id": "acoustid-1",
                "recordings": [{
                    "title": "Test Song",
                    "artists": [{"name": "Test Artist"}],
                    "releasegroups": [{"title": "Test Album"}],
                }]
            }]
        }).encode()
        mock_ctx = MagicMock()
        mock_ctx.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_ctx

        result = p.identify(filepath="/path/to/song.mp3")
        assert result is not None
        assert result["title"] == "Test Song"
        assert result["artist"] == "Test Artist"
        assert result["album"] == "Test Album"
        assert result["confidence"] == 0.85
        assert result["external_url"] == "https://acoustid.org/track/acoustid-1"

    @patch("urllib.request.urlopen")
    def test_identify_returns_none_when_score_too_low(self, mock_urlopen):
        p = self.make_provider()
        p._fingerprint = MagicMock(return_value=("fp123", 180.0))

        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "status": "ok",
            "results": [{
                "score": 0.5,
                "id": "acoustid-1",
                "recordings": [{"title": "T", "artists": [{"name": "A"}]}]
            }]
        }).encode()
        mock_ctx = MagicMock()
        mock_ctx.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_ctx

        result = p.identify(filepath="/path/to/song.mp3")
        assert result is None

    @patch("urllib.request.urlopen")
    def test_identify_returns_none_when_no_recordings(self, mock_urlopen):
        p = self.make_provider()
        p._fingerprint = MagicMock(return_value=("fp123", 180.0))

        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "status": "ok",
            "results": [{"score": 0.8, "recordings": []}]
        }).encode()
        mock_ctx = MagicMock()
        mock_ctx.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_ctx

        result = p.identify(filepath="/path/to/song.mp3")
        assert result is None

    @patch("urllib.request.urlopen")
    def test_identify_returns_none_on_api_error(self, mock_urlopen):
        p = self.make_provider()
        p._fingerprint = MagicMock(return_value=("fp123", 180.0))

        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "status": "error",
            "error": {"message": "Invalid key"}
        }).encode()
        mock_ctx = MagicMock()
        mock_ctx.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_ctx

        result = p.identify(filepath="/path/to/song.mp3")
        assert result is None

    @patch("urllib.request.urlopen")
    def test_identify_handles_http_error(self, mock_urlopen):
        from urllib.error import HTTPError
        p = self.make_provider()
        p._fingerprint = MagicMock(return_value=("fp123", 180.0))
        mock_urlopen.side_effect = HTTPError(
            "http://api.acoustid.org", 500, "Error", {}, None)

        result = p.identify(filepath="/path/to/song.mp3")
        assert result is None

    def test_identify_with_sample_bytes_creates_temp_file(self):
        p = self.make_provider()
        p._fingerprint = MagicMock(return_value=("fp456", 90.0))

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.read.return_value = json.dumps({
                "status": "ok",
                "results": [{
                    "score": 0.9,
                    "id": "aid-1",
                    "recordings": [{"title": "T", "artists": [{"name": "A"}],
                                    "releasegroups": [{"title": "Al"}]}]
                }]
            }).encode()
            mock_ctx = MagicMock()
            mock_ctx.__enter__.return_value = mock_resp
            mock_urlopen.return_value = mock_ctx

            with patch("tempfile.NamedTemporaryFile") as mock_tmp:
                mock_tmp.return_value.__enter__.return_value.name = "/tmp/tmp.wav"
                result = p.identify(sample_bytes=b"\x00\x01\x02")
                assert result is not None
                assert result["title"] == "T"

    def test_identify_cleans_up_temp_file(self):
        p = self.make_provider()
        p._fingerprint = MagicMock(return_value=("fp", 90.0))

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.read.return_value = json.dumps({
                "status": "ok",
                "results": [{
                    "score": 0.9,
                    "id": "aid-1",
                    "recordings": [{"title": "T", "artists": [{"name": "A"}],
                                    "releasegroups": [{"title": "Al"}]}]
                }]
            }).encode()
            mock_ctx = MagicMock()
            mock_ctx.__enter__.return_value = mock_resp
            mock_urlopen.return_value = mock_ctx

            with patch("tempfile.NamedTemporaryFile") as mock_tmp:
                mock_tmp.return_value.__enter__.return_value.name = "/tmp/tmp.wav"
                with patch("os.unlink") as mock_unlink:
                    p.identify(sample_bytes=b"\x00\x01\x02")
                    mock_unlink.assert_called_once_with("/tmp/tmp.wav")

    def test_configure_updates_client_key(self):
        p = self.make_provider()
        assert p._client_key == "test_key"
        p.configure("new_key_123")
        assert p._client_key == "new_key_123"

    def test_fingerprint_runs_fpcalc(self):
        p = self.make_provider()
        with patch("subprocess.run") as mock_run:
            mock_proc = MagicMock()
            mock_proc.returncode = 0
            mock_proc.stdout = json.dumps({
                "fingerprint": "fp_test",
                "duration": 123.5
            })
            mock_run.return_value = mock_proc

            fp, dur = p._fingerprint("/path/to/song.mp3")
            assert fp == "fp_test"
            assert dur == 123.5
            mock_run.assert_called_once_with(
                ["/usr/bin/fpcalc", "-json", "/path/to/song.mp3"],
                capture_output=True, text=True, timeout=30)

    def test_fingerprint_returns_none_on_error(self):
        p = self.make_provider()
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = Exception("fpcalc not found")
            fp, dur = p._fingerprint("/path/to/song.mp3")
            assert fp is None
            assert dur == 0.0

    def test_fingerprint_returns_none_on_nonzero_return(self):
        p = self.make_provider()
        with patch("subprocess.run") as mock_run:
            mock_proc = MagicMock()
            mock_proc.returncode = 1
            mock_proc.stderr = "error"
            mock_run.return_value = mock_proc
            fp, dur = p._fingerprint("/path/to/song.mp3")
            assert fp is None
            assert dur == 0.0

    def test_find_fpcalc_returns_none_when_not_found(self):
        with patch("shutil.which", return_value=None), patch("os.path.isfile", return_value=False):
            from recognition.providers.acoustid import AcoustIDProvider
            path = AcoustIDProvider._find_fpcalc()
            assert path is None

    def test_find_fpcalc_returns_path_when_found(self):
        with patch("shutil.which", return_value="/usr/bin/fpcalc"):
            from recognition.providers.acoustid import AcoustIDProvider
            path = AcoustIDProvider._find_fpcalc()
            assert path == "/usr/bin/fpcalc"

    def test_test_connection_with_fpcalc(self):
        p = self.make_provider()
        ok, msg = p.test_connection()
        assert ok is True
        assert "fpcalc ready" in msg

    def test_test_connection_without_fpcalc(self):
        p = self.make_provider(fpcalc_path=None)
        ok, msg = p.test_connection()
        assert ok is False
        assert "fpcalc not found" in msg
