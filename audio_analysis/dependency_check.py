"""Dependency check — detects available audio analysis backends."""

from __future__ import annotations

import importlib.util as _util


def check_dependencies() -> dict:
    result = {
        "available": False,
        "backend": "disabled",
        "missing": [],
        "message": "",
    }

    has_numpy = _util.find_spec("numpy") is not None
    if not has_numpy:
        result["missing"].append("numpy")

    has_librosa = _util.find_spec("librosa") is not None
    if not has_librosa:
        result["missing"].append("librosa")

    has_soundfile = _util.find_spec("soundfile") is not None
    if not has_soundfile:
        result["missing"].append("soundfile")

    if has_librosa and has_soundfile:
        result["available"] = True
        result["backend"] = "librosa"
        result["message"] = "librosa disponible. Analisis acustico completo habilitado."
    elif has_numpy:
        result["available"] = True
        result["backend"] = "basic"
        result["message"] = (
            "Solo numpy disponible. Analisis basico desde tags y heuristica. "
            "Instala librosa y soundfile para analisis acustico completo."
        )
    else:
        result["message"] = "Analisis acustico no disponible. Instala numpy, librosa y soundfile."

    return result
