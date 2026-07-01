"""ActionsHomeBuilder — builds HomeAction list."""

from __future__ import annotations

from core.home.home_status import HomeAction, LibraryHomeStatus, EcosystemHomeStatus


def build_actions(
    overall_state: str,
    library: LibraryHomeStatus,
    ecosystem: EcosystemHomeStatus,
) -> list[HomeAction]:
    actions: list[HomeAction] = []
    if overall_state == "empty_library":
        actions.append(HomeAction("Anadir carpeta", "library_hub", "folder", 10))
    if library.track_count > 0:
        actions.append(HomeAction("Ver biblioteca", "library_hub", "library", 5))
    if not library.is_healthy:
        actions.append(HomeAction("Diagnostico", "audio_lab_diagnostics", "diagnostics", 3))
    if ecosystem.micro_server_state == "unreachable":
        actions.append(HomeAction("Conectar servidor", "connections_hub", "server", 2))
    if not actions:
        actions.append(HomeAction("Explorar", "library_hub", "explore", 1))
    return actions
