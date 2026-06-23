"""Recommendation explainer — rule-based, no LLM hallucination."""

from __future__ import annotations

from recommendation.schemas import RecommendationResult, RecommendationExplanation


def explain(result: RecommendationResult) -> RecommendationExplanation:
    reasons = list(result.reasons) if result.reasons else []
    strategy = result.strategy or "similarity"

    if not reasons:
        if strategy == "metadata_similarity":
            reasons.append("Coincide en estilo con la referencia")
        elif strategy == "discovery":
            reasons.append("No la has escuchado antes")
        elif strategy == "favorites_like":
            reasons.append("Similar a tus favoritos")
        elif strategy == "seed_radio":
            reasons.append("Radio local basada en la referencia")
        elif strategy == "balanced_mix":
            reasons.append("Mezcla entre familiar y nuevo")
        elif strategy == "quality_mix":
            reasons.append("Audio de alta calidad")
        else:
            reasons.append("Recomendacion basada en tu biblioteca")

    summary_map = {
        "metadata_similarity": f"Recomendado por similitud musical a {result.artist} (score: {result.score:.0%})",
        "discovery": "Descubrimiento: cancion no escuchada que coincide con tus gustos",
        "favorites_like": "Similar a las canciones que tienes en favoritos",
        "seed_radio": f"Radio basada en {result.artist}",
        "balanced_mix": "Mix equilibrado entre familiar y nuevo",
        "quality_mix": "Audio de alta calidad: " + result.format.upper(),
    }

    return RecommendationExplanation(
        track_id=result.track_id,
        score=result.score,
        reason_summary=summary_map.get(strategy, reasons[0] if reasons else "Recomendacion local"),
        detailed_reasons=reasons,
    )
