"""Section context provider for connections section."""

from __future__ import annotations

from typing import Any

from core.context.section_context_provider import SectionContextProvider


class ConnectionsContextProvider(SectionContextProvider):
    section_key = "connections_hub"

    def __init__(self, db=None, sync_manager=None, device_registry=None):
        self._db = db
        self._sync = sync_manager
        self._device_registry = device_registry

    def get_context(self) -> dict[str, Any]:
        return _build_connections_context(self._sync, self._device_registry)

    def get_suggestions(self) -> list[dict[str, Any]]:
        return _connections_suggestions(self._sync, self._device_registry)

    def get_allowed_actions(self) -> list[str]:
        return [
            "diagnose_ecosystem",
            "diagnose_mobile_sync",
            "diagnose_micro_server",
            "diagnose_home_audio",
            "create_ecosystem_config_plan",
            "open_section",
        ]


def _build_connections_context(sync, device_registry) -> dict[str, Any]:
    ctx: dict[str, Any] = {
        "section": "connections_hub",
        "sync_active": False,
        "paired_devices": 0,
        "micro_server_configured": False,
        "home_audio_configured": False,
    }
    if sync is not None:
        try:
            if hasattr(sync, "isRunning"):
                ctx["sync_active"] = sync.isRunning()
            elif hasattr(sync, "is_active"):
                ctx["sync_active"] = sync.is_active
        except Exception:
            pass
    if device_registry is not None:
        try:
            devices = device_registry.list_all() if hasattr(device_registry, "list_all") else []
            ctx["paired_devices"] = len(devices)
        except Exception:
            pass
    return ctx


def _connections_suggestions(sync, device_registry) -> list[dict[str, Any]]:
    suggestions = []
    ctx = _build_connections_context(sync, device_registry)
    if not ctx.get("sync_active"):
        suggestions.append({
            "id": "connections_sync_disabled",
            "title": "Activar Sync",
            "description": "La sincronizacion no esta activa. Activala para conectar dispositivos.",
            "section": "connections_hub",
            "action": "diagnose_mobile_sync",
            "args": {},
            "priority": "medium",
            "requires_confirmation": False,
            "reason": "sync_active=False",
        })
    if ctx.get("paired_devices", 0) == 0:
        suggestions.append({
            "id": "connections_no_devices",
            "title": "Emparejar dispositivo",
            "description": "No hay dispositivos emparejados. Conecta Michi Mobile.",
            "section": "connections_hub",
            "action": "diagnose_ecosystem",
            "args": {},
            "priority": "medium",
            "requires_confirmation": False,
            "reason": "paired_devices=0",
        })
    suggestions.append({
        "id": "connections_diagnose",
        "title": "Diagnosticar ecosistema",
        "description": "Revisa el estado de todos los servicios Michi.",
        "section": "connections_hub",
        "action": "diagnose_ecosystem",
        "args": {},
        "priority": "low",
        "requires_confirmation": False,
        "reason": "",
    })
    return suggestions[:5]
