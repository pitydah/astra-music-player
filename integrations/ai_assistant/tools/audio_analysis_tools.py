"""Audio analysis tools for Michi AI Assistant — experimental, local only."""

from __future__ import annotations

from typing import Any

from integrations.ai_assistant.schemas import ToolResult


def _get_service(db: Any, worker_mgr: Any = None):
    from audio_analysis.analysis_service import AnalysisService
    return AnalysisService(db, worker_mgr)


def get_audio_analysis_status(db: Any, worker_mgr: Any = None) -> ToolResult:
    try:
        svc = _get_service(db, worker_mgr)
        status = svc.get_status()
        return ToolResult(
            name="get_audio_analysis_status", success=True,
            data={
                "backend": status.backend,
                "available": status.available,
                "enabled": status.enabled,
                "total_analyzed": status.total_analyzed,
                "pending_jobs": status.pending_jobs,
                "active_jobs": status.active_jobs,
                "missing_deps": status.missing_deps,
            },
        )
    except Exception as e:
        return ToolResult(
            name="get_audio_analysis_status", success=False, error=str(e),
        )


def analyze_track_audio(db: Any, track_id: int = 0,
                        worker_mgr: Any = None) -> ToolResult:
    try:
        if not track_id:
            return ToolResult(
                name="analyze_track_audio", success=False,
                error="Especifica un track_id.",
            )
        svc = _get_service(db, worker_mgr)
        result = svc.analyze_track(track_id)
        return ToolResult(
            name="analyze_track_audio", success=True, data=result,
        )
    except Exception as e:
        return ToolResult(
            name="analyze_track_audio", success=False, error=str(e),
        )


def analyze_selected_tracks(db: Any, track_ids: list[int],
                            worker_mgr: Any = None) -> ToolResult:
    try:
        if not track_ids:
            return ToolResult(
                name="analyze_selected_tracks", success=False,
                error="Especifica al menos un track_id.",
            )
        svc = _get_service(db, worker_mgr)
        batch_id = svc.analyze_tracks_async(track_ids)
        return ToolResult(
            name="analyze_selected_tracks", success=True,
            data={
                "batch_id": batch_id,
                "queued": min(len(track_ids), 50),
                "status": "processing",
            },
        )
    except Exception as e:
        return ToolResult(
            name="analyze_selected_tracks", success=False, error=str(e),
        )


def find_sonically_similar(db: Any, track_id: int = 0,
                           limit: int = 30,
                           worker_mgr: Any = None) -> ToolResult:
    try:
        if not track_id:
            return ToolResult(
                name="find_sonically_similar", success=False,
                error="Especifica un track_id.",
            )
        svc = _get_service(db, worker_mgr)
        results = svc.find_sonically_similar(track_id, limit)
        if not results:
            return ToolResult(
                name="find_sonically_similar", success=False,
                error="No se encontraron canciones similares. Analiza algunas primero.",
            )
        return ToolResult(
            name="find_sonically_similar", success=True,
            data={"total": len(results), "results": results},
        )
    except Exception as e:
        return ToolResult(
            name="find_sonically_similar", success=False, error=str(e),
        )


def create_acoustic_mix(db: Any, description: str = "",
                        seed_track_id: int = 0,
                        limit: int = 30,
                        worker_mgr: Any = None) -> ToolResult:
    try:
        strategy = "balanced_mix"
        desc = description.lower() if description else ""
        if any(w in desc for w in ("energ", "power", "workout", "ejercicio")):
            strategy = "energetic_local"
        elif any(w in desc for w in ("calm", "tranquil", "relax", "suave", "focus", "concentr", "noche", "night")):
            strategy = "calm_local"
        elif any(w in desc for w in ("bpm", "tempo")):
            strategy = "bpm_journey"
        elif any(w in desc for w in ("parecido", "similar", "suena como")):
            strategy = "acoustic_similar"

        from recommendation.smart_mix_service import SmartMixService
        mix_svc = SmartMixService(db)
        mix = mix_svc.create_mix(strategy, {"type": "track", "value": str(seed_track_id), "track_id": seed_track_id}, limit)

        return ToolResult(
            name="create_acoustic_mix", success=True,
            data={
                "mix_id": mix.mix_id,
                "title": mix.title,
                "description": mix.description,
                "strategy": mix.strategy,
                "results": [
                    {"track_id": t.track_id, "title": t.title, "artist": t.artist,
                     "album": t.album, "score": t.score, "reasons": t.reasons}
                    for t in mix.tracks
                ],
                "total": len(mix.tracks),
            },
        )
    except Exception as e:
        return ToolResult(
            name="create_acoustic_mix", success=False, error=str(e),
        )


def explain_acoustic_features(db: Any, track_id: int = 0,
                              worker_mgr: Any = None) -> ToolResult:
    try:
        if not track_id:
            return ToolResult(
                name="explain_acoustic_features", success=False,
                error="Especifica un track_id.",
            )
        svc = _get_service(db, worker_mgr)
        from audio_analysis.feature_extractor import make_track_key
        fp = svc._resolve_filepath(track_id)
        if not fp:
            return ToolResult(
                name="explain_acoustic_features", success=False,
                error="Track no encontrado.",
            )
        track_key = make_track_key(fp)
        feat = svc.get_features(track_key)
        if not feat:
            return ToolResult(
                name="explain_acoustic_features", success=False,
                error="No hay features acusticas. Analiza esta cancion primero.",
            )
        from audio_analysis.acoustic_profile import to_safe_labels
        labels = to_safe_labels(feat)
        return ToolResult(
            name="explain_acoustic_features", success=True, data=labels,
        )
    except Exception as e:
        return ToolResult(
            name="explain_acoustic_features", success=False, error=str(e),
        )


def list_tracks_missing_features(db: Any, limit: int = 50,
                                  worker_mgr: Any = None) -> ToolResult:
    try:
        svc = _get_service(db, worker_mgr)
        missing = svc.list_missing_features(limit)
        return ToolResult(
            name="list_tracks_missing_features", success=True,
            data={"total": len(missing), "results": missing},
        )
    except Exception as e:
        return ToolResult(
            name="list_tracks_missing_features", success=False, error=str(e),
        )
