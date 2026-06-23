"""Recommendation tools for Michi AI Assistant — local, private, explainable."""

from __future__ import annotations

from typing import Any

from integrations.ai_assistant.schemas import ToolResult


def _get_service(db: Any):
    from recommendation.recommendation_service import RecommendationService
    return RecommendationService(db)


def recommend_music(db: Any, description: str = "",
                    limit: int = 30) -> ToolResult:
    try:
        if not description.strip():
            return ToolResult(
                name="recommend_music", success=False,
                error="Describe que tipo de musica buscas.",
            )
        svc = _get_service(db)
        result = svc.recommend_from_text(description.strip(), limit)
        return ToolResult(name="recommend_music", success=True, data=result)
    except Exception as e:
        return ToolResult(
            name="recommend_music", success=False, error=str(e),
        )


def recommend_from_track(db: Any, track_id: int = 0,
                         limit: int = 30) -> ToolResult:
    try:
        if not track_id:
            return ToolResult(
                name="recommend_from_track", success=False,
                error="Especifica un track_id.",
            )
        svc = _get_service(db)
        result = svc.recommend_from_track(track_id, limit)
        return ToolResult(
            name="recommend_from_track", success=True, data=result,
        )
    except Exception as e:
        return ToolResult(
            name="recommend_from_track", success=False, error=str(e),
        )


def recommend_from_artist(db: Any, artist_name: str = "",
                          limit: int = 30) -> ToolResult:
    try:
        if not artist_name.strip():
            return ToolResult(
                name="recommend_from_artist", success=False,
                error="Especifica un nombre de artista.",
            )
        svc = _get_service(db)
        result = svc.recommend_from_artist(artist_name.strip(), limit)
        return ToolResult(
            name="recommend_from_artist", success=True, data=result,
        )
    except Exception as e:
        return ToolResult(
            name="recommend_from_artist", success=False, error=str(e),
        )


def recommend_from_album(db: Any, album_title: str = "",
                         artist_name: str = "",
                         limit: int = 30) -> ToolResult:
    try:
        if not album_title.strip():
            return ToolResult(
                name="recommend_from_album", success=False,
                error="Especifica un titulo de album.",
            )
        svc = _get_service(db)
        result = svc.recommend_from_album(album_title.strip(), artist_name.strip(), limit)
        return ToolResult(
            name="recommend_from_album", success=True, data=result,
        )
    except Exception as e:
        return ToolResult(
            name="recommend_from_album", success=False, error=str(e),
        )


def recommend_from_genre(db: Any, genre: str = "",
                         limit: int = 30) -> ToolResult:
    try:
        if not genre.strip():
            return ToolResult(
                name="recommend_from_genre", success=False,
                error="Especifica un genero.",
            )
        svc = _get_service(db)
        result = svc.recommend_from_genre(genre.strip(), limit)
        return ToolResult(
            name="recommend_from_genre", success=True, data=result,
        )
    except Exception as e:
        return ToolResult(
            name="recommend_from_genre", success=False, error=str(e),
        )


def create_smart_mix(db: Any, strategy: str = "",
                     seed: dict | None = None,
                     limit: int = 30) -> ToolResult:
    try:
        if not strategy.strip():
            return ToolResult(
                name="create_smart_mix", success=False,
                error="Especifica una estrategia de mix.",
            )
        svc = _get_service(db)
        result = svc.create_smart_mix(strategy.strip(), seed, limit)
        return ToolResult(
            name="create_smart_mix", success=True, data=result,
        )
    except Exception as e:
        return ToolResult(
            name="create_smart_mix", success=False, error=str(e),
        )


def explain_recommendation(db: Any, recommendation_id: str = "",
                           track_id: int = 0) -> ToolResult:
    try:
        if not recommendation_id:
            return ToolResult(
                name="explain_recommendation", success=False,
                error="Especifica un recommendation_id.",
            )
        svc = _get_service(db)
        result = svc.explain_recommendation(recommendation_id, track_id)
        return ToolResult(
            name="explain_recommendation", success=True, data=result,
        )
    except Exception as e:
        return ToolResult(
            name="explain_recommendation", success=False, error=str(e),
        )


def save_recommendation_as_playlist(db: Any, recommendation_id: str = "",
                                     playlist_name: str = "") -> ToolResult:
    try:
        if not recommendation_id:
            return ToolResult(
                name="save_recommendation_as_playlist", success=False,
                error="Especifica un recommendation_id.",
            )
        from recommendation.recommendation_repository import RecommendationRepository
        repo = RecommendationRepository()
        cached = repo.get_cached(recommendation_id)
        if not cached:
            return ToolResult(
                name="save_recommendation_as_playlist", success=False,
                error="Recomendacion no encontrada o expirada.",
            )
        tracks = cached.get("tracks", [])
        if not tracks:
            return ToolResult(
                name="save_recommendation_as_playlist", success=False,
                error="No hay canciones para guardar.",
            )
        name = playlist_name.strip() or f"Recomendación {recommendation_id[:8]}"
        if hasattr(db, "create_playlist"):
            pid = db.create_playlist(name)
            added = 0
            for t in tracks:
                tid = t.get("track_id", 0)
                if tid and hasattr(db, "get_all"):
                    items = db.get_all() or []
                    id_map = {getattr(i, "id", 0): getattr(i, "filepath", "")
                              for i in items}
                    fp = id_map.get(tid)
                    if fp and hasattr(db, "add_to_playlist"):
                        db.add_to_playlist(pid, fp)
                        added += 1
            return ToolResult(
                name="save_recommendation_as_playlist", success=True,
                data={
                    "playlist_id": pid, "playlist_name": name,
                    "track_count": added, "status": "created",
                },
            )
        return ToolResult(
            name="save_recommendation_as_playlist", success=False,
            error="No se pudo crear la playlist.",
        )
    except Exception as e:
        return ToolResult(
            name="save_recommendation_as_playlist", success=False, error=str(e),
        )
