"""Tests for audio format probing (format_probe.py)."""
import pytest
from audio.format_probe import probe_format, AudioFormatInfo, _default_dsd_rate, _dsd_speed_label


class TestStreamDetection:
    def test_http_stream(self):
        info = probe_format("http://stream.example.com/radio.mp3")
        assert info.is_stream is True
        assert info.container == "mp3"

    def test_https_stream(self):
        info = probe_format("https://stream.example.com/stream.aac")
        assert info.is_stream is True
        assert info.container == "aac"

    def test_rtmp_stream(self):
        info = probe_format("rtmp://stream.example.com/live")
        assert info.is_stream is True
        assert info.container == "stream"

    def test_rtsp_stream(self):
        info = probe_format("rtsp://stream.example.com/live.sdp")
        assert info.is_stream is True
        assert info.container == "sdp"


class TestFormatByExtension:
    def test_flac_lossless(self):
        info = probe_format("/music/track.flac")
        assert info.is_lossless is True
        assert info.is_pcm is True
        assert info.codec == "FLAC"
        assert info.is_dsd is False

    def test_wav_lossless(self):
        info = probe_format("/music/track.wav")
        assert info.is_lossless is True
        assert info.is_pcm is True
        assert info.codec == "WAV"

    def test_mp3_lossy(self):
        info = probe_format("/music/track.mp3")
        assert info.is_lossless is False
        assert info.is_pcm is True
        assert info.codec == "MP3"

    def test_aac_lossy(self):
        info = probe_format("/music/track.aac")
        assert info.is_lossless is False
        assert info.codec == "AAC"

    def test_ogg_lossy(self):
        info = probe_format("/music/track.ogg")
        assert info.is_lossless is False
        assert info.is_pcm is True

    def test_opus_lossy(self):
        info = probe_format("/music/track.opus")
        assert info.is_lossless is False
        assert info.is_pcm is True

    def test_wma_lossy(self):
        info = probe_format("/music/track.wma")
        assert info.is_lossless is False
        assert info.is_pcm is True

    def test_alac_lossless(self):
        info = probe_format("/music/track.alac")
        assert info.is_lossless is True
        assert info.codec == "ALAC"

    def test_aiff_lossless(self):
        info = probe_format("/music/track.aiff")
        assert info.is_lossless is True
        assert info.codec == "AIFF"

    def test_wv_lossless(self):
        info = probe_format("/music/track.wv")
        assert info.is_lossless is True

    def test_ape_lossless(self):
        info = probe_format("/music/track.ape")
        assert info.is_lossless is True

    def test_tta_lossless(self):
        info = probe_format("/music/track.tta")
        assert info.is_lossless is True

    def test_shn_lossless(self):
        info = probe_format("/music/track.shn")
        assert info.is_lossless is True

    def test_unknown_extension(self):
        info = probe_format("/music/track.xyz")
        assert info.is_pcm is True
        assert info.is_lossless is False
        assert info.codec == ""

    def test_no_extension(self):
        info = probe_format("/music/track")
        assert info.is_pcm is True
        assert info.is_lossless is False
        assert info.codec == ""

    def test_container_from_ext(self):
        info = probe_format("/music/track.FLAC")
        assert info.container == "flac"


class TestDSDDetection:
    def test_dsf_format(self):
        info = probe_format("/music/track.dsf")
        assert info.is_dsd is True
        assert info.is_dsf is True
        assert info.is_dff is False
        assert info.codec == "DSD"
        assert info.dsd_rate > 0

    def test_dff_format(self):
        info = probe_format("/music/track.dff")
        assert info.is_dsd is True
        assert info.is_dff is True
        assert info.is_dsf is False
        assert info.codec == "DSD"

    def test_dsd_speed_default(self):
        info = probe_format("/music/track.dsf")
        assert info.dsd_speed == "DSD64"

    def test_dsd_default_rate(self):
        assert _default_dsd_rate("dsf") == 2822400
        assert _default_dsd_rate("dff") == 2822400


class TestDsvSpeedLabel:
    def test_dsd64(self):
        assert _dsd_speed_label(2822400) == "DSD64"

    def test_dsd128(self):
        assert _dsd_speed_label(5644800) == "DSD128"

    def test_dsd256(self):
        assert _dsd_speed_label(11289600) == "DSD256"

    def test_above_dsd256(self):
        assert _dsd_speed_label(22579200) == "DSD256"

    def test_below_dsd64(self):
        assert _dsd_speed_label(1411200) == "DSD64"


class TestAudioFormatInfoDefaults:
    def test_default_construction(self):
        info = AudioFormatInfo()
        assert info.path_or_uri == ""
        assert info.is_stream is False
        assert info.container == ""
        assert info.codec == ""
        assert info.is_pcm is False
        assert info.is_lossless is False
        assert info.is_dsd is False
        assert info.is_dsf is False
        assert info.is_dff is False
        assert info.is_dst is False
        assert info.dsd_rate == 0
        assert info.dsd_speed == ""
        assert info.sample_rate == 0
        assert info.bit_depth == 0
        assert info.channels == 0
        assert info.bitrate == 0
        assert info.duration == 0.0
        assert info.replaygain_track_db is None
        assert info.replaygain_album_db is None
        assert info.has_gapless_tags is False
        assert info.warnings == []

    def test_path_or_uri_set(self):
        info = probe_format("/some/path.flac")
        assert info.path_or_uri == "/some/path.flac"

    def test_info_dataclass_mutable(self):
        info = AudioFormatInfo()
        info.sample_rate = 96000
        assert info.sample_rate == 96000
        info.warnings.append("test")
        assert len(info.warnings) == 1


class TestEdgeCases:
    def test_empty_string(self):
        info = probe_format("")
        assert info.is_stream is False
        assert info.container == ""

    def test_dot_file(self):
        info = probe_format("/music/.hidden")
        assert info.container == "hidden"

    def test_long_path(self):
        info = probe_format("/a/very/long/path/to/a/music/file/with-a-name.flac")
        assert info.is_lossless is True
        assert info.container == "flac"

    def test_uppercase_ext(self):
        info = probe_format("/music/track.MP3")
        assert info.codec == "MP3"
        assert info.container == "mp3"

    def test_m4a_as_lossy(self):
        info = probe_format("/music/track.m4a")
        assert info.is_lossless is False

    def test_m4b_audiobook(self):
        info = probe_format("/music/track.m4b")
        assert info.is_pcm is True
        assert info.is_lossless is False


class TestProbeWithItem:
    def test_item_provides_metadata(self):
        from unittest.mock import MagicMock
        item = MagicMock()
        item.sample_rate = 96000
        item.bit_depth = 24
        item.channels = 2
        item.bitrate = 320000
        item.duration = 300.0

        info = probe_format("/music/track.flac", item)
        assert info.sample_rate == 96000
        assert info.bit_depth == 24
        assert info.channels == 2
        assert info.bitrate == 320000
        assert info.duration == 300.0

    def test_item_missing_attrs_defaults(self):
        info = probe_format("/music/track.flac")
        assert info.sample_rate == 0
        assert info.bit_depth == 0
        assert info.channels == 0

    def test_item_with_none_values(self):
        from unittest.mock import MagicMock
        item = MagicMock()
        item.sample_rate = None
        item.bit_depth = None

        info = probe_format("/music/track.flac", item)
        assert info.sample_rate == 0
        assert info.bit_depth == 0
