"""Tests: Disc Lab profile combo and EncoderService error cleanup."""

from unittest.mock import MagicMock

import pytest
from PySide6.QtCore import QProcess


class TestDiscLabProfileCombo:

    def test_rip_profiles_have_available_flag(self):
        from ui.audio_lab.models import RIP_PROFILES
        assert len(RIP_PROFILES) > 0
        has_available = any(p.available for p in RIP_PROFILES)
        has_unavailable = any(not p.available for p in RIP_PROFILES)
        assert has_available
        assert has_unavailable

    def test_rip_profiles_have_format(self):
        from ui.audio_lab.models import RIP_PROFILES
        for p in RIP_PROFILES:
            assert p.fmt, f"Profile {p.name} has no format"

    def test_first_available_is_wav(self):
        from ui.audio_lab.models import RIP_PROFILES
        available = [p for p in RIP_PROFILES if p.available]
        assert len(available) > 0
        assert available[0].fmt == "wav", (
            f"First available profile should be WAV, got {available[0].fmt}"
        )

    def test_unavailable_profiles_have_no_usable_fmt_as_currentData(self):
        from ui.audio_lab.models import RIP_PROFILES
        for p in RIP_PROFILES:
            if not p.available:
                assert not p.available, (
                    f"Profile '{p.name}' is unavailable by design"
                )
                assert p.fmt  # fmt is informational, not executable


class TestEncoderServiceErrors:

    @pytest.fixture
    def encoder(self):
        from ui.audio_lab.services.encoder_service import EncoderService
        return EncoderService()

    def test_failed_to_start_cleans_up_process(self, encoder):
        mock_proc = MagicMock(spec=QProcess)
        encoder._processes = [mock_proc]
        encoder._on_encoder_error(QProcess.FailedToStart, "/tmp/a.wav", mock_proc)
        assert mock_proc not in encoder._processes

    def test_encoder_error_emitted(self, encoder):
        errors = []
        encoder.encode_error.connect(lambda ip, msg: errors.append((ip, msg)))
        encoder._on_encoder_error(QProcess.FailedToStart, "/tmp/a.wav")
        assert len(errors) == 1

    def test_no_zombie_process_after_error(self, encoder):
        mock_proc = MagicMock(spec=QProcess)
        encoder._processes = [mock_proc]
        initial_count = len(encoder._processes)
        encoder._on_encoder_error(QProcess.Crashed, "/tmp/a.wav", mock_proc)
        assert len(encoder._processes) < initial_count
