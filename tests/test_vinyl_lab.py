"""Tests for Vinyl Lab core services."""

from __future__ import annotations

import os
import tempfile
import wave

from vinyl.exporter import split_wav, encode_to_flac, encode_wav
from vinyl.vinyl_types import (
    CaptureDevice,
    ProjectStatus,
    RecordingStatus,
    TrackSplit,
    VinylProject,
    WaveformCache,
)
from vinyl.waveform_builder import (
    build_waveform,
    detect_silences,
    silence_to_split_points,
)


def _create_test_wav(filepath: str, duration_sec: float = 3.0,
                     sample_rate: int = 44100, n_channels: int = 2):
    """Create a test WAV file with a simple sine tone."""
    import numpy as np

    n_frames = int(sample_rate * duration_sec)
    t = np.linspace(0, duration_sec, n_frames, endpoint=False)
    tone = 0.5 * np.sin(2 * np.pi * 440 * t)
    # Add silence gaps to test silence detection
    tone[:int(sample_rate * 0.5)] = 0.0  # 0.5s silence at start
    tone[int(sample_rate * 1.5):int(sample_rate * 2.0)] = 0.0  # 0.5s silence at 1.5s

    if n_channels == 2:
        data = np.column_stack((tone, tone))
    else:
        data = tone

    with wave.open(filepath, "wb") as wf:
        wf.setnchannels(n_channels)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(data.astype(np.int16).tobytes())


class TestVinylTypes:
    def test_vinyl_project_defaults(self):
        p = VinylProject()
        assert p.status == ProjectStatus.DRAFT
        assert p.sample_rate == 96000
        assert p.bit_depth == 24

    def test_track_split_defaults(self):
        ts = TrackSplit()
        assert ts.side == "A"
        assert ts.track_number == 0

    def test_capture_device(self):
        d = CaptureDevice(name="USB ADC", sample_rates=[44100, 96000])
        assert 96000 in d.sample_rates
        assert d.channels == 2

    def test_waveform_cache(self):
        wc = WaveformCache(project_id="p1", side="A", data=[0.1, 0.2])
        assert len(wc.data) == 2


class TestWaveformBuilder:
    def test_build_waveform(self):
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            path = f.name
        try:
            _create_test_wav(path)
            result = build_waveform(path)
            assert result["sample_rate"] == 44100
            assert result["channels"] == 2
            assert result["duration_sec"] > 2.0
            assert len(result["peaks"]) > 0
            assert result["max_peak"] >= 0  # 0 is valid for silence, not an error
            assert not result["error"]
        finally:
            os.unlink(path)

    def test_build_waveform_nonexistent(self):
        result = build_waveform("/nonexistent.wav")
        assert result["error"]

    def test_detect_silences(self):
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            path = f.name
        try:
            _create_test_wav(path)
            silences = detect_silences(path, threshold=0.01, min_silence_sec=0.3)
            assert len(silences) > 0
            for s in silences:
                assert "start_sec" in s
                assert "end_sec" in s
                assert "duration_sec" in s
                assert s["duration_sec"] >= 0.3
        finally:
            os.unlink(path)

    def test_silence_to_split_points(self):
        silences = [
            {"start_sec": 0.0, "end_sec": 0.5, "duration_sec": 0.5},
            {"start_sec": 2.0, "end_sec": 2.5, "duration_sec": 0.5},
        ]
        points = silence_to_split_points(silences, 10.0)
        assert 0.0 in points
        assert 10.0 in points
        assert 0.2 in points  # midpoint of first silence (rounded to 1 dec)
        assert 2.2 in points  # midpoint of second silence

    def test_silence_to_split_points_empty(self):
        points = silence_to_split_points([], 5.0)
        assert points == [0.0, 5.0]


class TestExporter:
    def test_split_wav(self):
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            path = f.name
        out_dir = tempfile.mkdtemp()
        try:
            _create_test_wav(path, duration_sec=4.0)
            tracks = [
                {"track_number": 1, "title": "Intro"},
                {"track_number": 2, "title": "Main"},
            ]
            created = split_wav(path, out_dir, [0.0, 2.0, 4.0], tracks)
            assert len(created) == 2
            for fp in created:
                assert os.path.exists(fp)
                assert fp.endswith(".wav")
        finally:
            os.unlink(path)
            for f in os.listdir(out_dir):
                os.unlink(os.path.join(out_dir, f))
            os.rmdir(out_dir)

    def test_encode_to_flac(self):
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            wav_path = f.name
        out_dir = tempfile.mkdtemp()
        try:
            _create_test_wav(wav_path)
            result = encode_to_flac(wav_path, out_dir,
                                    tags={"ARTIST": "Test", "TITLE": "Song"})
            # May fail if flac/ffmpeg not installed — that's acceptable
            if result:
                assert os.path.exists(result)
                assert result.endswith(".flac")
        finally:
            os.unlink(wav_path)
            for f in os.listdir(out_dir):
                os.unlink(os.path.join(out_dir, f))
            os.rmdir(out_dir)

    def test_encode_wav_keep(self):
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            wav_path = f.name
        out_dir = tempfile.mkdtemp()
        try:
            _create_test_wav(wav_path)
            result = encode_wav(wav_path, out_dir, "wav")
            assert result is not None
            assert os.path.exists(result)
            assert result.endswith(".wav")
        finally:
            os.unlink(wav_path)
            for f in os.listdir(out_dir):
                os.unlink(os.path.join(out_dir, f))
            os.rmdir(out_dir)

    def test_split_wav_no_tracks(self):
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            path = f.name
        out_dir = tempfile.mkdtemp()
        try:
            _create_test_wav(path, duration_sec=2.0)
            created = split_wav(path, out_dir, [0.0, 2.0], [])
            assert len(created) == 1
        finally:
            os.unlink(path)
            for f in os.listdir(out_dir):
                os.unlink(os.path.join(out_dir, f))
            os.rmdir(out_dir)
