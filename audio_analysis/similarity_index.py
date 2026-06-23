"""Similarity index — computes acoustic distance between audio features."""

from __future__ import annotations

from audio_analysis.schemas import AudioFeature, SimilarityResult


def compute_similarity(seed: AudioFeature, candidate: AudioFeature) -> SimilarityResult:
    bpm_diff = _bpm_similarity(seed.bpm, candidate.bpm)
    energy_diff = _value_similarity(seed.energy, candidate.energy)
    centroid_diff = _value_similarity(seed.spectral_centroid, candidate.spectral_centroid, scale=4000.0)
    rolloff_diff = _value_similarity(seed.spectral_rolloff, candidate.spectral_rolloff, scale=4000.0)
    zcr_diff = _value_similarity(seed.zero_crossing_rate, candidate.zero_crossing_rate, scale=0.3)
    timbre_diff = (rolloff_diff + zcr_diff) / 2.0 if rolloff_diff + zcr_diff > 0 else bpm_diff

    if seed.backend == "basic" or not seed.spectral_centroid:
        score = bpm_diff * 0.5 + energy_diff * 0.3 + _value_similarity(seed.dynamic_range, candidate.dynamic_range, scale=30.0) * 0.2
    else:
        score = (
            bpm_diff * 0.25
            + energy_diff * 0.20
            + timbre_diff * 0.30
            + centroid_diff * 0.15
            + _value_similarity(seed.dynamic_range, candidate.dynamic_range, scale=30.0) * 0.10
        )

    reasons = []
    if bpm_diff >= 0.85:
        reasons.append(f"BPM cercano: {seed.bpm:.0f} vs {candidate.bpm:.0f}")
    if energy_diff >= 0.75:
        reasons.append("Energia similar")
    if centroid_diff >= 0.8:
        reasons.append("Timbre parecido")
    if _value_similarity(seed.dynamic_range, candidate.dynamic_range, scale=30.0) >= 0.7:
        reasons.append("Dinamica parecida")

    return SimilarityResult(
        track_key=candidate.track_key,
        score=round(score, 4),
        bpm_diff=round(bpm_diff, 4),
        energy_diff=round(energy_diff, 4),
        timbre_diff=round(timbre_diff, 4),
        centroid_diff=round(centroid_diff, 4),
        reasons=reasons,
    )


def _bpm_similarity(bpm_a: float, bpm_b: float) -> float:
    if bpm_a <= 0 or bpm_b <= 0:
        return 0.5
    diff = abs(bpm_a - bpm_b)
    return max(0.0, 1.0 - min(diff / 60.0, 1.0))


def _value_similarity(a: float, b: float, scale: float = 1.0) -> float:
    if scale <= 0:
        return 1.0
    diff = abs(a - b) / scale
    return max(0.0, 1.0 - min(diff, 1.0))
