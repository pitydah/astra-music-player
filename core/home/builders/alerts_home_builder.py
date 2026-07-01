"""AlertsHomeBuilder — builds HomeAlert list from statuses."""

from __future__ import annotations

import os
from typing import Any

from core.home.home_status import HomeAlert, LibraryHomeStatus, AudioHomeStatus, EcosystemHomeStatus


def build_alerts(
    library: LibraryHomeStatus,
    audio: AudioHomeStatus,
    ecosystem: EcosystemHomeStatus,
) -> list[HomeAlert]:
    alerts: list[HomeAlert] = []

    if library.index_error_count > 0:
        alerts.append(HomeAlert(severity="critical", kind="index_errors", title="Errores de indexacion", message=f"{library.index_error_count} archivos no pudieron ser indexados", count=library.index_error_count, target_route="audio_lab_diagnostics", action_label="Revisar"))

    if library.missing_file_count > 0:
        alerts.append(HomeAlert(severity="critical", kind="missing_files", title="Archivos faltantes", message=f"{library.missing_file_count} archivos no encontrados", count=library.missing_file_count, target_route="audio_lab_diagnostics", action_label="Revisar"))

    if library.missing_metadata_count > 50:
        alerts.append(HomeAlert(severity="warning", kind="metadata", title="Metadatos incompletos", message=f"{library.missing_metadata_count} canciones sin metadatos completos", count=library.missing_metadata_count, target_route="metadata_editor", action_label="Completar"))

    if library.missing_cover_count > 50:
        alerts.append(HomeAlert(severity="warning", kind="covers", title="Caratulas faltantes", message=f"{library.missing_cover_count} albumes sin caratula", count=library.missing_cover_count, target_route="audio_lab_artwork", action_label="Buscar"))

    if library.tracks_without_audio_features > 50:
        alerts.append(HomeAlert(severity="info", kind="audio_features", title="Analisis de audio pendiente", message=f"{library.tracks_without_audio_features} canciones sin perfil acustico", count=library.tracks_without_audio_features, target_route="audio_lab_intelligence", action_label="Analizar"))

    if audio.warnings:
        alerts.append(HomeAlert(severity="warning", kind="audio_output", title="Advertencias de audio", message=audio.warnings[0][:120], count=len(audio.warnings), target_route="audio_lab_output", action_label="Diagnostico"))

    if ecosystem.micro_server_state == "unreachable" and library.track_count > 0:
        alerts.append(HomeAlert(severity="info", kind="micro_server", title="Micro Server no conectado", message="Centraliza tu biblioteca con Michi Micro Server", target_route="connections_hub", action_label="Conectar"))

    if ecosystem.micro_server_state == "requires_pairing":
        alerts.append(HomeAlert(severity="warning", kind="micro_server", title="Micro Server requiere pairing", message="Acepta la solicitud de pairing en el servidor", target_route="connections_hub", action_label="Pairing"))

    if ecosystem.mobile_sync_state == "error":
        alerts.append(HomeAlert(severity="warning", kind="sync", title="Error de sincronizacion", message="La sincronizacion con dispositivos moviles fallo", target_route="devices_page", action_label="Ver"))

    safe_mode = os.environ.get("MICHI_SAFE_MODE") == "1"
    if safe_mode:
        alerts.insert(0, HomeAlert(severity="warning", kind="safe_mode", title="Modo seguro activo", message="Algunas funciones experimentales estan desactivadas", target_route="audio_lab_diagnostics", action_label="Ver diagnostico", dismissible=False))

    if len(alerts) > 5:
        extra = len(alerts) - 5
        alerts = alerts[:5]
        alerts.append(HomeAlert(severity="info", kind="playlists", title="Problemas adicionales", message=f"Hay {extra} problemas adicionales", count=extra))

    return alerts
