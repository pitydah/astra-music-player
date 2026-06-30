"""Contract tests for Audio Lab — structural integrity, safety, and honesty."""

from __future__ import annotations

import os


class TestAudioLabContract:

    def test_hub_has_exactly_five_main_sections(self):
        from ui.audio_lab.audio_lab_page import _SECTIONS
        assert len(_SECTIONS) == 5

    def test_no_section_marked_disponible_if_incomplete(self):
        from ui.audio_lab.audio_lab_page import _SECTIONS
        for sec in _SECTIONS:
            if sec["key"] in ("audio_lab_output", "audio_lab_diagnostics",
                              "audio_lab_intelligence"):
                assert sec["status"] in (
                    "proximamente", "experimental", "no_disponible"
                ), f"{sec['key']} should not be marked disponible"

    def test_michi_disc_lab_only_wav_available(self):
        from ui.audio_lab.models import RIP_PROFILES
        for p in RIP_PROFILES:
            if p.available:
                assert p.fmt == "wav", "Only WAV should be available"

    def test_no_orphan_routes(self):
        from ui.controllers.navigation_controller import NAV_ROUTES
        import ui.window

        missing = []
        for key, method_name in NAV_ROUTES.items():
            if not hasattr(ui.window.MainWindow, method_name):
                missing.append(f"{key} → {method_name}")
        assert not missing, f"Orphan routes: {'; '.join(missing)}"

    def test_all_audio_lab_routes_grouped_under_sidebar(self):
        from ui.controllers.navigation_controller import (
            NAV_ROUTES, resolve_sidebar_active_key,
        )
        for key in NAV_ROUTES:
            if key.startswith("audio_lab") or key == "michi_disc_lab":
                assert resolve_sidebar_active_key(key) == "audio_lab", (
                    f"{key} not grouped under audio_lab sidebar"
                )

    def test_no_import_of_context_repository(self):
        audio_lab_dir = os.path.join(
            os.path.dirname(__file__), "..", "ui", "audio_lab"
        )
        for root, _dirs, files in os.walk(os.path.abspath(audio_lab_dir)):
            for f in files:
                if f.endswith(".py"):
                    with open(os.path.join(root, f)) as fh:
                        content = fh.read()
                    assert "context_repository" not in content, (
                        f"{os.path.join(root, f)} imports context_repository"
                    )

    def test_rip_profiles_have_format(self):
        from ui.audio_lab.models import RIP_PROFILES
        for p in RIP_PROFILES:
            assert p.fmt, f"Profile {p.name} has no format"
