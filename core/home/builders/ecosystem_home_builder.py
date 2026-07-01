"""EcosystemHomeBuilder — builds EcosystemHomeStatus using Michi Link services."""

from __future__ import annotations

import logging
from typing import Any

from core.home.home_status import EcosystemHomeStatus

logger = logging.getLogger("michi.home.builders.ecosystem")


def build_ecosystem_status(
    sync_mgr: Any = None,
    ecosystem_doctor: Any = None,
) -> EcosystemHomeStatus:
    micro_state = "not_configured"
    micro_name = ""
    micro_issue_code = ""
    micro_host = ""
    remote_music_state = "not_configured"
    remote_music_count = 0
    remote_music_name = ""
    sync_state = "no_device"
    sync_count = 0
    api_state = "unknown"
    ha_state = "disabled"
    last_sync = None
    diag_avail = False

    try:
        from core.settings_manager import get_str
        micro_host = get_str("michi_link/micro_host", "")
        micro_port = 53318
        if micro_host:
            micro_state = "unreachable"
            micro_name = f"{micro_host}:{micro_port}"
    except Exception:
        pass

    try:
        from streaming.subsonic_client import load_servers
        servers = load_servers()
        if servers:
            remote_music_state = "configured"
            remote_music_count = len(servers)
            srv = servers[0]
            remote_music_name = getattr(srv, "name", "") or getattr(srv, "server_type", "Servidor")
    except Exception:
        pass

    if ecosystem_doctor is not None:
        try:
            diag = ecosystem_doctor.diagnose_micro_server(host=micro_host)
            if diag:
                micro_state = diag.get("state", micro_state)
                micro_issue_code = diag.get("issue_code", micro_issue_code)
        except Exception:
            pass

    if sync_mgr is not None:
        try:
            peers = sync_mgr.get_all_peers() if hasattr(sync_mgr, "get_all_peers") else []
            if peers:
                sync_state = "paired"
                sync_count = len(peers)
                if hasattr(sync_mgr, "is_syncing") and sync_mgr.is_syncing():
                    sync_state = "syncing"
            if hasattr(sync_mgr, "last_sync"):
                ls = sync_mgr.last_sync
                if ls:
                    last_sync = str(ls)
        except Exception:
            sync_state = "error"

    try:
        from core.settings_manager import get_bool
        api_state = "active" if get_bool("home_audio/michi_api_enabled") else "disabled"
        if get_bool("home_audio/ha_base_url"):
            ha_state = "configured"
        if get_bool("home_audio/enabled"):
            ha_state = "active" if ha_state == "configured" else ha_state
    except Exception:
        pass

    diag_avail = bool(micro_host or sync_count > 0 or api_state == "active")

    return EcosystemHomeStatus(
        micro_server_state=micro_state,
        micro_server_name=micro_name,
        micro_server_issue_code=micro_issue_code,
        remote_music_server_state=remote_music_state,
        remote_music_server_count=remote_music_count,
        remote_music_server_name=remote_music_name,
        mobile_sync_state=sync_state,
        mobile_device_count=sync_count,
        api_state=api_state,
        home_audio_state=ha_state,
        last_sync=last_sync,
        diagnostics_available=diag_avail,
    )
