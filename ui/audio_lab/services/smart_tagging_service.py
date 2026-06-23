"""Smart Tagging service — AI-assisted metadata suggestions. STUB."""

from __future__ import annotations

from ui.audio_lab.models import TagSuggestion, TrackMetadata


class SmartTaggingService:
    def analyze_files(self, paths: list[str]) -> list[TrackMetadata]:
        return []

    def suggest_tag_corrections(self, track_metadata: TrackMetadata) -> list[TagSuggestion]:
        return []

    def normalize_artist_name(self, name: str) -> TagSuggestion:
        return TagSuggestion(
            field="artist", current=name, suggested=name,
            confidence=0.0, source="ai_normalization", apply=False,
        )

    def suggest_genre(self, track_metadata: TrackMetadata) -> TagSuggestion:
        return TagSuggestion(
            field="genre", current=track_metadata.genre or "",
            suggested="", confidence=0.0, source="ai_suggestion", apply=False,
        )

    def detect_featured_artists(self, title_or_artist: str) -> list[str]:
        return []

    def suggest_folder_structure(self, album_metadata: dict) -> str:
        return ""

    def generate_album_description(self, album_metadata: dict) -> str:
        return ""
