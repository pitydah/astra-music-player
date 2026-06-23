"""Recommendation service — orchestrates similarity, profile, mixes, and explanations."""

from __future__ import annotations

import logging
from typing import Any

from recommendation.schemas import (
    RecommendationResult,
    SmartMix,
    ListeningProfile,
    generate_recommendation_id,
)
from recommendation.similarity_engine import (
    metadata_similarity,
    discovery,
    seed_radio,
)
from recommendation.recommendation_explainer import explain
from recommendation.recommendation_repository import RecommendationRepository
from recommendation.listening_profile import build_profile
from recommendation.smart_mix_service import SmartMixService

logger = logging.getLogger("michi.recommendation.service")


def _sanitize_results(results: list[RecommendationResult]) -> list[dict]:
    return [
        {
            "track_id": r.track_id, "title": r.title, "artist": r.artist,
            "album": r.album, "year": r.year, "genre": r.genre,
            "duration": r.duration, "format": r.format,
            "score": r.score, "reasons": r.reasons, "strategy": r.strategy,
        }
        for r in results
    ]


class RecommendationService:
    def __init__(self, db: Any, profile: ListeningProfile | None = None,
                 use_favorites: bool = True, use_history: bool = False,
                 cache_days: int = 7):
        self._db = db
        self._profile = profile or build_profile(db, use_favorites=use_favorites)
        self._repo = RecommendationRepository()
        self._mix_svc = SmartMixService(db, self._profile)
        self._use_history = use_history
        self._cache_days = cache_days

    def _items(self) -> list:
        return self._db.get_all() if hasattr(self._db, "get_all") else []

    def _find_seed(self, text: str):
        items = self._items()
        text_lower = text.lower().strip()
        for item in items:
            artist = str(getattr(item, "artist", "") or "").lower()
            album = str(getattr(item, "album", "") or "").lower()
            title = str(getattr(item, "title", "") or "").lower()
            genre = str(getattr(item, "genre", "") or "").lower()
            if text_lower in artist:
                return item
            if text_lower in album:
                return item
            if text_lower in title:
                return item
            if text_lower in genre:
                return item
        return None

    def recommend_from_text(self, description: str,
                            limit: int = 30) -> dict[str, Any]:
        rec_id = generate_recommendation_id()
        items = self._items()
        seed = self._find_seed(description)
        results: list[RecommendationResult] = []

        if seed:
            results = seed_radio(items, seed, limit=limit)
            strategy = "seed_radio"
        elif self._profile and self._profile.top_artists:
            seed_obj = type("Seed", (), {
                "artist": self._profile.top_artists[0],
                "genre": self._profile.top_genres[0] if self._profile.top_genres else "",
                "year": self._profile.preferred_years[0] if self._profile.preferred_years else 0,
                "ext": self._profile.preferred_formats[0] if self._profile.preferred_formats else "",
                "album": "",
            })()
            results = metadata_similarity(items, seed_obj, limit=limit)
            strategy = "metadata_similarity"
        else:
            results = discovery(items, limit=limit)
            strategy = "discovery"

        explanations = [explain(r) for r in results]
        self._repo.cache_recommendation(rec_id, "text", description,
                                         strategy, results, explanations, self._cache_days)

        return {
            "recommendation_id": rec_id,
            "seed": {"type": "text", "value": description},
            "strategy": strategy,
            "results": _sanitize_results(results),
            "total": len(results),
        }

    def recommend_from_track(self, track_id: int,
                             limit: int = 30) -> dict[str, Any]:
        rec_id = generate_recommendation_id()
        items = self._items()
        seed = next((i for i in items if getattr(i, "id", 0) == track_id), None)
        if not seed:
            return {"recommendation_id": rec_id, "error": "Track no encontrado.", "results": []}

        results = seed_radio(items, seed, limit=limit, exclude_id=track_id)
        explanations = [explain(r) for r in results]
        self._repo.cache_recommendation(rec_id, "track", str(track_id),
                                         "seed_radio", results, explanations, self._cache_days)

        return {
            "recommendation_id": rec_id,
            "seed": {"type": "track", "value": str(track_id),
                     "title": getattr(seed, "title", ""), "artist": getattr(seed, "artist", "")},
            "strategy": "seed_radio",
            "results": _sanitize_results(results),
            "total": len(results),
        }

    def recommend_from_artist(self, artist_name: str,
                              limit: int = 30) -> dict[str, Any]:
        rec_id = generate_recommendation_id()
        items = self._items()
        seed = type("Seed", (), {
            "artist": artist_name, "genre": "", "year": 0, "ext": "", "album": "",
        })()
        results = metadata_similarity(items, seed, limit=limit)
        explanations = [explain(r) for r in results]
        self._repo.cache_recommendation(rec_id, "artist", artist_name,
                                         "metadata_similarity", results, explanations, self._cache_days)
        return {
            "recommendation_id": rec_id,
            "seed": {"type": "artist", "value": artist_name},
            "strategy": "metadata_similarity",
            "results": _sanitize_results(results),
            "total": len(results),
        }

    def recommend_from_album(self, album_title: str, artist_name: str = "",
                             limit: int = 30) -> dict[str, Any]:
        rec_id = generate_recommendation_id()
        items = self._items()
        seed = type("Seed", (), {
            "artist": artist_name, "genre": "", "year": 0, "ext": "", "album": album_title,
        })()
        results = metadata_similarity(items, seed, limit=limit)
        explanations = [explain(r) for r in results]
        self._repo.cache_recommendation(rec_id, "album", album_title,
                                         "metadata_similarity", results, explanations, self._cache_days)
        return {
            "recommendation_id": rec_id,
            "seed": {"type": "album", "value": album_title, "artist": artist_name},
            "strategy": "metadata_similarity",
            "results": _sanitize_results(results),
            "total": len(results),
        }

    def recommend_from_genre(self, genre: str, limit: int = 30) -> dict[str, Any]:
        rec_id = generate_recommendation_id()
        items = self._items()
        seed = type("Seed", (), {
            "artist": "", "genre": genre, "year": 0, "ext": "", "album": "",
        })()
        results = metadata_similarity(items, seed, limit=limit)
        explanations = [explain(r) for r in results]
        self._repo.cache_recommendation(rec_id, "genre", genre,
                                         "metadata_similarity", results, explanations, self._cache_days)
        return {
            "recommendation_id": rec_id,
            "seed": {"type": "genre", "value": genre},
            "strategy": "metadata_similarity",
            "results": _sanitize_results(results),
            "total": len(results),
        }

    def create_smart_mix(self, strategy: str, seed: dict | None = None,
                         limit: int = 30) -> dict[str, Any]:
        mix: SmartMix = self._mix_svc.create_mix(strategy, seed, limit)
        return {
            "mix_id": mix.mix_id,
            "title": mix.title,
            "description": mix.description,
            "strategy": mix.strategy,
            "seed_type": mix.seed_type,
            "seed_value": mix.seed_value,
            "results": _sanitize_results(mix.tracks),
            "explanation": mix.explanation,
            "total": len(mix.tracks),
        }

    def explain_recommendation(self, recommendation_id: str,
                               track_id: int = 0) -> dict[str, Any]:
        cached = self._repo.get_cached(recommendation_id)
        if cached and cached.get("explanations"):
            for e in cached["explanations"]:
                if e.get("track_id") == track_id:
                    return {
                        "track_id": track_id,
                        "explanation": {
                            "reason_summary": e.get("reason_summary", ""),
                            "detailed_reasons": e.get("detailed_reasons", []),
                        },
                    }
        return {
            "track_id": track_id,
            "explanation": {
                "reason_summary": "Recomendacion basada en tu biblioteca local.",
                "detailed_reasons": ["Coincidencia por metadata musical"],
            },
        }

    def record_feedback(self, recommendation_id: str, track_id: int,
                        feedback: str) -> dict[str, Any]:
        self._repo.record_feedback(recommendation_id, str(track_id), feedback)
        return {"status": "recorded", "recommendation_id": recommendation_id,
                "track_id": track_id, "feedback": feedback}

    def get_profile_summary(self) -> dict[str, Any]:
        return {
            "top_artists": self._profile.top_artists[:10],
            "top_genres": self._profile.top_genres[:10],
            "top_albums": self._profile.top_albums[:10],
            "preferred_years": self._profile.preferred_years[:5],
            "preferred_formats": self._profile.preferred_formats[:3],
            "unplayed_count": self._profile.unplayed_count,
            "favorite_count": self._profile.favorite_count,
            "total_plays": self._profile.total_plays,
        }

    def rebuild_profile(self) -> dict[str, Any]:
        self._profile = build_profile(self._db, use_favorites=True)
        return self.get_profile_summary()
