"""Schemas for experimental audio analysis."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class AudioFeature:
    track_key: str = ""
    duration: float = 0.0
    bpm: float = 0.0
    bpm_confidence: float = 0.0
    energy: float = 0.0
    dynamic_range: float = 0.0
    spectral_centroid: float = 0.0
    spectral_rolloff: float = 0.0
    zero_crossing_rate: float = 0.0
    mfcc_json: str = "[]"
    chroma_json: str = "[]"
    backend: str = ""
    status: str = "pending"
    error: str = ""


@dataclass(slots=True)
class AcousticProfile:
    track_key: str = ""
    is_calm: bool = False
    is_energetic: bool = False
    is_bright: bool = False
    is_dark: bool = False
    is_dynamic: bool = False
    labels: list[str] = field(default_factory=list)


@dataclass(slots=True)
class SimilarityResult:
    track_key: str = ""
    track_id: int = 0
    title: str = ""
    artist: str = ""
    score: float = 0.0
    bpm_diff: float = 0.0
    energy_diff: float = 0.0
    timbre_diff: float = 0.0
    centroid_diff: float = 0.0
    reasons: list[str] = field(default_factory=list)


@dataclass(slots=True)
class AnalysisJob:
    job_id: str = ""
    track_key: str = ""
    status: str = "pending"
    priority: int = 5
    created_at: str = ""
    started_at: str = ""
    finished_at: str = ""
    error: str = ""


@dataclass(slots=True)
class AnalysisStatus:
    backend: str = "disabled"
    available: bool = False
    enabled: bool = False
    total_analyzed: int = 0
    pending_jobs: int = 0
    active_jobs: int = 0
    missing_deps: list[str] = field(default_factory=list)
