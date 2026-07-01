"""Audio conversion tools — recommend profiles, never convert files."""

from __future__ import annotations


from integrations.ai_assistant.schemas import ToolResult

_MOBILE_PROFILES = {
    "space_saver": {"codec": "opus", "bitrate": "128k", "container": "ogg", "reason": "Maximo ahorro de espacio con buena calidad para reproduccion movil."},
    "balanced": {"codec": "opus", "bitrate": "160k", "container": "ogg", "reason": "Equilibrio optimo entre calidad y tamano para uso diario."},
    "high_quality": {"codec": "opus", "bitrate": "256k", "container": "ogg", "reason": "Alta calidad para escucha exigente en dispositivo movil."},
}

_MICRO_SERVER_PROFILES = {
    "remote": {"codec": "opus", "bitrate": "128k-160k", "container": "ogg", "reason": "Perfil liviano para streaming remoto por Tailscale o internet."},
    "lan": {"codec": "flac", "bitrate": "original", "container": "flac", "reason": "Calidad original para red local estable."},
    "balanced": {"codec": "opus", "bitrate": "192k", "container": "ogg", "reason": "Buena calidad para redes mixtas LAN/remoto."},
}

_HIFI_PROFILES = {
    "hifi": {"codec": "flac", "bitrate": "original", "container": "flac", "reason": "Calidad original sin transcodificacion. Respeta sample rate y bit depth."},
    "alac": {"codec": "alac", "bitrate": "original", "container": "m4a", "reason": "Apple Lossless para compatibilidad con dispositivos Apple."},
}


def explain_audio_format(db, track_ids: list[int] | None = None, **kwargs) -> ToolResult:
    if db is None:
        return ToolResult(name="explain_audio_format", success=True, data={"message": "No hay biblioteca cargada.", "format_info": None})
    track_id = (track_ids or [None])[0]
    if track_id is None:
        return ToolResult(name="explain_audio_format", success=True, data={"message": "Selecciona una pista para ver su informacion de formato.", "format_info": None})
    try:
        item = db.get_media_item_by_id(track_id) if hasattr(db, "get_media_item_by_id") else None
        if item is None:
            return ToolResult(name="explain_audio_format", success=True, data={"message": "Pista no encontrada en la biblioteca.", "format_info": None})
        info = _extract_format_info(item)
        return ToolResult(name="explain_audio_format", success=True, data={"message": _format_description(info), "format_info": info})
    except Exception as e:
        return ToolResult(name="explain_audio_format", success=False, error=str(e))


def recommend_conversion_profile(db, track_ids: list[int] | None = None, target: str = "mobile", priority: str = "balanced", **kwargs) -> ToolResult:
    if db is None or not track_ids:
        return ToolResult(name="recommend_conversion_profile", success=True, data={"target": target, "recommendation": None, "source_summary": None, "warnings": ["Selecciona una o mas pistas para recomendar un perfil."]})
    source_info = _gather_source_info(db, track_ids)
    profile = _select_profile(target, priority)
    if profile is None:
        return ToolResult(name="recommend_conversion_profile", success=True, data={"target": target, "recommendation": None, "source_summary": source_info, "warnings": [f"No hay perfil disponible para target='{target}'."]})
    return ToolResult(name="recommend_conversion_profile", success=True, data={"target": target, "recommendation": profile, "source_summary": source_info, "warnings": ["El archivo original no sera modificado.", "Esta es solo una recomendacion; la conversion requiere confirmacion."]})


def suggest_mobile_audio_profile(db, track_ids: list[int] | None = None, phone_storage_profile: str = "balanced", **kwargs) -> ToolResult:
    return recommend_conversion_profile(db, track_ids=track_ids, target="mobile", priority=phone_storage_profile)


def suggest_micro_server_streaming_profile(db, track_ids: list[int] | None = None, network_profile: str = "remote", **kwargs) -> ToolResult:
    return recommend_conversion_profile(db, track_ids=track_ids, target="micro_server", priority=network_profile)


def suggest_hifi_audio_profile(db, track_ids: list[int] | None = None, output_profile: str = "hifi", **kwargs) -> ToolResult:
    return recommend_conversion_profile(db, track_ids=track_ids, target="hifi", priority=output_profile)


def _extract_format_info(item) -> dict:
    return {"codec": getattr(item, "codec", None) or getattr(item, "container", "desconocido"), "container": getattr(item, "container", "desconocido"), "sample_rate": getattr(item, "sample_rate", 0), "bit_depth": getattr(item, "bit_depth", 0), "bitrate": getattr(item, "bitrate", 0), "channels": getattr(item, "channels", 0), "quality_category": _classify_quality(getattr(item, "sample_rate", 0), getattr(item, "bit_depth", 0))}


def _classify_quality(sample_rate: int, bit_depth: int) -> str:
    if bit_depth >= 24 and sample_rate >= 96000:
        return "hires"
    if bit_depth >= 16 and sample_rate >= 44100:
        return "lossless"
    return "lossy"


def _format_description(info: dict) -> str:
    if info is None:
        return "No disponible."
    parts = []
    codec = info.get("codec", "?")
    sr = info.get("sample_rate", 0)
    bd = info.get("bit_depth", 0)
    br = info.get("bitrate", 0)
    ch = info.get("channels", 0)
    qc = info.get("quality_category", "desconocida")
    parts.append(f"Codec: {codec}")
    if sr:
        parts.append(f"{sr} Hz")
    if bd:
        parts.append(f"{bd} bits")
    if br:
        parts.append(f"{br} bps")
    if ch:
        parts.append(f"{ch} canales")
    parts.append(f"Categoria: {qc}")
    return " . ".join(parts)


def _gather_source_info(db, track_ids: list[int]) -> dict:
    info = {"track_count": len(track_ids), "quality_categories": set(), "formats": set()}
    for tid in track_ids:
        try:
            item = db.get_media_item_by_id(tid) if hasattr(db, "get_media_item_by_id") else None
            if item:
                codec = getattr(item, "codec", None) or getattr(item, "container", "?")
                info["formats"].add(codec)
                sr = getattr(item, "sample_rate", 0)
                bd = getattr(item, "bit_depth", 0)
                info["quality_categories"].add(_classify_quality(sr, bd))
        except Exception:
            pass
    info["quality_categories"] = sorted(info["quality_categories"])
    info["formats"] = sorted(info["formats"])
    return info


_PROFILE_MAP = {"mobile": _MOBILE_PROFILES, "micro_server": _MICRO_SERVER_PROFILES, "hifi": _HIFI_PROFILES}


def _select_profile(target: str, priority: str) -> dict | None:
    profiles = _PROFILE_MAP.get(target)
    if profiles is None:
        return None
    return profiles.get(priority)
