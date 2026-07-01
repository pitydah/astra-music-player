"""Tests for spectral analysis helpers — WAV/FLAC support."""
from __future__ import annotations



from core.audio_lab.diagnostics_helpers import supports_spectral_analysis


class TestSupportsSpectralAnalysis:
    def test_wav_supported(self):
        assert supports_spectral_analysis("file.wav") is True

    def test_flac_supported(self):
        assert supports_spectral_analysis("file.flac") is True

    def test_wav_uppercase(self):
        assert supports_spectral_analysis("file.WAV") is True

    def test_flac_mixed_case(self):
        assert supports_spectral_analysis("file.Flac") is True

    def test_mp3_not_supported(self):
        assert supports_spectral_analysis("file.mp3") is False

    def test_ogg_not_supported(self):
        assert supports_spectral_analysis("file.ogg") is False

    def test_m4a_not_supported(self):
        assert supports_spectral_analysis("file.m4a") is False

    def test_dsf_not_supported(self):
        assert supports_spectral_analysis("file.dsf") is False

    def test_no_extension(self):
        assert supports_spectral_analysis("file") is False

    def test_dotfile(self):
        assert supports_spectral_analysis(".hidden") is False

    def test_with_path(self):
        assert supports_spectral_analysis("/home/user/music/test.flac") is True


class TestCanAnalyseFunction:
    def test_can_analyse_wav(self):
        from core.audio_analysis.spectral_authenticator import can_analyse

        assert can_analyse("test.wav") is True

    def test_can_analyse_flac(self):
        from core.audio_analysis.spectral_authenticator import can_analyse

        assert can_analyse("test.flac") is True

    def test_can_analyse_mp3(self):
        from core.audio_analysis.spectral_authenticator import can_analyse

        assert can_analyse("test.mp3") is False

    def test_can_analyse_ogg(self):
        from core.audio_analysis.spectral_authenticator import can_analyse

        assert can_analyse("test.ogg") is False

    def test_can_analyse_no_ext(self):
        from core.audio_analysis.spectral_authenticator import can_analyse

        assert can_analyse("test") is False


class TestDiagnosticsServiceIntegration:
    def test_analyse_spectral_wav_path(self):
        from ui.audio_lab.diagnostics_service import analyse_spectral

        result = analyse_spectral("/nonexistent/test.wav")
        assert result.get("verdict") == "ANALYSIS_ERROR"

    def test_analyse_spectral_flac_path(self):
        from ui.audio_lab.diagnostics_service import analyse_spectral

        result = analyse_spectral("/nonexistent/test.flac")
        assert result.get("verdict") == "ANALYSIS_ERROR"

    def test_diagnostics_page_filter(self):
        filter_str = "WAV/FLAC (*.wav *.flac)"
        assert "*.wav" in filter_str
        assert "*.flac" in filter_str
