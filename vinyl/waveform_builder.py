"""Waveform builder — generates peak data from WAV files for waveform display.

Reads PCM samples from a WAV file and computes per-second peak values
for waveform rendering in the UI.
"""

from __future__ import annotations

import logging
import wave
from typing import Any

logger = logging.getLogger("michi.vinyl.waveform")


def build_waveform(filepath: str,
                   samples_per_second: int = 100) -> dict[str, Any]:
    """Build waveform peak data from a WAV file.

    Args:
        filepath: Path to WAV file.
        samples_per_second: Number of peak samples per second of audio.
            Higher values give more detail.

    Returns:
        dict with keys: peaks (list[float]), duration_sec (float),
        sample_rate (int), channels (int), bits_per_sample (int),
        max_peak (float), error (str if failed).
    """
    result: dict[str, Any] = {
        "peaks": [],
        "duration_sec": 0.0,
        "sample_rate": 0,
        "channels": 0,
        "bits_per_sample": 0,
        "max_peak": 0.0,
        "error": "",
    }

    try:
        with wave.open(filepath, "rb") as wf:
            frames = wf.getnframes()
            sr = wf.getframerate()
            sampwidth = wf.getsampwidth()
            n_channels = wf.getnchannels()

            result["sample_rate"] = sr
            result["channels"] = n_channels
            result["bits_per_sample"] = sampwidth * 8

            if frames == 0 or sr == 0:
                return result

            duration = frames / sr
            result["duration_sec"] = duration

            chunk_size = max(1, frames // max(1, int(duration * samples_per_second)))
            raw = wf.readframes(frames)
            if not raw:
                return result

            import numpy as np

            if sampwidth == 1:
                dtype = np.uint8
            elif sampwidth == 2:
                dtype = np.int16
            elif sampwidth == 3:
                raw_bytes = np.frombuffer(raw, dtype=np.uint8)
                raw_bytes = raw_bytes.reshape(-1, 3)
                padded = np.zeros((len(raw_bytes), 4), dtype=np.uint8)
                padded[:, :3] = raw_bytes
                samples = padded.view(np.int32).flatten()
                if n_channels > 1:
                    samples = samples.reshape(-1, n_channels)
                    samples = samples[:, 0]
                samples = samples.astype(np.float64)
                max_val = 2**31
                return _build_peaks_from_samples(
                    samples, max_val, chunk_size, result
                )
            elif sampwidth == 4:
                dtype = np.int32
            else:
                result["error"] = f"Unsupported sample width: {sampwidth}"
                return result

            samples = np.frombuffer(raw, dtype=dtype).astype(np.float64)
            if n_channels > 1:
                samples = samples.reshape(-1, n_channels)
                samples = samples[:, 0]

            max_val = 2 ** (sampwidth * 8 - 1)
            return _build_peaks_from_samples(
                samples, max_val, chunk_size, result
            )

    except Exception as e:
        logger.exception("Waveform build failed for %s", filepath)
        result["error"] = str(e)

    return result


def _build_peaks_from_samples(samples, max_val, chunk_size, result):
    import numpy as np

    n_chunks = max(1, len(samples) // chunk_size)
    peaks = np.zeros(n_chunks, dtype=np.float64)

    for i in range(n_chunks):
        start = i * chunk_size
        end = min(start + chunk_size, len(samples))
        chunk = samples[start:end]
        if len(chunk) > 0:
            peaks[i] = np.max(np.abs(chunk)) / max_val

    result["peaks"] = peaks.tolist()
    result["max_peak"] = float(np.max(peaks)) if len(peaks) > 0 else 0.0
    return result


def detect_silences(filepath: str,
                    threshold: float = 0.02,
                    min_silence_sec: float = 2.0) -> list[dict]:
    """Detect silence regions in a WAV file for track splitting.

    Args:
        filepath: Path to WAV file.
        threshold: RMS threshold below which audio is considered silence (0..1).
        min_silence_sec: Minimum silence duration to register a split point.

    Returns:
        list of dicts: {start_sec, end_sec, duration_sec}
    """
    results = []
    try:
        with wave.open(filepath, "rb") as wf:
            frames = wf.getnframes()
            sr = wf.getframerate()
            sampwidth = wf.getsampwidth()
            n_channels = wf.getnchannels()

            if frames == 0 or sr == 0:
                return results

            raw = wf.readframes(frames)
            import numpy as np

            dtype = np.int16 if sampwidth == 2 else np.int32
            samples = np.frombuffer(raw, dtype=dtype).astype(np.float64)
            if n_channels > 1:
                samples = samples.reshape(-1, n_channels)
                samples = np.mean(samples, axis=1)

            max_val = 2 ** (sampwidth * 8 - 1)
            samples = samples / max_val

            frame_step = int(sr * 0.1)
            is_silent = np.array([
                np.sqrt(np.mean(samples[i:i + frame_step] ** 2)) < threshold
                for i in range(0, len(samples), frame_step)
            ])

            in_silence = False
            silence_start = 0.0
            for i, silent in enumerate(is_silent):
                t = i * 0.1
                if silent and not in_silence:
                    in_silence = True
                    silence_start = t
                elif not silent and in_silence:
                    dur = t - silence_start
                    if dur >= min_silence_sec:
                        results.append({
                            "start_sec": round(silence_start, 1),
                            "end_sec": round(t, 1),
                            "duration_sec": round(dur, 1),
                        })
                    in_silence = False

            if in_silence:
                dur = (len(is_silent) * 0.1) - silence_start
                if dur >= min_silence_sec:
                    results.append({
                        "start_sec": round(silence_start, 1),
                        "end_sec": round(len(is_silent) * 0.1, 1),
                        "duration_sec": round(dur, 1),
                    })

    except Exception:
        logger.exception("Silence detection failed for %s", filepath)

    return results


def silence_to_split_points(silences: list[dict],
                            total_duration: float) -> list[float]:
    """Convert silence regions to track split points in seconds.

    Takes the mid-point of each silence region as the split point.
    Adds 0.0 and total_duration as boundaries.
    """
    points = [0.0]
    for s in silences:
        mid = (s["start_sec"] + s["end_sec"]) / 2
        points.append(round(mid, 1))
    if total_duration > 0:
        points.append(total_duration)
    return sorted(set(points))
