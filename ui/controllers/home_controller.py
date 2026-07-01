"""HomeController — manages the Home dashboard page refresh lifecycle.

Uses HomeDashboardService to build a typed snapshot and delegates
visual rendering to HomePage.
"""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject

from core.home.home_dashboard_service import HomeDashboardService
from ui.hubs.home_page import HomePage

if TYPE_CHECKING:
    from ui.window import MainWindow

logger = logging.getLogger("michi.home_controller")


class HomeController(QObject):
    """Owns HomePage lifecycle + HomeDashboardService."""

    def __init__(self, window: MainWindow):
        super().__init__(window)
        self._win = window
        self._page: HomePage | None = None
        self._dashboard_svc: HomeDashboardService | None = None

    @property
    def page(self) -> HomePage | None:
        return self._page

    def _ensure_page(self) -> HomePage:
        if self._page is None:
            self._page = HomePage()
            self._page.navigation_requested.connect(
                self._win._on_sidebar_navigate
            )
            self._page.add_music_requested.connect(self._on_add_music)
            self._page.add_folder_requested.connect(self._on_add_folder)
        return self._page

    def _ensure_service(self) -> HomeDashboardService:
        if self._dashboard_svc is None:
            w = self._win
            self._dashboard_svc = HomeDashboardService(
                db=getattr(w, "_db", None),
                playback=getattr(w, "_playback", None),
                context_svc=getattr(w, "_context_svc", None),
                sync_mgr=getattr(w, "_sync_mgr", None),
                audio_output_ctrl=getattr(w, "_audio_output_ctrl", None),
                player_engine=getattr(w, "_player", None),
                features=getattr(w, "_features", None),
                settings_mgr=getattr(w, "_settings_mgr", None),
            )
        return self._dashboard_svc

    def show(self):
        """Show the Home page in the content stack."""
        page = self._ensure_page()
        w = self._win
        if not w._views.widget("home"):
            w._views.register("home", page)
        self.refresh()
        w._fade_content("home")

    def refresh(self):
        """Build fresh snapshot and push to HomePage."""
        page = self._page
        if page is None:
            return
        try:
            svc = self._ensure_service()
            snapshot = svc.build_snapshot()
            page.render_snapshot(snapshot)
        except Exception:
            logger.exception("HomeController refresh failed")
            from core.home.home_status import (
                HomeDashboardSnapshot,
                HomeAlert,
                HomeCardError,
                LibraryHomeStatus,
            )

            fallback = HomeDashboardSnapshot(
                overall_state="error",
                headline="Error al cargar",
                library=LibraryHomeStatus(is_empty=True),
                alerts=[
                    HomeAlert(
                        severity="critical",
                        kind="safe_mode",
                        title="Error al cargar el dashboard",
                        message="Ocurrió un error inesperado. Reintenta o reinicia.",
                        target_route="audio_lab_diagnostics",
                        action_label="Diagnóstico",
                    )
                ],
                errors=[HomeCardError("dashboard", "Error inesperado", is_fatal=True)],
            )
            page.render_snapshot(fallback)

    # ── Add Music handlers ──

    def _get_import_service(self):
        w = self._win
        svc = getattr(w, "_services", None)
        if svc and getattr(svc, "library_import", None):
            return svc.library_import
        svc = getattr(w, "_library_import", None)
        if svc:
            return svc
        logger.warning("LibraryImportService not available, using fallback")
        return None

    def _on_add_music(self, filepaths: list[str]):
        """Import selected files and refresh library."""
        w = self._win
        svc = self._get_import_service()
        if svc:
            added = svc.add_files(filepaths, reason="home_add_music")
        else:
            from library.metadata_extractor import ALL_EXTS

            added = 0
            for fp in filepaths:
                ext = os.path.splitext(fp)[1].lower()
                if ext in ALL_EXTS and os.path.isfile(fp):
                    w._db.add_file(fp)
                    added += 1
            if added:
                w._reload_library_after_change(reason="home_add_music_fallback")
        w._toast_svc.show(f"{added} canciones añadidas a la biblioteca", "success")
        self.refresh()

    def _on_add_folder(self, path: str):
        """Scan a folder for music files."""
        w = self._win
        svc = self._get_import_service()
        if svc and getattr(svc, "scan_folder", None):
            svc.scan_folder(path)
        else:
            w._scan_path(path)
        self.refresh()
