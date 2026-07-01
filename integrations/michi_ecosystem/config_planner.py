"""Ecosystem configuration planner — create/preview/apply/rollback plans."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any

PLAN_DEFINITIONS: dict[str, dict[str, Any]] = {
    "setup_mobile_sync": {
        "title": "Configurar sincronizacion movil",
        "description": "Activa la sincronizacion y prepara el perfil para Michi Mobile.",
        "changes": [{"key": "home_audio/michi_api_enabled", "current": False, "proposed": True, "desc": "Activar API de Michi Link", "risk": "low"}],
        "tests": ["Verificar que Sync este activo"],
        "risks": ["Ninguno"],
    },
    "setup_micro_server_remote": {
        "title": "Configurar Micro Server remoto",
        "description": "Configura perfil de streaming liviano para conexion remota.",
        "changes": [{"key": "audio/profile", "current": "", "proposed": "streaming", "desc": "Perfil de streaming remoto", "risk": "low"}],
        "tests": ["Verificar conexion al Micro Server"],
        "risks": ["Ninguno"],
    },
    "setup_tailscale_streaming": {
        "title": "Configurar streaming por Tailscale",
        "description": "Optimiza la reproduccion remota via Tailscale con Opus 128-160k.",
        "changes": [{"key": "audio/profile", "current": "", "proposed": "streaming", "desc": "Perfil streaming para Tailscale", "risk": "low"}],
        "tests": ["Verificar conectividad Tailscale"],
        "risks": ["Ninguno"],
    },
    "setup_mobile_space_saver_profile": {
        "title": "Perfil de ahorro de espacio para Mobile",
        "description": "Configura perfil de conversion ligero para dispositivos con poco almacenamiento.",
        "changes": [{"key": "sync/mobile_profile", "current": "", "proposed": "space_saver", "desc": "Perfil mobile espacio reducido", "risk": "low"}],
        "tests": [],
        "risks": ["Ninguno"],
    },
    "setup_hifi_profile": {
        "title": "Configurar perfil Hi-Fi",
        "description": "Configura la salida bit-perfect para reproduccion Hi-Fi.",
        "changes": [{"key": "audio/profile", "current": "", "proposed": "hifi_pcm", "desc": "Perfil de salida Hi-Fi PCM", "risk": "low"}],
        "tests": [],
        "risks": ["Ninguno"],
    },
    "setup_home_audio": {
        "title": "Configurar Home Audio",
        "description": "Activa Home Audio con Home Assistant y Snapcast.",
        "changes": [
            {"key": "home_audio/enabled", "current": False, "proposed": True, "desc": "Activar Home Audio", "risk": "low"},
            {"key": "home_audio/michi_api_enabled", "current": False, "proposed": True, "desc": "Activar API de Michi", "risk": "low"},
        ],
        "tests": [],
        "risks": ["Ninguno"],
    },
}


@dataclass
class ConfigChange:
    key: str
    current_value: Any
    proposed_value: Any
    description: str
    risk: str = "low"
    requires_confirmation: bool = True


@dataclass
class ConfigPlan:
    plan_id: str
    title: str
    description: str
    changes: list[ConfigChange] = field(default_factory=list)
    tests: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    requires_confirmation: bool = True
    rollback_available: bool = True


class EcosystemConfigPlanner:
    def __init__(self, settings_manager=None):
        self._settings = settings_manager
        self._plans: dict[str, ConfigPlan] = {}

    def create_plan(self, plan_type: str, context: dict | None = None) -> ConfigPlan:
        definition = PLAN_DEFINITIONS.get(plan_type)
        if definition is None:
            raise ValueError(f"Unknown plan type: {plan_type}")
        changes = []
        for c in definition.get("changes", []):
            current = self._get_current_value(c["key"]) if self._settings is not None else c["current"]
            changes.append(ConfigChange(key=c["key"], current_value=current, proposed_value=c["proposed"], description=c["desc"], risk=c.get("risk", "low")))
        plan_id = str(uuid.uuid4())[:8]
        plan = ConfigPlan(plan_id=plan_id, title=definition["title"], description=definition["description"], changes=changes, tests=list(definition.get("tests", [])), risks=list(definition.get("risks", [])), requires_confirmation=True, rollback_available=True)
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
        return [{"type": k, "title": v["title"], "description": v["description"]} for k, v in PLAN_DEFINITIONS.items()]

    def _get_current_value(self, key: str) -> Any:
        if self._settings is None:
            return None
        try:
            if hasattr(self._settings, "get_str"):
                return self._settings.get_str(key, "")
            if hasattr(self._settings, "get_bool"):
                return self._settings.get_bool(key)
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
