"""Knowledge tools for Michi AI Assistant — uses KnowledgeBroker for external metadata."""

from __future__ import annotations

from typing import Any

from integrations.ai_assistant.schemas import ToolResult


def _get_broker() -> Any:
    from integrations.knowledge_broker.service import KnowledgeBrokerService
    global _broker_singleton
    if not hasattr(_get_broker, "_instance") or _get_broker._instance is None:
        try:
            _get_broker._instance = KnowledgeBrokerService()
        except Exception:
            _get_broker._instance = None
    return _get_broker._instance


_get_broker._instance = None


def lookup_artist_info(db: Any, artist_name: str = "",
                       mbid: str = "") -> ToolResult:
    try:
        if not artist_name.strip() and not mbid.strip():
            return ToolResult(
                name="lookup_artist_info", success=False,
                error="Especifica un nombre de artista o MBID.",
            )
        broker = _get_broker()
        if broker is None:
            return ToolResult(
                name="lookup_artist_info", success=False,
                error="KnowledgeBroker no disponible.",
            )
        result = broker.lookup_artist(artist_name.strip(), mbid.strip())
        return ToolResult(name="lookup_artist_info", success=True, data=result)
    except Exception as e:
        return ToolResult(
            name="lookup_artist_info", success=False, error=str(e),
        )


def lookup_album_info(db: Any, album_title: str = "",
                      artist_name: str = "",
                      release_group_mbid: str = "") -> ToolResult:
    try:
        if not album_title.strip() and not release_group_mbid.strip():
            return ToolResult(
                name="lookup_album_info", success=False,
                error="Especifica un titulo de album o MBID.",
            )
        broker = _get_broker()
        if broker is None:
            return ToolResult(
                name="lookup_album_info", success=False,
                error="KnowledgeBroker no disponible.",
            )
        result = broker.lookup_album(
            album_title.strip(), artist_name.strip(), release_group_mbid.strip(),
        )
        return ToolResult(name="lookup_album_info", success=True, data=result)
    except Exception as e:
        return ToolResult(
            name="lookup_album_info", success=False, error=str(e),
        )


def lookup_track_info(db: Any, track_title: str = "",
                      artist_name: str = "",
                      recording_mbid: str = "") -> ToolResult:
    try:
        if not track_title.strip() and not recording_mbid.strip():
            return ToolResult(
                name="lookup_track_info", success=False,
                error="Especifica un titulo de cancion o MBID.",
            )
        broker = _get_broker()
        if broker is None:
            return ToolResult(
                name="lookup_track_info", success=False,
                error="KnowledgeBroker no disponible.",
            )
        result = broker.lookup_recording(
            track_title.strip(), artist_name.strip(), recording_mbid.strip(),
        )
        return ToolResult(name="lookup_track_info", success=True, data=result)
    except Exception as e:
        return ToolResult(
            name="lookup_track_info", success=False, error=str(e),
        )


def explain_artist(db: Any, artist_name: str = "",
                   mbid: str = "") -> ToolResult:
    try:
        if not artist_name.strip() and not mbid.strip():
            return ToolResult(
                name="explain_artist", success=False,
                error="Especifica un nombre de artista.",
            )
        broker = _get_broker()
        if broker is None:
            return ToolResult(
                name="explain_artist", success=False,
                error="KnowledgeBroker no disponible.",
            )
        result = broker.explain_artist(artist_name.strip(), mbid.strip())
        return ToolResult(name="explain_artist", success=True, data=result)
    except Exception as e:
        return ToolResult(
            name="explain_artist", success=False, error=str(e),
        )


def explain_album(db: Any, album_title: str = "",
                  artist_name: str = "") -> ToolResult:
    try:
        if not album_title.strip():
            return ToolResult(
                name="explain_album", success=False,
                error="Especifica un titulo de album.",
            )
        broker = _get_broker()
        if broker is None:
            return ToolResult(
                name="explain_album", success=False,
                error="KnowledgeBroker no disponible.",
            )
        result = broker.explain_album(album_title.strip(), artist_name.strip())
        return ToolResult(name="explain_album", success=True, data=result)
    except Exception as e:
        return ToolResult(
            name="explain_album", success=False, error=str(e),
        )


def refresh_artist_metadata(db: Any, artist_name: str = "",
                            mbid: str = "") -> ToolResult:
    try:
        if not artist_name.strip() and not mbid.strip():
            return ToolResult(
                name="refresh_artist_metadata", success=False,
                error="Especifica un nombre de artista o MBID.",
            )
        broker = _get_broker()
        if broker is None:
            return ToolResult(
                name="refresh_artist_metadata", success=False,
                error="KnowledgeBroker no disponible.",
            )
        result = broker.refresh_artist(artist_name.strip(), mbid.strip())
        return ToolResult(
            name="refresh_artist_metadata", success=True, data=result,
        )
    except Exception as e:
        return ToolResult(
            name="refresh_artist_metadata", success=False, error=str(e),
        )


def refresh_album_metadata(db: Any, album_title: str = "",
                           artist_name: str = "",
                           release_group_mbid: str = "") -> ToolResult:
    try:
        if not album_title.strip() and not release_group_mbid.strip():
            return ToolResult(
                name="refresh_album_metadata", success=False,
                error="Especifica un titulo de album o MBID.",
            )
        broker = _get_broker()
        if broker is None:
            return ToolResult(
                name="refresh_album_metadata", success=False,
                error="KnowledgeBroker no disponible.",
            )
        result = broker.refresh_album(
            album_title.strip(), artist_name.strip(), release_group_mbid.strip(),
        )
        return ToolResult(
            name="refresh_album_metadata", success=True, data=result,
        )
    except Exception as e:
        return ToolResult(
            name="refresh_album_metadata", success=False, error=str(e),
        )
