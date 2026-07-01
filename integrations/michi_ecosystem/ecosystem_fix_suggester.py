"""EcosystemFixSuggester — suggest fixes for ecosystem issues."""

from __future__ import annotations

from typing import Any

_ISSUE_FIXES: dict[str, dict[str, Any]] = {
    "NO_PAIRED_DEVICES": {
        "problem": "No hay dispositivos emparejados.",
        "probable_cause": "Ningun dispositivo Michi Mobile se ha conectado aun.",
        "recommended_fix": "Abre Michi Sync Suite e inicia el emparejamiento desde un dispositivo movil.",
        "manual_steps": ["Abre Conexiones en Michi Music Player.", "Activa la sincronizacion.", "Desde Michi Mobile, inicia el emparejamiento.", "Confirma el codigo en ambos dispositivos."],
        "automatic_actions": [{"action": "open_section", "args": {"target": "connections_hub"}, "requires_confirmation": False}],
        "risk": "low",
    },
    "SYNC_STOPPED": {
        "problem": "La sincronizacion esta detenida.",
        "probable_cause": "El servidor de sincronizacion no se ha iniciado o se detuvo.",
        "recommended_fix": "Reinicia la sincronizacion desde el panel de Conexiones.",
        "manual_steps": ["Abre Conexiones.", "Activa el interruptor de sincronizacion."],
        "automatic_actions": [{"action": "open_section", "args": {"target": "connections_hub"}, "requires_confirmation": False}],
        "risk": "low",
    },
    "MICRO_UNREACHABLE": {
        "problem": "Michi Micro Server no responde.",
        "probable_cause": "El servicio esta detenido, la IP/puerto configurado no responde, o Tailscale no esta activo.",
        "recommended_fix": "Verifica que el Micro Server este encendido y que el host/puerto sean correctos.",
        "manual_steps": ["Abre Conexiones.", "Revisa el host configurado.", "Prueba el emparejamiento nuevamente.", "Verifica que Tailscale este activo si usas conexion remota."],
        "automatic_actions": [{"action": "open_section", "args": {"target": "connections_hub"}, "requires_confirmation": False}],
        "risk": "low",
    },
    "PAIRING_REQUIRED": {
        "problem": "Se requiere emparejamiento.",
        "probable_cause": "El dispositivo no esta emparejado o el token ha expirado.",
        "recommended_fix": "Inicia el emparejamiento desde las Conexiones.",
        "manual_steps": ["Abre Conexiones.", "Selecciona 'Emparejar dispositivo'."],
        "automatic_actions": [{"action": "open_section", "args": {"target": "connections_hub"}, "requires_confirmation": False}],
        "risk": "low",
    },
}

_DEFAULT_FIX: dict[str, Any] = {
    "problem": "Problema desconocido.",
    "probable_cause": "No se pudo determinar la causa automaticamente.",
    "recommended_fix": "Ejecuta un diagnostico completo del ecosistema para mas detalles.",
    "manual_steps": ["Abre Conexiones.", "Ejecuta 'Diagnosticar ecosistema'.", "Revisa los resultados."],
    "automatic_actions": [{"action": "diagnose_ecosystem", "args": {}, "requires_confirmation": False}],
    "risk": "low",
}


class EcosystemFixSuggester:
    def __init__(self):
        pass

    def suggest_fix(self, report: dict[str, Any]) -> dict[str, Any]:
        issue_codes = self._collect_issue_codes(report)
        if not issue_codes:
            return {"problem": "No se detectaron problemas.", "probable_cause": "Todos los servicios del ecosistema responden correctamente.", "recommended_fix": "No se requiere ninguna accion.", "manual_steps": [], "automatic_actions": [], "risk": "none"}
        primary = issue_codes[0]
        return _ISSUE_FIXES.get(primary, _DEFAULT_FIX)

    def suggest_next_steps(self, issue_code: str, context: dict | None = None) -> dict[str, Any]:
        return _ISSUE_FIXES.get(issue_code, _DEFAULT_FIX)

    def _collect_issue_codes(self, report: dict[str, Any]) -> list[str]:
        codes = []
        for _key, diag in report.items():
            if isinstance(diag, dict):
                code = diag.get("issue_code", "")
                if code:
                    codes.append(code)
        return codes
