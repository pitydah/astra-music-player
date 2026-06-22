"""Genre Grouping — build GenreGroup objects from MediaItem list."""
from dataclasses import dataclass, field
from metadata.genre_normalizer import split_genres, genre_key, canonicalize_genre
from metadata.genre_taxonomy import get_family


@dataclass
class GenreGroup:
    key: str = ""
    name: str = ""
    canonical_name: str = ""
    family: str = "Other"
    tracks: list = field(default_factory=list)
    albums: set = field(default_factory=set)
    artists: set = field(default_factory=set)
    cover_paths: list[str] = field(default_factory=list)
    total_duration: float = 0.0
    track_count: int = 0
    artist_count: int = 0
    album_count: int = 0
    play_count: int = 0
    favorite_count: int = 0
    lossless_count: int = 0
    lossy_count: int = 0
    hi_res_count: int = 0
    incomplete_count: int = 0
    avg_bpm: float = 0.0
    years: list[int] = field(default_factory=list)
    year_min: int = 0
    year_max: int = 0
    dominant_decade: str = ""
    quality_summary: str = ""
    gen: int = 0  # generation/split index for multi-genre handling


def build_genre_groups(items: list) -> list[GenreGroup]:
    """Build GenreGroup objects from a list of MediaItems."""
    genre_map: dict[str, GenreGroup] = {}
    untagged = GenreGroup(
        key="untagged",
        name="Sin género",
        canonical_name="Sin género",
        family="Other",
    )
    genre_map["untagged"] = untagged

    for item in items:
        raw_genre = (getattr(item, 'genre', '') or '').strip()
        if not raw_genre:
            untagged.tracks.append(item)
            continue

        genres = split_genres(raw_genre)
        if not genres:
            untagged.tracks.append(item)
            continue

        seen_in_item = set()
        gen_counter = 0
        for genre_name in genres:
            cname = canonicalize_genre(genre_name)
            if not cname:
                continue
            key = genre_key(cname)

            # Deduplicate within the same track
            if key in seen_in_item:
                continue
            seen_in_item.add(key)

            if key not in genre_map:
                family = get_family(cname)
                genre_map[key] = GenreGroup(
                    key=key,
                    name=cname,
                    canonical_name=cname,
                    family=family,
                    gen=gen_counter,
                )
            g = genre_map[key]
            g.tracks.append(item)
            g.gen = max(g.gen, gen_counter)
            gen_counter += 1

    # Aggregate stats
    for g in genre_map.values():
        _aggregate_group(g)

    return sorted(
        [g for g in genre_map.values() if g.track_count > 0 or g.key == "untagged"],
        key=lambda g: (g.name == "Sin género", g.name.lower()),
    )


def _aggregate_group(g: GenreGroup):
    """Compute aggregated stats for a GenreGroup."""
    tracks = g.tracks
    g.track_count = len(tracks)
    g.total_duration = sum(
        getattr(t, 'duration', 0) or 0 for t in tracks)

    albums = set()
    artists = set()
    covers = []
    years = []
    lossless = 0
    lossy = 0
    hi_res = 0
    incomplete = 0
    plays = 0
    favs = 0
    bpms = []

    for t in tracks:
        album = getattr(t, 'album', '') or ''
        if album:
            albums.add(album)
        artist = getattr(t, 'artist', '') or ''
        if artist:
            artists.add(artist)
        if getattr(t, 'cover_path', ''):
            covers.append(t.cover_path)
        yr = getattr(t, 'year', 0)
        if yr:
            years.append(yr)
        sr = getattr(t, 'sample_rate', 0) or 0
        bd = getattr(t, 'bit_depth', 0) or 0
        ext = (getattr(t, 'ext', '') or '').lower()
        lossy_exts = ('.mp3', '.aac', '.wma', '.ogg', '.opus')
        is_lossy = any(ext.endswith(e) for e in lossy_exts)
        if sr >= 88200 or bd >= 24:
            hi_res += 1
        if is_lossy:
            lossy += 1
        else:
            lossless += 1
        if not album or not artist:
            incomplete += 1
        plays += getattr(t, 'play_count', 0) or 0
        if getattr(t, 'rating', 0) and (getattr(t, 'rating', 0) or 0) >= 4:
            favs += 1
        bpm = getattr(t, 'bpm', 0) or 0
        if bpm:
            bpms.append(bpm)

    g.album_count = len(albums)
    g.artist_count = len(artists)
    g.albums = albums
    g.artists = artists
    g.cover_paths = covers[:4]
    g.years = sorted(set(years))
    g.year_min = min(years) if years else 0
    g.year_max = max(years) if years else 0
    if years:
        decade = (g.year_min // 10) * 10
        g.dominant_decade = f"{decade}s"
    g.lossless_count = lossless
    g.lossy_count = lossy
    g.hi_res_count = hi_res
    g.incomplete_count = incomplete
    g.play_count = plays
    g.favorite_count = favs
    if bpms:
        g.avg_bpm = sum(bpms) / len(bpms)

    # Quality summary
    if hi_res > len(tracks) * 0.3:
        g.quality_summary = "Hi-Res"
    elif lossless > lossy:
        g.quality_summary = "Lossless"
    else:
        g.quality_summary = "Mixed"
