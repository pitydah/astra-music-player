"""Tests for spectral cache persistence."""

import os
import tempfile
import wave
import contextlib
import numpy as np


def _create_test_wav(path, sr=44100, bd_bytes=2, channels=1, duration_secs=1.0):
    n_frames = int(sr * duration_secs)
    t = np.linspace(0, duration_secs, n_frames, endpoint=False)
    if bd_bytes == 2:
        data = (0.3 * np.sin(2 * np.pi * 440 * t) * 32767).astype(np.int16)
    elif bd_bytes == 3:
        raw = np.int32(0.3 * 8388608 * np.sin(2 * np.pi * 440 * t))
        data = np.zeros(n_frames * 3, dtype=np.uint8)
        for i in range(n_frames):
            v = int(raw[i]) & 0xFFFFFF
            data[i * 3] = v & 0xFF
            data[i * 3 + 1] = (v >> 8) & 0xFF
            data[i * 3 + 2] = (v >> 16) & 0xFF
        data = data.tobytes()
    else:
        data = (0.3 * np.sin(2 * np.pi * 440 * t) * 127).astype(np.int8).tobytes()
    with wave.open(path, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(bd_bytes)
        wf.setframerate(sr)
        wf.writeframes(data if isinstance(data, bytes) else data.tobytes())


class TestSpectralCache:
    def test_attach_spectral_persists_to_cache(self):
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            path = f.name
        try:
            _create_test_wav(path)
            from core.audio_lab.diagnostics_service import (
                DiagnosticsCache, analyse_file, attach_spectral_analysis,
                close_global_cache, reset_global_cache_for_tests,
            )
            cache_path = os.path.join(tempfile.gettempdir(), "test_spec_cache.db")
            try:
                reset_global_cache_for_tests(cache_path)
                result = analyse_file(path, use_cache=False)
                result = attach_spectral_analysis(result, path, persist=True)
                close_global_cache()
                cache2 = DiagnosticsCache(cache_path)
                cached = cache2.get(path)
                cache2.close()
                assert cached is not None
                spec = cached.get("spectral", {})
                assert isinstance(spec, dict)
                assert spec.get("verdict", "") != ""
                assert isinstance(spec.get("confidence", 0), (int, float))
                assert isinstance(spec.get("metrics", {}), dict)
            finally:
                close_global_cache()
                with contextlib.suppress(Exception):
                    os.unlink(cache_path)
        finally:
            os.unlink(path)

    def test_analyse_directory_persists_spectral(self):
        with tempfile.TemporaryDirectory() as tmp:
            p1 = os.path.join(tmp, "a.wav")
            p2 = os.path.join(tmp, "b.wav")
            _create_test_wav(p1)
            _create_test_wav(p2)
            from core.audio_lab.diagnostics_service import analyse_directory, close_global_cache
            close_global_cache()
            results = analyse_directory(tmp, include_spectral=True)
            assert len(results) == 2
            for r in results:
                spec = r.get("spectral", {})
                assert isinstance(spec, dict), f"Missing spectral in {r.get('filepath')}"
