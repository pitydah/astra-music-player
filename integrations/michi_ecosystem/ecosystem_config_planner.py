"""EcosystemConfigPlanner — create, preview, apply, and rollback config plans."""

from __future__ import annotations

import uuid
from typing import Any

from integrations.michi_ecosystem.ecosystem_models import ConfigChange, EcosystemConfigPlan

_PLAN_DEFINITIONS: dict[str, dict[str, Any]] = {
    "setup_mobile_sync": {
        "title": "Configurar sincronizacion movil",
        "description": "Activa la sincronizacion y prepara el perfil para Michi Mobile.",
        "changes": [ConfigChange(key="sync/enabled", current_value=False, proposed_value=True, description="Activar sincronizacion", risk="low")],
        "tests": ["Verificar que Sync este activo"],
        "risks": ["Ninguno"],
    },
    "setup_micro_server_remote": {
        "title": "Configurar Micro Server remoto",
        "description": "Configura perfil de streaming liviano para conexion remota con Tailscale.",
        "changes": [ConfigChange(key="michi_link/streaming_profile", current_value="", proposed_value="remote", description="Perfil de streaming remoto (Opus 128-160k)", risk="low")],
        "tests": ["Verificar conexion al Micro Server"],
        "risks": ["Ninguno"],
    },
    "setup_mobile_space_saver_profile": {
        "title": "Perfil de ahorro de espacio para Mobile",
        "description": "Configura perfil de conversion ligero para dispositivos con poco almacenamiento.",
        "changes": [ConfigChange(key="sync/mobile_profile", current_value="", proposed_value="space_saver", description="Perfil mobile espacio reducido (Opus 128k)", risk="low")],
        "tests": [],
        "risks": ["Ninguno"],
    },
    "setup_hifi_profile": {
        "title": "Configurar perfil Hi-Fi",
        "description": "Configura la salida de audio para reproduccion Hi-Fi sin transcodificacion.",
        "changes": [ConfigChange(key="audio/output_profile", current_value="", proposed_value="hifi_pcm", description="Perfil de salida Hi-Fi PCM", risk="low")],
        "tests": [],
        "risks": ["Ninguno"],
    },
    "setup_remote_light_streaming_profile": {
        "title": "Perfil de streaming ligero remoto",
        "description": "Configura Opus 128-160k para streaming remoto sin consumir ancho de banda.",
        "changes": [ConfigChange(key="michi_link/streaming_profile", current_value="", proposed_value="remote_light", description="Perfil remoto ligero (Opus 128k)", risk="low")],
        "tests": [],
        "risks": ["Ninguno"],
    },
}


class EcosystemConfigPlanner:
    def __init__(self, settings_manager=None):
        self._settings = settings_manager
        self._plans: dict[str, EcosystemConfigPlan] = {}

    def create_plan(self, plan_type: str, context: dict[str, Any] | None = None) -> EcosystemConfigPlan:
        definition = _PLAN_DEFINITIONS.get(plan_type)
        if definition is None:
            raise ValueError(f"Unknown plan type: {plan_type}")
        changes = []
        for c in definition["changes"]:
            current = self._get_current_value(c.key) if self._settings is not None else c.current_value
            changes.append(ConfigChange(key=c.key, current_value=current, proposed_value=c.proposed_value, description=c.description, risk=c.risk))
        plan_id = str(uuid.uuid4())[:8]
        plan = EcosystemConfigPlan(plan_id=plan_id, title=definition["title"], description=definition["description"], changes=changes, tests=list(definition["tests"]), risks=list(definition["risks"]), requires_confirmation=True, rollback_available=True)
        self._plans[plan_id] = plan
        return plan

    def preview_plan(self, plan_id: str) -> dict[str, Any]:
        plan = self._plans.get(plan_id)
        if plan is None:
            return {"error": f"Plan '{plan_id}' not found."}
        return {"plan_id": plan.plan_id, "title": plan.title, "description": plan.description, "changes": [{"key": c.key, "current_value": c.current_value, "proposed_value": c.proposed_value, "description": c.description, "risk": c.risk} for c in plan.changes], "tests": plan.tests, "risks": plan.risks}

    def apply_plan(self, plan_id: str, confirmed: bool = False) -> dict[str, Any]:
        if not confirmed:
            return {"success": False, "error": "Permiso denegado. Se requiere confirmacion explicita para aplicar este plan."}
        plan = self._plans.get(plan_id)
        if plan is None:
            return {"success": False, "error": f"Plan '{plan_id}' not found."}
        if self._settings is None:
            return {"success": False, "error": "No hay gestor de configuracion disponible."}
        applied = []
        errors = []
        for c in plan.changes:
            try:
                self._apply_change(c)
                applied.append(c.key)
            except Exception as e:
                errors.append({"key": c.key, "error": str(e)})
        return {"success": not errors, "status": "ok" if not errors else "partial", "applied": applied, "errors": errors}

    def rollback_plan(self, plan_id: str, confirmed: bool = False) -> dict[str, Any]:
        if not confirmed:
            return {"success": False, "error": "Permiso denegado. Se requiere confirmacion explicita para revertir este plan."}
        plan = self._plans.get(plan_id)
        if plan is None:
            return {"success": False, "error": f"Plan '{plan_id}' not found."}
        if self._settings is None:
            return {"success": False, "error": "No hay gestor de configuracion disponible."}
        rolled_back = []
        errors = []
        for c in plan.changes:
            try:
                self._rollback_change(c)
                rolled_back.append(c.key)
            except Exception as e:
                errors.append({"key": c.key, "error": str(e)})
        return {"success": not errors, "rolled_back": rolled_back, "errors": errors}

    def list_plan_types(self) -> list[dict[str, str]]:
        return [{"type": k, "title": v["title"], "description": v["description"]} for k, v in _PLAN_DEFINITIONS.items()]

    def _get_current_value(self, key: str) -> Any:
        if self._settings is None:
            return None
        try:
            if hasattr(self._settings, "get_str"):
                return self._settings.get_str(key, "")
            if hasattr(self._settings, "get"):
                return self._settings.get(key)
        except Exception:
            pass
        return None

    def _apply_change(self, change: ConfigChange) -> None:
        if self._settings is None:
            raise RuntimeError("No settings manager")
        if hasattr(self._settings, "set_str"):
            self._settings.set_str(change.key, str(change.proposed_value))

    def _rollback_change(self, change: ConfigChange) -> None:
        if self._settings is None:
            raise RuntimeError("No settings manager")
        if hasattr(self._settings, "set_str"):
            self._settings.set_str(change.key, str(change.current_value))
