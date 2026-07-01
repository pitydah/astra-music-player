"""Ecosystem fix suggester — map issue codes to human-readable solutions."""

from __future__ import annotations

from typing import Any

ISSUE_FIXES: dict[str, dict[str, Any]] = {
    "MICRO_NOT_CONFIGURED": {
        "problem": "Michi Micro Server no configurado.",
        "probable_cause": "No se ha configurado la direccion del Micro Server.",
        "recommended_fix": "Configura el host del Micro Server en Conexiones.",
        "manual_steps": ["Abre Conexiones.", "Configura la IP/puerto del Micro Server.", "Inicia el emparejamiento."],
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
    "MICRO_REQUIRES_PAIRING": {
        "problem": "Michi Micro Server requiere emparejamiento.",
        "probable_cause": "El Micro Server esta en linea pero requiere aceptar el pairing.",
        "recommended_fix": "Acepta la solicitud de pairing en el Micro Server o inicia el emparejamiento desde Conexiones.",
        "manual_steps": ["Abre Conexiones.", "Selecciona 'Emparejar dispositivo'.", "Sigue las instrucciones en pantalla."],
        "automatic_actions": [{"action": "open_section", "args": {"target": "connections_hub"}, "requires_confirmation": False}],
        "risk": "low",
    },
    "MICRO_CONTRACT_MISMATCH": {
        "problem": "Incompatibilidad de contrato entre Player y Micro Server.",
        "probable_cause": "Las versiones del Player y Micro Server no son completamente compatibles.",
        "recommended_fix": "Actualiza ambos componentes a la version mas reciente.",
        "manual_steps": ["Ejecuta 'Diagnosticar contrato' en Conexiones.", "Revisa las versiones.", "Actualiza segun sea necesario."],
        "automatic_actions": [{"action": "diagnose_micro_contract", "args": {}, "requires_confirmation": False}],
        "risk": "medium",
    },
    "SYNC_STOPPED": {
        "problem": "La sincronizacion esta detenida.",
        "probable_cause": "El servidor de sincronizacion no se ha iniciado o se detuvo.",
        "recommended_fix": "Reinicia la sincronizacion desde el panel de Conexiones.",
        "manual_steps": ["Abre Conexiones.", "Activa el interruptor de sincronizacion."],
        "automatic_actions": [{"action": "open_section", "args": {"target": "connections_hub"}, "requires_confirmation": False}],
        "risk": "low",
    },
    "NO_PAIRED_DEVICES": {
        "problem": "No hay dispositivos emparejados.",
        "probable_cause": "Ningun dispositivo Michi Mobile se ha conectado aun.",
        "recommended_fix": "Abre Michi Sync Suite e inicia el emparejamiento desde un dispositivo movil.",
        "manual_steps": ["Abre Conexiones en Michi Music Player.", "Activa la sincronizacion.", "Desde Michi Mobile, inicia el emparejamiento.", "Confirma el codigo en ambos dispositivos."],
        "automatic_actions": [{"action": "open_section", "args": {"target": "connections_hub"}, "requires_confirmation": False}],
        "risk": "low",
    },
    "MOBILE_PAIRING_REQUIRED": {
        "problem": "Emparejamiento con dispositivo movil requerido.",
        "probable_cause": "El dispositivo movil no esta emparejado o el token ha expirado.",
        "recommended_fix": "Reinicia el emparejamiento desde el movil.",
        "manual_steps": ["Abre Michi Mobile.", "Inicia el emparejamiento.", "Confirma el codigo en el Player."],
        "automatic_actions": [{"action": "open_section", "args": {"target": "devices"}, "requires_confirmation": False}],
        "risk": "low",
    },
    "HOME_AUDIO_DISABLED": {
        "problem": "Home Audio no esta configurado.",
        "probable_cause": "No se ha configurado Home Assistant o Snapcast.",
        "recommended_fix": "Configura Home Audio desde el panel correspondiente.",
        "manual_steps": ["Abre Home Audio.", "Configura Home Assistant.", "Configura Snapcast si aplica."],
        "automatic_actions": [{"action": "open_section", "args": {"target": "home_audio"}, "requires_confirmation": False}],
        "risk": "low",
    },
    "MICHILINK_API_DISABLED": {
        "problem": "API de Michi Link desactivada.",
        "probable_cause": "La API REST de Michi Link no esta habilitada en configuracion.",
        "recommended_fix": "Activa la API de Michi Link en las preferencias de Home Audio.",
        "manual_steps": ["Abre Configuracion > Home Audio.", "Activa 'Michi API'."],
        "automatic_actions": [{"action": "create_ecosystem_config_plan", "args": {"plan_type": "setup_mobile_sync"}, "requires_confirmation": True}],
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


def suggest_fix(report: dict[str, Any]) -> dict[str, Any]:
    issue_codes = _collect_issue_codes(report)
    if not issue_codes:
        return {"problem": "No se detectaron problemas.", "probable_cause": "Todos los servicios del ecosistema responden correctamente.", "recommended_fix": "No se requiere ninguna accion.", "manual_steps": [], "automatic_actions": [], "risk": "none"}
    return ISSUE_FIXES.get(issue_codes[0], _DEFAULT_FIX)


def suggest_next_steps(issue_code: str, context: dict | None = None) -> dict[str, Any]:
    return ISSUE_FIXES.get(issue_code, _DEFAULT_FIX)


def _collect_issue_codes(report: dict[str, Any]) -> list[str]:
    codes = []
    for _key, diag in report.items():
        if isinstance(diag, dict):
            code = diag.get("issue_code", "")
            if code:
                codes.append(code)
    return codes
