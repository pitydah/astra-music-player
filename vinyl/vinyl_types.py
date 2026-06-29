"""Data types for Vinyl Lab projects and recordings."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class RecordingStatus(str, Enum):
    IDLE = "idle"
    RECORDING = "recording"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class ProjectStatus(str, Enum):
    DRAFT = "draft"
    RECORDING_SIDE_A = "recording_side_a"
    RECORDING_SIDE_B = "recording_side_b"
    SPLITTING = "splitting"
    CLEANING = "cleaning"
    EXPORTING = "exporting"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class CaptureDevice:
    name: str = ""
    description: str = ""
    sample_rates: list[int] = field(default_factory=lambda: [44100, 48000, 96000])
    bit_depths: list[int] = field(default_factory=lambda: [16, 24])
    channels: int = 2
    is_default: bool = False


@dataclass
class VinylProject:
    id: str = ""
    name: str = ""
    status: ProjectStatus = ProjectStatus.DRAFT
    artist: str = ""
    album: str = ""
    year: int = 0
    genre: str = ""
    side_a_path: str = ""
    side_b_path: str = ""
    sample_rate: int = 96000
    bit_depth: int = 24
    channels: int = 2
    created_at: str = ""
    updated_at: str = ""


@dataclass
class TrackSplit:
    id: str = ""
    project_id: str = ""
    side: str = "A"
    track_number: int = 0
    title: str = ""
    start_sec: float = 0.0
    end_sec: float = 0.0
    duration_sec: float = 0.0
    artist: str = ""


@dataclass
class WaveformCache:
    project_id: str = ""
    side: str = "A"
    data: list[float] = field(default_factory=list)
    peaks: list[float] = field(default_factory=list)
    sample_count: int = 0
    duration_sec: float = 0.0
