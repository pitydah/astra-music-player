"""Disc detection service — optical drive and audio CD detection. STUB."""

from __future__ import annotations


class DiscDetectionService:
    def detect_drives(self) -> list[str]:
        return []

    def detect_audio_cd(self, drive: str = "") -> bool:
        return False

    def get_default_drive(self) -> str:
        return ""

    def get_disc_toc(self, drive: str = "") -> dict:
        return {"tracks": 0, "duration_seconds": 0}

    def get_track_count(self, drive: str = "") -> int:
        return 0

    def get_track_durations(self, drive: str = "") -> list[float]:
        return []
