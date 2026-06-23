"""Smart mix service — extends existing smart_mixes.py with new strategies."""

from __future__ import annotations

import time
from typing import Any

from recommendation.schemas import SmartMix, generate_mix_id
from recommendation.similarity_engine import (
    discovery,
    favorites_like,
    seed_radio,
    balanced_mix,
    quality_mix,
)
from recommendation.recommendation_explainer import explain


class SmartMixService:
    def __init__(self, db: Any, profile: Any = None):
        self._db = db
        self._profile = profile

    def _all_items(self) -> list:
        return self._db.get_all() if hasattr(self._db, "get_all") else []

    def _favorite_ids(self) -> set:
        if hasattr(self._db, "get_favorites"):
            return set(self._db.get_favorites() or [])
        return set()

    def create_mix(self, strategy: str, seed: dict | None = None,
                   limit: int = 30) -> SmartMix:
        items = self._all_items()
        if not items:
            return SmartMix(
                mix_id=generate_mix_id(), title="Sin resultados",
                description="No se encontraron canciones en la biblioteca.",
                strategy=strategy,
            )

        seed_item = None
        if seed and seed.get("track_id"):
            for item in items:
                if getattr(item, "id", 0) == seed["track_id"]:
                    seed_item = item
                    break

        tracks = []
        title = ""
        desc = ""

        if strategy == "genre_journey":
            genre = seed.get("genre", "") if seed else ""
            if not genre and self._profile:
                genre = (self._profile.top_genres or [""])[0]
            seed_obj = type("Seed", (), {"genre": genre, "artist": "", "year": 0, "ext": ""})()
            from recommendation.similarity_engine import metadata_similarity
            tracks = metadata_similarity(items, seed_obj, limit=limit)
            title = f"Viaje por {genre}" if genre else "Viaje musical"
            desc = f"Canciones del genero {genre}" if genre else "Exploracion musical por generos"

        elif strategy == "decade_mix":
            year_str = seed.get("year", "1990") if seed else "1990"
            try:
                decade = int(int(year_str) / 10) * 10
            except (ValueError, TypeError):
                decade = 1990
            decade_items = [
                i for i in items
                if getattr(i, "year", 0) and decade <= int(getattr(i, "year", 0)) < decade + 10
            ]
            if decade_items:
                from recommendation.similarity_engine import _build_result, _quality_bonus
                for item in decade_items[:limit]:
                    tracks.append(_build_result(
                        item, _quality_bonus(item) * 0.5 + 0.5,
                        [f"Decada de los {decade % 100}"], "decade_mix",
                    ))
            title = f"Decada de los {decade % 100}"
            desc = f"Canciones de los años {decade}"

        elif strategy == "lossless_showcase":
            tracks = quality_mix(items, limit=limit)
            title = "Muestra lossless"
            desc = "Canciones en formato sin perdida"

        elif strategy == "favorites_neighbors":
            fav_ids = self._favorite_ids()
            if fav_ids:
                tracks = favorites_like(items, fav_ids, limit=limit)
            else:
                tracks = discovery(items, limit=limit)
            title = "Vecinos de favoritos"
            desc = "Canciones similares a tus favoritas"

        elif strategy == "recently_missed":
            played = set()
            for i in items:
                if getattr(i, "play_count", 0) > 0 and getattr(i, "last_played", 0):
                    lp = getattr(i, "last_played", 0)
                    if lp > time.time() - 86400 * 30:
                        played.add(getattr(i, "id", 0))
            tracks = discovery(items, played_ids=played, limit=limit)
            title = "Te las perdiste"
            desc = "Canciones que no escuchas hace mas de 30 dias"

        elif strategy == "deep_cuts":
            fav_ids = self._favorite_ids()
            if fav_ids:
                from recommendation.similarity_engine import _build_result, _genre_overlap
                favs = [i for i in items if getattr(i, "id", 0) in fav_ids]
                scores = []
                for item in items:
                    if getattr(item, "id", 0) in fav_ids:
                        continue
                    score = 0.0
                    for fav in favs:
                        score += _genre_overlap(item, fav) * 0.5
                        years = abs(int(getattr(item, "year", 0) or 0) - int(getattr(fav, "year", 0) or 0))
                        score += 1.0 / (1 + years * 0.3) * 0.3
                        if getattr(item, "artist", "").lower() == getattr(fav, "artist", "").lower():
                            score += 0.2
                    score /= max(len(favs), 1)
                    if score > 0.1:
                        scores.append((score, item))
                scores.sort(key=lambda x: x[0], reverse=True)
                tracks = [_build_result(item, s, ["Corte profundo", "Similar a tus favoritos"], "deep_cuts")
                          for s, item in scores[:limit]]
            title = "Cortes profundos"
            desc = "Canciones ocultas que podrian gustarte"

        elif strategy == "similar_to_artist":
            artist = seed.get("artist", "") if seed else ""
            if artist and seed_item:
                tracks = seed_radio(items, seed_item, limit=limit)
            elif artist:
                seed_obj = type("Seed", (), {"artist": artist, "genre": "", "year": 0, "ext": "", "album": ""})()
                from recommendation.similarity_engine import metadata_similarity
                tracks = metadata_similarity(items, seed_obj, limit=limit)
            title = f"Similar a {artist}" if artist else "Mix por artista"
            desc = f"Canciones similares a {artist}" if artist else "Recomendaciones por artista"

        elif strategy == "similar_to_album":
            album = seed.get("album", "") if seed else ""
            artist = seed.get("artist", "") if seed else ""
            if seed_item:
                tracks = seed_radio(items, seed_item, limit=limit)
            else:
                seed_obj = type("Seed", (), {"artist": artist, "genre": "", "year": 0, "ext": "", "album": album})()
                from recommendation.similarity_engine import metadata_similarity
                tracks = metadata_similarity(items, seed_obj, limit=limit)
            title = f"Como {album}" if album else "Mix por album"
            desc = f"Mezcla basada en el album {album}" if album else "Recomendaciones por album"

        else:
            tracks = balanced_mix(items,
                type("Seed", (), {"artist": "", "genre": "", "year": 0, "ext": "", "album": ""})(),
                limit=limit)
            title = "Mix balanceado"
            desc = "Mezcla entre canciones familiares y por descubrir"

        explanations = [explain(t) for t in tracks]  # noqa: F841  # kept for future UI use

        return SmartMix(
            mix_id=generate_mix_id(),
            title=title, description=desc,
            strategy=strategy,
            seed_type=seed.get("type", "") if seed else "",
            seed_value=seed.get("value", "") if seed else "",
            tracks=tracks, explanation=desc,
            created_at=time.strftime("%Y-%m-%dT%H:%M:%S"),
            is_saved=False,
        )
