"""EcosystemRegistry — aggregate view of all Michi ecosystem services."""

from __future__ import annotations


from integrations.michi_ecosystem.ecosystem_models import EcosystemService


class EcosystemRegistry:
    def __init__(self, device_registry=None, sync_manager=None, settings_manager=None):
        self._device_registry = device_registry
        self._sync = sync_manager
        self._settings = settings_manager
        self._additional_services: list[EcosystemService] = []

    def register_service(self, service: EcosystemService) -> None:
        existing = [s for s in self._additional_services if s.id == service.id]
        if existing:
            self._additional_services.remove(existing[0])
        self._additional_services.append(service)

    def list_services(self) -> list[EcosystemService]:
        services = list(self._additional_services)
        services.append(self._build_player_service())
        services.extend(self._build_device_services())
        services.extend(self._build_micro_server_services())
        return services

    def get_service(self, service_id: str) -> EcosystemService | None:
        for s in self.list_services():
            if s.id == service_id:
                return s
        return None

    def list_mobile_devices(self) -> list[EcosystemService]:
        return [s for s in self.list_services() if s.type == "mobile"]

    def list_micro_servers(self) -> list[EcosystemService]:
        return [s for s in self.list_services() if s.type == "micro_server"]

    def list_stream_receivers(self) -> list[EcosystemService]:
        return [s for s in self.list_services() if s.type == "stream_receiver"]

    def list_home_audio_endpoints(self) -> list[EcosystemService]:
        return [s for s in self.list_services() if s.type == "home_audio"]

    def count(self) -> int:
        return len(self.list_services())

    def _build_player_service(self) -> EcosystemService:
        return EcosystemService(id="player", name="Michi Music Player", type="player", protocol="local", status="ok", paired=True, capabilities={"version": "0.1.0-alpha"})

    def _build_device_services(self) -> list[EcosystemService]:
        if self._device_registry is None:
            return []
        services = []
        try:
            if hasattr(self._device_registry, "list_all"):
                for d in self._device_registry.list_all():
                    services.append(EcosystemService(id=f"device:{getattr(d, 'device_id', '')}", name=getattr(d, "name", "Unknown"), type="mobile", host=getattr(d, "host", ""), port=getattr(d, "port", 53318), protocol="michi_link", paired=getattr(d, "status", "") == "paired", status=getattr(d, "status", "unknown")))
        except Exception:
            pass
        return services

    def _build_micro_server_services(self) -> list[EcosystemService]:
        if self._settings is None:
            return []
        services = []
        try:
            host = self._settings.get_str("michi_link/micro_host", "") if hasattr(self._settings, "get_str") else ""
            port = self._settings.get_int("michi_link/micro_port", 53318) if hasattr(self._settings, "get_int") else 53318
            if host:
                services.append(EcosystemService(id="micro_server", name="Michi Micro Server", type="micro_server", host=host, port=port, protocol="michi_link", status="unknown"))
        except Exception:
            pass
        return services
