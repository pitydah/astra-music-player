"""Library Doctor — metadata quality diagnostics. STUB."""

from __future__ import annotations


class LibraryDoctor:
    def scan_missing_metadata(self) -> list[dict]:
        return []

    def detect_duplicate_artists(self) -> list[dict]:
        return []

    def detect_split_albums(self) -> list[dict]:
        return []

    def detect_missing_artwork(self) -> list[dict]:
        return []

    def detect_possible_duplicates(self) -> list[dict]:
        return []

    def generate_repair_plan(self) -> dict:
        return {
            "total_issues": 0,
            "fixable": 0,
            "suggestions": [],
        }
