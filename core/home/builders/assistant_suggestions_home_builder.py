"""AssistantSuggestionsHomeBuilder — builds AssistantSuggestion list."""

from __future__ import annotations

import logging
from typing import Any

from core.home.home_status import AssistantSuggestion, LibraryHomeStatus, PlaybackHomeStatus

logger = logging.getLogger("michi.home.builders.suggestions")


def build_assistant_suggestions(
    library: LibraryHomeStatus,
    playback: PlaybackHomeStatus,
    context_svc: Any = None,
) -> list[AssistantSuggestion]:
    suggestions: list[AssistantSuggestion] = []

    if context_svc is not None:
        try:
            snap = context_svc.get_assistant_snapshot()
            if snap and "suggested_actions" in snap:
                for act in snap["suggested_actions"][:3]:
                    suggestions.append(AssistantSuggestion(
                        title=act.get("label", act.get("title", "")),
                        message=act.get("description", ""),
                        target_route=act.get("route", ""),
                        action_kind=act.get("kind", "navigate"),
                        priority=act.get("priority", 0),
                    ))
                if suggestions:
                    return suggestions
        except Exception:
            logger.debug("Assistant snapshot unavailable")

    if library.missing_metadata_count > 0:
        suggestions.append(AssistantSuggestion(title="Limpiar metadatos", message=f"{library.missing_metadata_count} canciones con metadatos incompletos", target_route="metadata_editor", action_kind="navigate", priority=10))

    if library.missing_cover_count > 0:
        suggestions.append(AssistantSuggestion(title="Buscar caratulas", message=f"{library.missing_cover_count} albumes sin caratula", target_route="audio_lab_artwork", action_kind="navigate", priority=8))

    if library.track_count > 0 and not playback.can_continue:
        suggestions.append(AssistantSuggestion(title="Explorar biblioteca", message="Descubre nueva musica en tu biblioteca", target_route="library_hub", action_kind="navigate", priority=5))

    if not suggestions and library.track_count > 0:
        suggestions.append(AssistantSuggestion(title="Crear mix de novedades", message="Genera un mix automatico con canciones recien agregadas", target_route="mix_hub", action_kind="navigate", priority=3))

    if not suggestions:
        suggestions.append(AssistantSuggestion(title="Anadir musica", message="Agrega carpetas o archivos para comenzar", target_route="library_hub", action_kind="navigate", priority=1))

    return suggestions[:3]
