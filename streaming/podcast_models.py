"""Podcast models — data classes for podcasts and episodes."""

from __future__ import annotations

import dataclasses


@dataclasses.dataclass
class PodcastShow:
    id: str = ""
    title: str = ""
    author: str = ""
    description: str = ""
    image_url: str = ""
    feed_url: str = ""
    website: str = ""
    episode_count: int = 0
    new_count: int = 0
    language: str = ""
    categories: list[str] = dataclasses.field(default_factory=list)
    last_build: str = ""


@dataclasses.dataclass
class PodcastEpisode:
    id: str = ""
    show_id: str = ""
    title: str = ""
    description: str = ""
    audio_url: str = ""
    audio_format: str = ""
    duration_sec: int = 0
    file_size: int = 0
    published: str = ""
    image_url: str = ""
    status: str = "new"
    progress_sec: int = 0
    downloaded: bool = False
    download_path: str = ""
    is_favorite: bool = False


@dataclasses.dataclass
class BroadcastHistoryEntry:
    id: str = ""
    entry_type: str = "radio"
    title: str = ""
    source: str = ""
    url: str = ""
    started_at: str = ""
    duration_sec: int = 0
    completed: bool = False
