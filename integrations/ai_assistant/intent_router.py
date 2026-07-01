"""IntentRouter — hybrid rule-based + optional Ollama intent detection."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class IntentResult:
    tool_name: str | None
    args: dict[str, Any]
    query_text: str
    confidence: float
    source: str
    requires_confirmation: bool = False


_MIN_CONFIDENCE = 0.6

_ECO_QUERIES: dict[str, str] = {
    "mobile": "diagnose_mobile_sync",
    "micro server": "diagnose_micro_server",
    "big server": "diagnose_big_server",
    "ecosistema": "diagnose_ecosystem",
    "home audio": "diagnose_home_audio",
    "tailscale": "diagnose_tailscale_route",
    "emparejam": "diagnose_pairing",
    "pairing": "diagnose_pairing",
    "plan de configur": "create_ecosystem_config_plan",
    "configuraci": "create_ecosystem_config_plan",
}

_CONVERSION_QUERIES: dict[str, str] = {
    "formato": "explain_audio_format",
    "calidad": "explain_audio_format",
    "convertir": "recommend_conversion_profile",
    "conversi": "recommend_conversion_profile",
    "mobile": "suggest_mobile_audio_profile",
    "telefono": "suggest_mobile_audio_profile",
    "teléfono": "suggest_mobile_audio_profile",
    "micro server": "suggest_micro_server_streaming_profile",
    "streaming": "suggest_micro_server_streaming_profile",
    "hifi": "suggest_hifi_audio_profile",
    "hi fi": "suggest_hifi_audio_profile",
}

_LIBRARY_QUERIES: dict[str, str] = {
    "biblioteca": "search_library",
    "buscar": "search_library",
    "busqueda": "search_library",
    "búsqueda": "search_library",
    "metadatos": "find_metadata_gaps",
    "metadata": "find_metadata_gaps",
    "caratula": "find_metadata_gaps",
    "carátula": "find_metadata_gaps",
    "playlist": "draft_playlist",
    "recomiend": "recommend_music",
    "recomend": "recommend_music",
    "musica": "recommend_music",
    "música": "recommend_music",
    "mix": "create_smart_mix",
}

_ACTION_MAPPING: list[tuple[re.Pattern, str]] = [
    (re.compile(r"\b(diagnosticar|diagnostica|revisa|revisar|chequear)\b.*\b(todo|ecosistema|general|completo)\b", re.IGNORECASE), "diagnose_ecosystem"),
    (re.compile(r"\b(diagnosticar|diagnostica|revisar|revisa)\b.*\b(mobile|sync|sincronizacion|android)\b", re.IGNORECASE), "diagnose_mobile_sync"),
    (re.compile(r"\b(diagnosticar|diagnostica|revisar|revisa)\b.*\b(micro.?server|servidor|remoto)\b", re.IGNORECASE), "diagnose_micro_server"),
    (re.compile(r"\b(mobile|telefono|teléfono)\b.*\b(espacio|poco|ahorro|liviano)\b", re.IGNORECASE), "suggest_mobile_audio_profile"),
    (re.compile(r"\b(micro.?server|servidor)\b.*\b(streaming|remoto|perfil)\b", re.IGNORECASE), "suggest_micro_server_streaming_profile"),
    (re.compile(r"\b(hifi|hi.?fi|alta calidad)\b.*\b(perfil|audio|salida)\b", re.IGNORECASE), "suggest_hifi_audio_profile"),
    (re.compile(r"\b(crear|hacer|generar)\b.*\b(plan|configuracion)\b", re.IGNORECASE), "create_ecosystem_config_plan"),
    (re.compile(r"\b(aplica|aplicar|ejecutar|confirmar)\b.*\b(plan|configuracion)\b", re.IGNORECASE), "apply_ecosystem_config_plan"),
    (re.compile(r"\b(explica|explicar|que es|qué es)\b.*\b(formato|calidad|codec)\b", re.IGNORECASE), "explain_audio_format"),
    (re.compile(r"\b(recomienda|recomendar|sugerir)\b.*\b(conversion|convertir|perfil)\b", re.IGNORECASE), "recommend_conversion_profile"),
    (re.compile(r"\b(analizar|analiza)\b.*\b(audio|acustico|acústico)\b", re.IGNORECASE), "analyze_track_audio"),
    (re.compile(r"\b(crear|hacer|generar)\b.*\b(mix|mezcla)\b", re.IGNORECASE), "create_smart_mix"),
    (re.compile(r"\b(crear|hacer|generar)\b.*\b(playlist|lista)\b", re.IGNORECASE), "draft_playlist"),
    (re.compile(r"\b(buscar|busca|encuentra)\b.*\b(musica|cancion|canciones|artista|album|álbum)\b", re.IGNORECASE), "search_library"),
    (re.compile(r"\b(metadatos|metadata|completar)\b", re.IGNORECASE), "find_metadata_gaps"),
]


class IntentRouter:
    def __init__(self):
        self._ollama_client = None

    def set_ollama_client(self, client):
        self._ollama_client = client

    def detect(self, text: str, section_snapshot: dict | None = None, allowed_actions: list[str] | None = None) -> IntentResult:
        text_lower = text.strip().lower()
        if not text_lower:
            return self._fallback_result(text)
        section = (section_snapshot or {}).get("section", "")
        allowed = allowed_actions or []
        tool, args, confidence = self._match_rules(text_lower, section)
        if tool and confidence >= _MIN_CONFIDENCE:
            if tool in allowed or not allowed:
                return IntentResult(tool_name=tool, args=args, query_text=text, confidence=confidence, source="rules", requires_confirmation=self._requires_confirm(tool))
            return IntentResult(tool_name=None, args={}, query_text=text, confidence=0.0, source="fallback")
        if self._ollama_client is not None:
            try:
                return self._detect_via_ollama(text, section, allowed)
            except Exception:
                pass
        return self._fallback_result(text)

    def _match_rules(self, text: str, section: str):
        for pattern, tool in _ACTION_MAPPING:
            if pattern.search(text):
                return tool, self._infer_args(text, tool), 0.85
        if section in ("connections_hub", "devices"):
            for keyword, tool in _ECO_QUERIES.items():
                if keyword in text:
                    return tool, self._infer_args(text, tool), 0.80
        elif section == "audio_lab":
            for keyword, tool in _CONVERSION_QUERIES.items():
                if keyword in text:
                    return tool, self._infer_args(text, tool), 0.80
        elif section == "library_hub":
            for keyword, tool in _LIBRARY_QUERIES.items():
                if keyword in text:
                    return tool, self._infer_args(text, tool), 0.80
        return None, {}, 0.0

    def _infer_args(self, text: str, tool: str):
        args = {}
        plan_match = re.search(r"\b(reducido|space.?saver|ahorro)\b", text, re.IGNORECASE)
        if plan_match and "profile" in tool:
            args["phone_storage_profile"] = "space_saver"
        hifi_match = re.search(r"\b(hifi|hi.?fi)\b", text, re.IGNORECASE)
        if hifi_match and "profile" in tool:
            args["output_profile"] = "hifi"
        return args

    def _requires_confirm(self, tool: str):
        return tool in {"apply_ecosystem_config_plan", "rollback_ecosystem_config_plan", "draft_playlist", "create_playlist_from_draft", "add_tracks_to_queue"}

    def _detect_via_ollama(self, text: str, section: str, allowed: list[str]):
        try:
            if self._ollama_client and hasattr(self._ollama_client, "check_health") and not self._ollama_client.check_health():
                return self._fallback_result(text)
            return self._fallback_result(text)
        except Exception:
            return self._fallback_result(text)

    def _fallback_result(self, text: str):
        return IntentResult(tool_name=None, args={}, query_text=text, confidence=0.0, source="fallback")
