"""Album Summary — lightweight dataclass for album info banner."""
from dataclasses import dataclass, field


@dataclass
class AlbumSummary:
    album_key: str = ""
    title: str = ""
    artist: str = ""
    year: str = ""
    genre: str = ""
    style: str = ""
    mood: str = ""
    description: str = ""
    track_count: int = 0
    duration: float = 0.0
    cover_path: str = ""
    cover_url: str = ""
    thumb_path: str = ""
    thumb_url: str = ""
    fanart_path: str = ""
    source: str = "local"
    match_confidence: float = 0.0
    updated_at: str = ""
    dominant_color: str = ""
    track_list: list = field(default_factory=list)
    external_ids: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.track_list is None:
            self.track_list = []
        if self.external_ids is None:
            self.external_ids = {}
