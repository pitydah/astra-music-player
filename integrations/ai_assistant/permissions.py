"""Tool permission definitions for Michi AI Assistant."""

from __future__ import annotations

from integrations.ai_assistant.schemas import PermissionLevel

TOOL_PERMISSIONS: dict[str, PermissionLevel] = {
    "search_library":             PermissionLevel.READ_ONLY,
    "get_library_stats":          PermissionLevel.READ_ONLY,
    "find_metadata_gaps":         PermissionLevel.READ_ONLY,
    "recommend_local_tracks":     PermissionLevel.READ_ONLY,
    "draft_playlist":             PermissionLevel.READ_ONLY,
    "create_playlist_from_draft": PermissionLevel.REVERSIBLE,
    "add_tracks_to_queue":        PermissionLevel.REVERSIBLE,
    "play_track":                 PermissionLevel.REVERSIBLE,
    "mark_favorite":              PermissionLevel.REVERSIBLE,
    "unmark_favorite":            PermissionLevel.REVERSIBLE,
    "open_artist_view":           PermissionLevel.READ_ONLY,
    "open_album_view":            PermissionLevel.READ_ONLY,
    "open_genre_view":            PermissionLevel.READ_ONLY,
    "open_playlist_view":         PermissionLevel.READ_ONLY,
    "show_track_in_library":      PermissionLevel.READ_ONLY,
    "lookup_artist_info":         PermissionLevel.READ_ONLY,
    "lookup_album_info":          PermissionLevel.READ_ONLY,
    "lookup_track_info":          PermissionLevel.READ_ONLY,
    "explain_artist":             PermissionLevel.READ_ONLY,
    "explain_album":              PermissionLevel.READ_ONLY,
    "refresh_artist_metadata":    PermissionLevel.REVERSIBLE,
    "refresh_album_metadata":     PermissionLevel.REVERSIBLE,
    "find_metadata_inconsistencies": PermissionLevel.READ_ONLY,
    "suggest_metadata_for_track":    PermissionLevel.READ_ONLY,
    "suggest_metadata_for_album":    PermissionLevel.READ_ONLY,
    "suggest_metadata_for_artist":   PermissionLevel.READ_ONLY,
    "create_metadata_review":        PermissionLevel.READ_ONLY,
    "apply_metadata_review":         PermissionLevel.REVERSIBLE,
    "reject_metadata_review":        PermissionLevel.REVERSIBLE,
    "undo_metadata_review":          PermissionLevel.REVERSIBLE,
    "recommend_music":                PermissionLevel.READ_ONLY,
    "recommend_from_track":           PermissionLevel.READ_ONLY,
    "recommend_from_artist":          PermissionLevel.READ_ONLY,
    "recommend_from_album":           PermissionLevel.READ_ONLY,
    "recommend_from_genre":           PermissionLevel.READ_ONLY,
    "create_smart_mix":               PermissionLevel.READ_ONLY,
    "explain_recommendation":         PermissionLevel.READ_ONLY,
    "save_recommendation_as_playlist": PermissionLevel.REVERSIBLE,
    "get_audio_analysis_status":       PermissionLevel.READ_ONLY,
    "analyze_track_audio":             PermissionLevel.RESOURCE_INTENSIVE,
    "analyze_selected_tracks":         PermissionLevel.RESOURCE_INTENSIVE,
    "find_sonically_similar":          PermissionLevel.READ_ONLY,
    "create_acoustic_mix":             PermissionLevel.READ_ONLY,
    "explain_acoustic_features":       PermissionLevel.READ_ONLY,
    "list_tracks_missing_features":    PermissionLevel.READ_ONLY,
}


def is_allowed(tool_name: str, max_level: PermissionLevel) -> bool:
    required = TOOL_PERMISSIONS.get(tool_name)
    if required is None:
        return False
    return required.value <= max_level.value


def tool_description(tool_name: str) -> str:
    descriptions = {
        "search_library":             "Buscar canciones en la biblioteca local por texto, artista, album, genero o año.",
        "get_library_stats":          "Obtener estadisticas de la biblioteca: total de canciones, artistas, albumes, generos, formatos, duracion.",
        "find_metadata_gaps":         "Detectar canciones con metadatos faltantes (sin artista, album, genero, año o caratula).",
        "recommend_local_tracks":     "Recomendar canciones locales basadas en un texto semilla usando coincidencias de metadatos.",
        "draft_playlist":             "Crear borrador de playlist en memoria (no se guarda automaticamente).",
        "create_playlist_from_draft": "Crear una playlist real desde un borrador confirmado.",
        "add_tracks_to_queue":        "Añadir canciones a la cola de reproduccion.",
        "play_track":                 "Reproducir una cancion especifica.",
        "mark_favorite":              "Marcar canciones como favoritas.",
        "unmark_favorite":            "Desmarcar canciones de favoritos.",
        "open_artist_view":           "Abrir la vista de un artista en la biblioteca.",
        "open_album_view":            "Abrir la vista de un album en la biblioteca.",
        "open_genre_view":            "Abrir la vista de un genero en la biblioteca.",
        "open_playlist_view":         "Abrir la vista de una playlist.",
        "show_track_in_library":      "Mostrar una cancion en la biblioteca.",
        "lookup_artist_info":         "Buscar informacion de artista en KnowledgeBroker (MusicBrainz).",
        "lookup_album_info":          "Buscar informacion de album en KnowledgeBroker (MusicBrainz + CoverArt).",
        "lookup_track_info":          "Buscar informacion de cancion en KnowledgeBroker (MusicBrainz).",
        "explain_artist":             "Explicar quien es un artista usando Wikipedia.",
        "explain_album":              "Explicar un album usando Wikipedia.",
        "refresh_artist_metadata":    "Refrescar cache de artista desde MusicBrainz.",
        "refresh_album_metadata":     "Refrescar cache de album desde MusicBrainz y CoverArt.",
        "find_metadata_inconsistencies": "Detectar canciones con metadata inconsistente o incompleta.",
        "suggest_metadata_for_track":    "Sugerir correcciones de metadata para una cancion usando MusicBrainz.",
        "suggest_metadata_for_album":    "Sugerir correcciones de metadata para un album.",
        "suggest_metadata_for_artist":   "Sugerir metadata para un artista.",
        "create_metadata_review":        "Crear una revision de metadata con comparacion antes/despues.",
        "apply_metadata_review":         "Aplicar cambios de metadata aceptados (requiere confirmacion).",
        "reject_metadata_review":        "Rechazar una revision de metadata.",
        "undo_metadata_review":          "Deshacer cambios de metadata aplicados.",
        "recommend_music":                "Recomendar musica local por descripcion en texto libre.",
        "recommend_from_track":           "Recomendar canciones similares a una cancion.",
        "recommend_from_artist":          "Recomendar canciones similares a un artista.",
        "recommend_from_album":           "Recomendar canciones similares a un album.",
        "recommend_from_genre":           "Recomendar canciones de un genero.",
        "create_smart_mix":               "Crear un mix inteligente (genre_journey, decade_mix, lossless_showcase, etc).",
        "explain_recommendation":         "Explicar por que se recomendo una cancion.",
        "save_recommendation_as_playlist": "Guardar una recomendacion como playlist real (requiere confirmacion).",
    }
    return descriptions.get(tool_name, "")
