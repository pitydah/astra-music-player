"""Feature extractor — dual backend: basic (numpy/tags) or librosa (full analysis)."""

from __future__ import annotations

import hashlib
import logging
from typing import Any

from audio_analysis.schemas import AudioFeature

logger = logging.getLogger("michi.audio_analysis.extractor")


def make_track_key(filepath: str) -> str:
    return hashlib.sha256(filepath.encode()).hexdigest()[:16]


def extract_features(filepath: str, backend: str = "basic",
                     sample_duration: int = 90,
                     db: Any = None) -> AudioFeature:
    track_key = make_track_key(filepath)
    feat = AudioFeature(track_key=track_key, backend=backend, status="pending")

    if backend == "librosa":
        return _extract_librosa(filepath, feat, sample_duration)
    return _extract_basic(filepath, feat, db)


def _extract_basic(filepath: str, feat: AudioFeature,
                   db: Any = None) -> AudioFeature:
    try:
        feat.backend = "basic"
        if db and hasattr(db, "get_all"):
            items = db.get_all() or []
            for item in items:
                if getattr(item, "filepath", "") == filepath:
                    feat.duration = float(getattr(item, "duration", 0) or 0)
                    tag_bpm = int(getattr(item, "bpm", 0) or 0)
                    if tag_bpm > 0 and tag_bpm < 300:
                        feat.bpm = float(tag_bpm)
                        feat.bpm_confidence = 0.5
                    rg_track = float(getattr(item, "replaygain_track", 0) or 0)
                    rg_peak = float(getattr(item, "replaygain_track_peak", 0) or 0)
                    if rg_track < 0:
                        feat.energy = max(0.0, min(1.0, 1.0 + rg_track / 24.0))
                    elif rg_track > 0:
                        feat.energy = min(1.0, 0.5 - rg_track / 24.0)
                    else:
                        feat.energy = 0.5
                    if rg_peak > 0 and rg_track < 0:
                        feat.dynamic_range = abs(rg_peak) - abs(rg_track)
                    else:
                        feat.dynamic_range = 6.0
                    break
        feat.status = "completed"
    except Exception as e:
        logger.warning("Basic extraction failed for %s: %s", make_track_key(filepath), e)
        feat.status = "error"
        feat.error = str(e)
    return feat


def _extract_librosa(filepath: str, feat: AudioFeature,
                     sample_duration: int = 90) -> AudioFeature:
    try:
        import numpy as np
        import soundfile as sf
        import librosa

        duration = min(sample_duration, 90)
        max_frames = int(duration * 22050)  # upper bound, actual sr may differ
        try:
            y, sr = sf.read(filepath, dtype="float32", samplerate=None,
                            always_2d=False, frames=max_frames + 1)
        except Exception:
            y, sr = sf.read(filepath, dtype="float32", samplerate=None)
            y = y[:max_frames] if len(y) > max_frames else y

        if len(y.shape) > 1:
            y = np.mean(y, axis=1)
        max_samples = int(duration * sr)
        if len(y) > max_samples:
            y = y[:max_samples]

        feat.duration = float(len(y) / sr)
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr) if hasattr(librosa.beat, "beat_track") else librosa.beat.tempo(y=y, sr=sr)
        feat.bpm = round(float(tempo), 1)
        feat.bpm_confidence = 0.85

        rms = librosa.feature.rms(y=y)[0]
        feat.energy = float(np.mean(rms) * 10)
        feat.energy = max(0.0, min(1.0, feat.energy))

        peak = float(np.max(np.abs(y)))
        rms_mean = float(np.sqrt(np.mean(y ** 2)))
        if rms_mean > 0:
            feat.dynamic_range = float(20 * np.log10(peak / rms_mean))
        feat.dynamic_range = max(0.0, min(60.0, feat.dynamic_range))

        cent = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        feat.spectral_centroid = float(np.mean(cent))
        rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
        feat.spectral_rolloff = float(np.mean(rolloff))
        zcr = librosa.feature.zero_crossing_rate(y)[0]
        feat.zero_crossing_rate = float(np.mean(zcr))

        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        mfcc_mean = mfcc.mean(axis=1).tolist()
        mfcc_std = mfcc.std(axis=1).tolist()
        import json
        feat.mfcc_json = json.dumps({"mean": mfcc_mean, "std": mfcc_std})

        chroma = librosa.feature.chroma_stft(y=y, sr=sr, n_chroma=12)
        chroma_mean = chroma.mean(axis=1).tolist()
        feat.chroma_json = json.dumps({"mean": chroma_mean})

        feat.status = "completed"
    except Exception as e:
        logger.warning("Librosa extraction failed for %s: %s", make_track_key(filepath), e)
        feat.status = "error"
        feat.error = str(e)
        _extract_basic(filepath, feat)
    return feat
