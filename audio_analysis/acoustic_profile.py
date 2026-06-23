"""Acoustic profile — heuristic classification from audio features."""

from __future__ import annotations

from audio_analysis.schemas import AudioFeature, AcousticProfile


def classify_profile(feat: AudioFeature) -> AcousticProfile:
    profile = AcousticProfile(track_key=feat.track_key)
    labels: list[str] = []

    if feat.bpm > 0 and feat.energy > 0:
        if feat.bpm < 100 and feat.energy < 0.4:
            profile.is_calm = True
            labels.append("calm")
        if feat.bpm > 120 and feat.energy > 0.6:
            profile.is_energetic = True
            labels.append("energetic")
        if feat.spectral_centroid > 2000:
            profile.is_bright = True
            labels.append("bright")
        elif feat.spectral_centroid > 0 and feat.spectral_centroid < 800:
            profile.is_dark = True
            labels.append("dark")
        if feat.dynamic_range > 20:
            profile.is_dynamic = True
            labels.append("dynamic")

    if not labels:
        labels.append("neutral")

    profile.labels = labels
    return profile


def to_safe_labels(feat: AudioFeature) -> dict:
    profile = classify_profile(feat)
    return {
        "bpm": round(feat.bpm, 1),
        "bpm_confidence": round(feat.bpm_confidence, 2),
        "energy_bucket": _energy_bucket(feat.energy),
        "acoustic_labels": profile.labels,
        "dynamic_range_db": round(feat.dynamic_range, 1),
    }


def _energy_bucket(energy: float) -> str:
    if energy >= 0.7:
        return "high"
    if energy >= 0.4:
        return "medium"
    if energy > 0:
        return "low"
    return "unknown"
