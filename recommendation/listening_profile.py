"""Listening profile — builds aggregated user profile from play history (no raw data exposed)."""

from __future__ import annotations

from typing import Any
from collections import Counter

from recommendation.schemas import ListeningProfile


def build_profile(db: Any, use_favorites: bool = True,
                  max_items: int = 200) -> ListeningProfile:
    profile = ListeningProfile()

    items = db.get_all() if hasattr(db, "get_all") else []

    artist_counter: Counter = Counter()
    genre_counter: Counter = Counter()
    album_counter: Counter = Counter()
    year_counter: Counter = Counter()
    format_counter: Counter = Counter()

    played_ids: set = set()
    favorite_ids: set = set()
    recent_artist = ""
    recent_genre = ""

    for item in items:
        artist = str(getattr(item, "artist", "") or "").strip()
        genre_str = str(getattr(item, "genre", "") or "").strip()
        album = str(getattr(item, "album", "") or "").strip()
        ext = str(getattr(item, "ext", "") or "").strip(".").lower()
        year_val = getattr(item, "year", 0) or 0
        play_count = getattr(item, "play_count", 0) or 0
        last_played = getattr(item, "last_played", 0) or 0

        if play_count > 0:
            played_ids.add(getattr(item, "id", 0))

        if artist:
            artist_counter[artist.lower()] += play_count
        if genre_str:
            for g in genre_str.replace(",", " ").replace("/", " ").split():
                g = g.strip().lower()
                if g:
                    genre_counter[g] += play_count
        if album and artist:
            album_counter[f"{artist.lower()}|{album.lower()}"] += play_count
        try:
            yr = int(year_val)
            if 1900 <= yr <= 2099:
                year_counter[yr] += play_count
        except (ValueError, TypeError):
            pass
        if ext:
            format_counter[ext] += play_count

        if last_played > getattr(item, "_max_lp", 0):
            recent_artist = artist
            recent_genre = genre_str.split(",")[0].strip() if genre_str else ""

    if hasattr(db, "get_favorites") and use_favorites:
        favs = db.get_favorites() or []
        favorite_ids = set(favs)

    profile.top_artists = [a for a, _ in artist_counter.most_common(10)]
    profile.top_genres = [g for g, _ in genre_counter.most_common(10)]
    profile.top_albums = [
        a.split("|", 1)[1] if "|" in a else a
        for a, _ in album_counter.most_common(10)
    ]
    profile.preferred_years = [y for y, _ in year_counter.most_common(5)]
    profile.preferred_formats = [f for f, _ in format_counter.most_common(3)]
    profile.unplayed_count = len(items) - len(played_ids) if items else 0
    profile.favorite_count = len(favorite_ids)
    profile.total_plays = sum(play_count for _ in items)
    profile.recent_artist = recent_artist
    profile.recent_genre = recent_genre

    return profile
