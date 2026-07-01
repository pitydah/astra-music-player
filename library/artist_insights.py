"""Artist insights — quality, health, appearances, and analysis for artist pages."""
import os as _os
from dataclasses import dataclass, field

from library.library_db import MediaItem
from library.artist_grouping import ArtistGroup

LOSSLESS_EXTS = {"flac", "alac", "wav", "aiff", "ape", "wv", "dsd", "dff", "dsf"}
LOSSY_EXTS = {"mp3", "aac", "m4a", "ogg", "opus", "wma"}


def _normalize_ext(ext: str) -> str:
    return ext.lower().lstrip(".")


@dataclass
class ArtistQualitySummary:
    total_tracks: int = 0
    total_duration: float = 0.0
    formats: dict[str, int] = field(default_factory=dict)
    lossless_count: int = 0
    lossy_count: int = 0
    hi_res_count: int = 0
    unknown_quality_count: int = 0
    average_bitrate: int = 0
    max_sample_rate: int = 0
    max_bit_depth: int = 0
    replaygain_count: int = 0
    replaygain_ratio: float = 0.0
    lossless_ratio: float = 0.0
    dominant_format: str = ""

    @property
    def format_labels(self) -> list[str]:
        labels = []
        for fmt, cnt in sorted(self.formats.items(), key=lambda x: -x[1]):
            labels.append(f"{fmt.upper()} ({cnt})" if cnt > 1 else fmt.upper())
        return labels


@dataclass
class ArtistMetadataHealth:
    missing_album_count: int = 0
    missing_genre_count: int = 0
    missing_year_count: int = 0
    missing_track_number_count: int = 0
    missing_artwork_count: int = 0
    missing_files_count: int = 0
    duplicate_album_candidates: list[str] = field(default_factory=list)
    alias_candidates: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def total_issues(self) -> int:
        return (self.missing_album_count + self.missing_genre_count
                + self.missing_year_count + self.missing_track_number_count
                + self.missing_artwork_count + self.missing_files_count
                + len(self.duplicate_album_candidates) + len(self.alias_candidates))


@dataclass
class ArtistAppearance:
    filepath: str
    title: str
    artist: str
    album: str
    year: int
    reason: str
    confidence: float


@dataclass
class ArtistInsight:
    artist_key: str
    display_name: str
    top_tracks: list[MediaItem] = field(default_factory=list)
    collaborations: list[ArtistAppearance] = field(default_factory=list)
    primary_genres: list[str] = field(default_factory=list)
    active_year_range: tuple[int, int] | None = None
    quality: ArtistQualitySummary = field(default_factory=ArtistQualitySummary)
    health: ArtistMetadataHealth = field(default_factory=ArtistMetadataHealth)


def compute_quality_summary(tracks: list[MediaItem]) -> ArtistQualitySummary:
    summary = ArtistQualitySummary()
    if not tracks:
        return summary

    summary.total_tracks = len(tracks)
    summary.total_duration = sum(getattr(t, "duration", 0) or 0 for t in tracks)

    bitrate_sum = 0
    bitrate_count = 0
    rggain_count = 0

    for t in tracks:
        ext = _normalize_ext(getattr(t, "ext", "") or "")
        if ext:
            summary.formats[ext] = summary.formats.get(ext, 0) + 1
        if ext in LOSSLESS_EXTS:
            summary.lossless_count += 1
        elif ext in LOSSY_EXTS:
            summary.lossy_count += 1
        else:
            summary.unknown_quality_count += 1

        sr = getattr(t, "sample_rate", 0) or 0
        bd = getattr(t, "bit_depth", 0) or 0
        if sr > summary.max_sample_rate:
            summary.max_sample_rate = sr
        if bd > summary.max_bit_depth:
            summary.max_bit_depth = bd
        if ext in LOSSLESS_EXTS and (sr >= 88200 or bd >= 24 or ext in ("dsd", "dff", "dsf")):
            summary.hi_res_count += 1

        br = getattr(t, "bitrate", 0) or 0
        if br:
            bitrate_sum += br
            bitrate_count += 1

        rg = getattr(t, "replaygain_track", 0) or 0
        if rg:
            rggain_count += 1

    summary.average_bitrate = bitrate_sum // bitrate_count if bitrate_count else 0
    summary.replaygain_count = rggain_count
    summary.replaygain_ratio = rggain_count / len(tracks) if tracks else 0.0
    summary.lossless_ratio = summary.lossless_count / len(tracks) if tracks else 0.0

    if summary.formats:
        summary.dominant_format = max(summary.formats, key=summary.formats.get)

    return summary


def compute_metadata_health(group: ArtistGroup) -> ArtistMetadataHealth:
    health = ArtistMetadataHealth()
    missing_album = 0
    missing_genre = 0
    missing_year = 0
    missing_tn = 0

    for t in group.all_tracks:
        if not str(getattr(t, "album", "") or "").strip():
            missing_album += 1
        if not str(getattr(t, "genre", "") or "").strip():
            missing_genre += 1
        if not getattr(t, "year", 0):
            missing_year += 1
        if not getattr(t, "track_number", 0):
            missing_tn += 1

    health.missing_album_count = missing_album
    health.missing_genre_count = missing_genre
    health.missing_year_count = missing_year
    health.missing_track_number_count = missing_tn

    missing_art = 0
    for album in group.albums:
        if not album.cover_path or not _os.path.isfile(album.cover_path):
            missing_art += 1
    health.missing_artwork_count = missing_art

    missing_files = sum(1 for t in group.all_tracks if not _os.path.isfile(t.filepath))
    health.missing_files_count = missing_files

    # Remove duplicate album candidates that are just "Sin álbum"
    health.duplicate_album_candidates = [a for a in health.duplicate_album_candidates if a != "sin álbum"]

    album_titles = [a.title.lower().strip() for a in group.albums if a.title]
    seen = {}
    for a in album_titles:
        if a in seen and a not in health.duplicate_album_candidates:
                health.duplicate_album_candidates.append(a)
        seen[a] = seen.get(a, 0) + 1

    return health


def detect_artist_appearances(group: ArtistGroup, all_items: list[MediaItem]) -> list[ArtistAppearance]:
    appearances = []
    if not all_items or not group:
        return appearances

    name_lower = group.display_name.lower()
    known_tracks = {t.filepath for t in group.all_tracks}

    for item in all_items:
        if item.filepath in known_tracks:
            continue
        artist_raw = str(item.artist or "")
        albumartist_raw = str(getattr(item, "albumartist", "") or "")
        combined = (artist_raw + " " + albumartist_raw).lower()

        if name_lower not in combined:
            continue

        reason = _detect_appearance_reason(name_lower, artist_raw, albumartist_raw)
        if not reason:
            continue

        appearances.append(ArtistAppearance(
            filepath=item.filepath,
            title=item.title or item.filename,
            artist=artist_raw or albumartist_raw,
            album=str(item.album or "") or "",
            year=item.year or 0,
            reason=reason,
            confidence=_compute_confidence(reason, artist_raw, name_lower),
        ))

    appearances.sort(key=lambda a: -a.confidence)
    return appearances


def _detect_appearance_reason(name_lower: str, artist: str, albumartist: str) -> str:
    a_lower = artist.lower()
    aa_lower = albumartist.lower()
    if name_lower in a_lower and any(marker in a_lower for marker in ("feat", "ft.", "featuring", "with")):
        return "feat"
    if name_lower in a_lower and a_lower != name_lower:
        return "colaboración"
    if name_lower in aa_lower and aa_lower != name_lower:
        return "aparición"
    if a_lower == name_lower:
        return ""
    return ""


def _compute_confidence(reason: str, artist: str, name_lower: str) -> float:
    if reason == "feat":
        return 0.95
    if reason == "colaboración":
        artist_lower = artist.lower()
        tokens = artist_lower.replace(name_lower, "").strip().split()
        if tokens:
            return 0.85
        return 0.50
    if reason == "aparición":
        return 0.70
    return 0.50


def rank_top_tracks(group: ArtistGroup, limit: int = 10) -> list[MediaItem]:
    tracks = list(group.all_tracks)
    for t in tracks:
        if not hasattr(t, 'play_count') or t.play_count is None:
            t.play_count = 0
    tracks.sort(key=lambda t: (
        -(getattr(t, 'play_count', 0) or 0),
        getattr(t, 'year', 0) or 0,
        str(getattr(t, 'album', '') or ''),
        getattr(t, 'disc_number', 1) or 1,
        getattr(t, 'track_number', 0) or 0,
    ))
    return tracks[:limit]


def extract_primary_genres(group: ArtistGroup, limit: int = 6) -> list[str]:
    return (group.genres or [])[:limit]


def active_year_range(group: ArtistGroup) -> tuple[int, int] | None:
    years = group.years
    if not years:
        return None
    return years[0], years[-1]


def build_artist_insight(group: ArtistGroup, all_items: list[MediaItem] | None = None) -> ArtistInsight:
    top_tracks = rank_top_tracks(group)
    primary_genres = extract_primary_genres(group)
    year_range = active_year_range(group)
    quality = compute_quality_summary(group.all_tracks)
    health = compute_metadata_health(group)
    collaborations = detect_artist_appearances(group, all_items or [])

    return ArtistInsight(
        artist_key=group.key,
        display_name=group.display_name,
        top_tracks=top_tracks,
        collaborations=collaborations,
        primary_genres=primary_genres,
        active_year_range=year_range,
        quality=quality,
        health=health,
    )



