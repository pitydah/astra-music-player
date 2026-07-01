"""AudioHomeBuilder — builds AudioHomeStatus."""

from __future__ import annotations

import logging
from typing import Any

from core.home.home_status import AudioHomeStatus

logger = logging.getLogger("michi.home.builders.audio")


def build_audio_status(
    player_engine: Any = None,
    playback: Any = None,
) -> AudioHomeStatus:
    output_device = ""
    output_profile = ""
    replaygain_enabled = False
    eq_enabled = False
    dsp_active = False
    bitperfect_state = "not_available"
    warnings_list: list[str] = []

    try:
        from core.settings_manager import get_str, get_bool
        output_profile = get_str("audio/profile") or ""
        replaygain_enabled = get_bool("audio/replaygain_enabled")
    except Exception:
        pass

    if player_engine is not None:
        try:
            eng = player_engine
            if hasattr(eng, "dsp_state") and eng.dsp_state is not None:
                dsp = eng.dsp_state
                eq_enabled = getattr(dsp, "eq_enabled", False)
                dsp_active = getattr(dsp, "is_dsp_active", lambda: False)()
                replaygain_enabled = replaygain_enabled or getattr(dsp, "replaygain_enabled", False)
            if hasattr(eng, "current_format"):
                fmt = eng.current_format
                if fmt:
                    bitperfect_state = "not_verified"
                    if "bitperfect" in output_profile.lower():
                        bitperfect_state = "verified"
        except Exception:
            pass

    if playback is not None:
        try:
            if hasattr(playback, "get_output_device_id"):
                oid = playback.get_output_device_id()
                if oid:
                    output_device = str(oid)
            if hasattr(playback, "get_audio_diagnostics"):
                diag = playback.get_audio_diagnostics()
                if isinstance(diag, dict) and diag.get("warnings"):
                    warnings_list = diag["warnings"]
        except Exception:
            pass

    if not output_device:
        output_device = "Predeterminado"

    return AudioHomeStatus(
        output_device=output_device,
        output_profile=output_profile,
        replaygain_enabled=replaygain_enabled,
        eq_enabled=eq_enabled,
        dsp_active=dsp_active,
        bitperfect_state=bitperfect_state,
        warnings=warnings_list,
    )
