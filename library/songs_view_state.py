"""SongsFilterState + SongsViewState — typed contracts between UI and service layers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from library.media_item import MediaItem


@dataclass(frozen=True)
class SongsFilterState:
    text: str = ""
    formats: frozenset[str] = field(default_factory=frozenset)
    qualities: frozenset[str] = field(default_factory=frozenset)
    genres: frozenset[str] = field(default_factory=frozenset)
    year_min: int | None = None
    year_max: int | None = None
    bitrate_min: int | None = None
    sample_rate_min: int | None = None
    only_favorites: bool = False
    only_missing_metadata: bool = False
    only_missing_cover: bool = False
    only_missing_file: bool = False
    only_audio_lab_warning: bool = False

    def to_query_kwargs(self) -> dict:
        kwargs = dict(
            text_filter=self.text,
            formats=set(self.formats) if self.formats else None,
            qualities=set(self.qualities) if self.qualities else None,
            genres=set(self.genres) if self.genres else None,
            year_min=self.year_min,
            year_max=self.year_max,
            bitrate_min=self.bitrate_min,
            sample_rate_min=self.sample_rate_min,
            only_favorites=self.only_favorites,
            only_missing_metadata=self.only_missing_metadata,
            only_missing_cover=self.only_missing_cover,
            only_missing_file=self.only_missing_file,
            only_audio_lab_warning=self.only_audio_lab_warning,
        )
        return {k: v for k, v in kwargs.items() if v is not None}


@dataclass(frozen=True)
class SongsViewState:
    items: list[MediaItem]
    favorite_track_ids: frozenset[str]
    status_cache: Mapping[int | str, dict]
    filter_state: SongsFilterState
