"""Audio conversion tools for Michi AI Assistant."""

from __future__ import annotations

from typing import Any

from integrations.ai_assistant.schemas import ToolResult


_MOBILE_PROFILES: dict[str, dict[str, Any]] = {
    "space_saver": {"codec": "opus", "bitrate": 128, "description": "Opus 128 kbps — espacio mínimo, calidad aceptable"},
    "balanced": {"codec": "opus", "bitrate": 160, "description": "Opus 160 kbps — equilibrio entre espacio y calidad"},
    "high_quality": {"codec": "opus", "bitrate": 256, "description": "Opus 256 kbps — buena calidad, tamaño moderado"},
}

_MICRO_SERVER_PROFILES: dict[str, dict[str, Any]] = {
    "remote": {"codec": "opus", "bitrate_range": "128-160", "description": "Opus 128-160 kbps — streaming remoto eficiente"},
    "lan": {"codec": "flac", "description": "FLAC original — sin pérdida en red local"},
    "balanced": {"codec": "opus", "bitrate": 192, "description": "Opus 192 kbps — buena calidad para red mixta"},
}

_HIFI_PROFILES: dict[str, dict[str, Any]] = {
    "hifi": {"codec": "flac", "description": "FLAC original — sin pérdida, calidad de estudio"},
    "alac": {"codec": "alac", "container": "m4a", "description": "ALAC (FLAC → M4A) — Apple Lossless"},
}


def explain_audio_format(format_name: str = "") -> ToolResult:
    try:
        info = _extract_format_info(format_name)
        if not info:
            return ToolResult(name="explain_audio_format", success=False, error=f"Formato '{format_name}' no reconocido.")
        return ToolResult(name="explain_audio_format", success=True, data=info)
    except Exception as e:
        return ToolResult(name="explain_audio_format", success=False, error=str(e))


def recommend_conversion_profile(source_format: str = "", target_format: str = "", quality_goal: str = "balanced") -> ToolResult:
    try:
        quality = _classify_quality(quality_goal)
        source_info = _gather_source_info(source_format)
        recommendations = _select_profile(source_info, quality)
        return ToolResult(name="recommend_conversion_profile", success=True, data=recommendations)
    except Exception as e:
        return ToolResult(name="recommend_conversion_profile", success=False, error=str(e))


def suggest_mobile_audio_profile(storage_priority: str = "balanced") -> ToolResult:
    try:
        profile = _MOBILE_PROFILES.get(storage_priority)
        if not profile:
            available = list(_MOBILE_PROFILES.keys())
            return ToolResult(name="suggest_mobile_audio_profile", success=False, error=f"Perfil '{storage_priority}' no valido. Opciones: {', '.join(available)}")
        result = {
            "profile": storage_priority,
            "codec": profile["codec"],
            "bitrate": profile.get("bitrate"),
            "description": profile["description"],
            "savings_estimate": "30-50% de ahorro frente a FLAC original" if storage_priority == "space_saver" else "10-25% de ahorro",
        }
        return ToolResult(name="suggest_mobile_audio_profile", success=True, data=result)
    except Exception as e:
        return ToolResult(name="suggest_mobile_audio_profile", success=False, error=str(e))


def suggest_micro_server_streaming_profile(network_type: str = "balanced") -> ToolResult:
    try:
        profile = _MICRO_SERVER_PROFILES.get(network_type)
        if not profile:
            available = list(_MICRO_SERVER_PROFILES.keys())
            return ToolResult(name="suggest_micro_server_streaming_profile", success=False, error=f"Perfil '{network_type}' no valido. Opciones: {', '.join(available)}")
        result = {
            "profile": network_type,
            "codec": profile["codec"],
            "bitrate": profile.get("bitrate"),
            "bitrate_range": profile.get("bitrate_range"),
            "description": profile["description"],
        }
        return ToolResult(name="suggest_micro_server_streaming_profile", success=True, data=result)
    except Exception as e:
        return ToolResult(name="suggest_micro_server_streaming_profile", success=False, error=str(e))


def suggest_hifi_audio_profile(output_format: str = "hifi") -> ToolResult:
    try:
        profile = _HIFI_PROFILES.get(output_format)
        if not profile:
            available = list(_HIFI_PROFILES.keys())
            return ToolResult(name="suggest_hifi_audio_profile", success=False, error=f"Perfil '{output_format}' no valido. Opciones: {', '.join(available)}")
        result = {
            "profile": output_format,
            "codec": profile["codec"],
            "container": profile.get("container"),
            "description": profile["description"],
            "note": "Requiere DAC externo o salida bit-perfect para aprovechar al maximo",
        }
        return ToolResult(name="suggest_hifi_audio_profile", success=True, data=result)
    except Exception as e:
        return ToolResult(name="suggest_hifi_audio_profile", success=False, error=str(e))


def _extract_format_info(format_name: str) -> dict[str, Any] | None:
    formats: dict[str, dict[str, Any]] = {
        "flac": {"name": "FLAC", "full_name": "Free Lossless Audio Codec", "lossless": True, "compression": "sin perdida", "use_case": "Archivo, audifilos, reproduccion local"},
        "alac": {"name": "ALAC", "full_name": "Apple Lossless Audio Codec", "lossless": True, "compression": "sin perdida", "use_case": "Ecosistema Apple, iTunes"},
        "opus": {"name": "Opus", "full_name": "Opus Interactive Audio Codec", "lossless": False, "compression": "con perdida", "use_case": "Streaming, llamadas, red"},
        "mp3": {"name": "MP3", "full_name": "MPEG Audio Layer III", "lossless": False, "compression": "con perdida", "use_case": "Compatibilidad universal, dispositivos antiguos"},
        "aac": {"name": "AAC", "full_name": "Advanced Audio Codec", "lossless": False, "compression": "con perdida", "use_case": "YouTube, iTunes, streaming moderno"},
        "wav": {"name": "WAV", "full_name": "Waveform Audio File Format", "lossless": True, "compression": "sin comprimir", "use_case": "Produccion, edicion, masterizacion"},
        "dsf": {"name": "DSF", "full_name": "DSD Stream File", "lossless": True, "compression": "sin perdida", "use_case": "Audio de alta resolucion, SACD"},
    }
    key = format_name.strip().lower()
    return formats.get(key)


def _classify_quality(quality_goal: str) -> str:
    goal = quality_goal.strip().lower()
    if goal in ("maximo", "maximum", "hifi", "lossless"):
        return "lossless"
    if goal in ("balance", "balanced", "medio", "medium"):
        return "balanced"
    return "compact"


def _format_description(profile: dict[str, Any]) -> str:
    parts = [f"Codec: {profile['codec']}"]
    if "bitrate" in profile:
        parts.append(f"Bitrate: {profile['bitrate']} kbps")
    if "bitrate_range" in profile:
        parts.append(f"Rango: {profile['bitrate_range']} kbps")
    if "description" in profile:
        parts.append(f"Descripcion: {profile['description']}")
    return " | ".join(parts)


def _gather_source_info(source_format: str) -> dict[str, Any]:
    info = _extract_format_info(source_format)
    if info:
        return info
    return {"name": source_format, "lossless": False, "compression": "desconocido"}


def _select_profile(source_info: dict[str, Any], quality: str) -> dict[str, Any]:
    if quality == "lossless":
        return {"recommendation": "flac", "reason": "Calidad sin perdida recomendada"}
    if quality == "balanced":
        return {"recommendation": "opus 192k", "reason": "Buen equilibrio entre calidad y tamano"}
    return {"recommendation": "opus 128k", "reason": "Tamano minimo, calidad aceptable"}
