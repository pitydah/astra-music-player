"""Album controller — advanced actions on albums: play, queue, metadata, covers, quality, server."""
from __future__ import annotations

import logging
import os
import subprocess

from PySide6.QtWidgets import QInputDialog, QLineEdit

from library.album_identity import detect_album_artist
import contextlib

logger = logging.getLogger("michi.album_controller")


class AlbumController:
    def __init__(self, window, refresh_grid=None, services=None):
        self._win = window
        self._ctx = window._ctx
        self._svc = services
        self._refresh_grid = refresh_grid or (lambda: None)

    @property
    def _context_svc(self):
        return (
            getattr(self._svc, "context_svc", None)
            or getattr(self._ctx, "context_svc", None)
            or getattr(self._win, "_context_svc", None)
        )

    def _toast(self, text: str, level: str = "info"):
        self._ctx.toast.show(text, level)

    def _playback(self):
        return getattr(self._win, "_playback", None) or getattr(self._ctx, "playback", None)

    def _playback_ctrl(self):
        return getattr(self._win, "_playback_ctrl", None)

    def _filepaths(self, tracks: list) -> list[str]:
        return [str(getattr(t, "filepath", "") or "") for t in tracks
                if str(getattr(t, "filepath", "") or "")]

    def play_album(self, tracks: list) -> None:
        fps = self._filepaths(tracks)
        if not fps:
            self._toast("No hay canciones para reproducir", "error")
            return
        w = self._win
        if hasattr(w, "_play_filepaths"):
            w._play_filepaths(fps, play_now=True)
        else:
            pb = self._playback()
            if pb:
                pb.enqueue(fps, play_now=True)
        self._toast(f"Reproduciendo {len(fps)} canciones", "info")
        ctx = self._context_svc
        if ctx and hasattr(ctx, "record_event"):
            with contextlib.suppress(Exception):
                ctx.record_event("album_played", {"track_count": len(fps)})

    def queue_album(self, tracks: list) -> None:
        fps = self._filepaths(tracks)
        if not fps:
            self._toast("No hay canciones para encolar", "error")
            return
        pb = self._playback()
        if pb and hasattr(pb, "enqueue"):
            pb.enqueue(fps, play_now=False)
        else:
            pc = self._playback_ctrl()
            if pc and hasattr(pc, "enqueue_with_context"):
                pc.enqueue_with_context(fps, play_now=False, source="album")
        self._toast(f"{len(fps)} canciones añadidas a la cola", "info")
        ctx = self._context_svc
        if ctx and hasattr(ctx, "record_event"):
            with contextlib.suppress(Exception):
                ctx.record_event("album_queued", {"track_count": len(fps)})

    def play_next_album(self, tracks: list) -> None:
        fps = self._filepaths(tracks)
        if not fps:
            self._toast("No hay canciones", "error")
            return
        pb = self._playback()
        if pb and hasattr(pb, "enqueue"):
            queue = pb.get_queue() or []
            if queue:
                pb.enqueue(fps, play_now=False)
                self._toast(f"Reproduciendo {len(fps)} canciones después de actual", "info")
                return
        self.play_album(tracks)

    def create_playlist(self, fps: list) -> None:
        pc = self._playback_ctrl()
        if pc:
            pc.enqueue_with_context(fps, play_now=False, source="album")
        else:
            pb = self._playback()
            if pb:
                pb.enqueue(fps, play_now=False)
        self._toast("Álbum añadido a la cola", "success")

    def create_playlist_from_tracks(self, tracks: list, name: str = "") -> None:
        fps = self._filepaths(tracks)
        if not fps:
            self._toast("No hay canciones para crear playlist", "error")
            return
        if not name:
            album = str(getattr(tracks[0], "album", "") if tracks else "")
            artist = detect_album_artist(tracks)
            suggested = f"{album} — {artist}" if album and artist else "Nueva playlist"
            name, ok = QInputDialog.getText(
                self._win, "Crear playlist", "Nombre:", QLineEdit.Normal, suggested)
            if not ok or not name.strip():
                return
        db = getattr(self._win, "_db", None) or getattr(self._ctx, "db", None)
        if not db:
            self._toast("Base de datos no disponible", "error")
            return
        pid = db.create_playlist(name.strip())
        for fp in fps:
            if os.path.isfile(fp):
                db.add_to_playlist(pid, fp)
        if hasattr(self._win, "_rebuild_sidebar"):
            self._win._rebuild_sidebar()
        self._toast(f"Playlist '{name.strip()}' creada con {len(fps)} canciones", "success")
        ctx = self._context_svc
        if ctx and hasattr(ctx, "record_event"):
            with contextlib.suppress(Exception):
                ctx.record_event("playlist_created_from_album",
                                 {"name": name, "track_count": len(fps)})

    def edit_album_metadata(self, tracks: list) -> None:
        w = self._win
        fps = self._filepaths(tracks)
        if not fps:
            self._toast("No hay archivos para editar", "error")
            return
        editor = getattr(w, "_metadata_editor", None)
        if editor and hasattr(editor, "load_files"):
            editor.load_files(fps)
            if hasattr(w, "_configure_header_for_section"):
                w._configure_header_for_section("metadata_editor")
            if hasattr(w, "_fade_content"):
                w._fade_content("metadata_editor")
        else:
            self._toast("Editor de metadatos no disponible", "error")

    def search_or_change_cover(self, tracks: list) -> None:
        if not tracks:
            self._toast("No hay canciones en este álbum", "error")
            return
        d = os.path.dirname(str(getattr(tracks[0], "filepath", "") or "."))
        try:
            from library.artwork_cache import cache_cover
            from library.cover_art_service import CoverArtService
            cover_path = os.path.join(d, "cover.jpg")
            if os.path.isfile(cover_path):
                from PySide6.QtGui import QPixmap
                pix = QPixmap(cover_path)
                if not pix.isNull():
                    cache_cover(cover_path, pix, "large")
                self._toast("Carátula actualizada", "success")
                self._refresh_grid()
            elif CoverArtService.find_cover(str(getattr(tracks[0], "filepath", ""))):
                self._toast("Carátula encontrada", "success")
                self._refresh_grid()
            else:
                self._toast("No se encontró carátula local", "info")
        except Exception as e:
            self._toast(f"Error al buscar carátula: {e}", "error")

    def analyze_album_quality(self, tracks: list) -> None:
        if not tracks:
            self._toast("No hay canciones para analizar", "error")
            return
        try:
            from library.album_repository import AlbumRepository
            repo = AlbumRepository()
            repo.build(tracks)
            key = repo.list_groups()[0].identity.album_key if repo.list_groups() else ""
            if key:
                quality = repo.get_quality_summary(key)
                msg = (f"Calidad dominante: {quality.dominant_quality.upper()}\n"
                       f"Formato: {quality.dominant_format}\n"
                       f"Hi-Res: {'Sí' if quality.has_hires else 'No'}\n"
                       f"Lossless: {'Sí' if quality.has_lossless else 'No'}\n"
                       f"Lossy: {'Sí' if quality.has_lossy else 'No'}\n"
                       f"DSD: {'Sí' if quality.has_dsd else 'No'}\n")
                if quality.warnings:
                    msg += "\nAdvertencias:\n" + "\n".join(f"• {w}" for w in quality.warnings)
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.information(self._win, "Análisis de calidad", msg)
            else:
                self._toast("No se pudo analizar la calidad", "error")
        except Exception as e:
            self._toast(f"Error al analizar calidad: {e}", "error")
        ctx = self._context_svc
        if ctx and hasattr(ctx, "record_event"):
            with contextlib.suppress(Exception):
                ctx.record_event("quality_analyzed", {"track_count": len(tracks)})

    def send_album_to_server(self, tracks: list) -> None:
        try:
            from integrations.michi_link.services.import_to_server_service import (
                ImportToServerService,
            )
            svc = ImportToServerService()
            server = getattr(self._ctx, "micro_server", None)
            if not server:
                self._toast(
                    "Michi Link no está configurado. Configura un servidor en "
                    "Dispositivos > Michi Sync Suite.", "info")
                return
            fps = self._filepaths(tracks)
            result = svc.create_session(server, fps)
            if result.ok:
                self._toast(
                    f"Preflight: {result.data.get('existing', 0)} existentes, "
                    f"{result.data.get('needs_upload', 0)} a subir", "info")
            else:
                self._toast(f"Error en preflight: {result.message}", "error")
        except ImportError:
            self._toast("Michi Link no está disponible en esta versión", "info")

    def sync_album_to_mobile(self, tracks: list) -> None:
        self._toast("Sincronización con móvil: preparado en Michi Sync Suite (Fase 2)", "info")

    def open_album_folder(self, tracks: list) -> None:
        for t in tracks:
            fp = str(getattr(t, "filepath", "") or "")
            if fp:
                folder = os.path.dirname(fp)
                subprocess.Popen(["xdg-open", folder])
                return
        self._toast("No se encontró la carpeta", "error")

    # Legacy methods

    def search_cover(self, group):
        tracks = group.data.get("tracks", []) if hasattr(group, "data") and group.data else []
        self.search_or_change_cover(tracks)

    def open_folder(self, folder: str):
        subprocess.Popen(["xdg-open", folder])

    def show_details(self, group):
        tracks = group.data.get("tracks", []) if hasattr(group, "data") and group.data else []
        count = len(tracks)
        dur = sum(getattr(t, 'duration', 0) or 0 for t in tracks)
        dur_str = f"{dur // 60}:{int(dur % 60):02d}" if dur > 0 else "—"
        exts = set(
            (getattr(t, 'ext', '') or '').upper().lstrip(".")
            for t in tracks if getattr(t, 'ext', ''))
        fmt_str = ", ".join(sorted(exts)) or "—"
        msg = (
            f"Álbum: {group.title}\n"
            f"Artista: {group.subtitle or '—'}\n"
            f"Canciones: {count}\n"
            f"Duración: {dur_str}\n"
            f"Formato: {fmt_str}"
        )
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(self._win, "Detalles del álbum", msg)

    def show_album_detail_from_cover_item(self, cover_item):
        import unicodedata
        w = self._win
        w._nav_ctrl.checkpoint()
        album = getattr(cover_item, 'title', '') or ''
        artist = getattr(cover_item, 'subtitle', '') or ''
        tracks = []
        data = getattr(cover_item, 'data', None)
        if isinstance(data, dict):
            tracks = data.get("tracks", [])
        if not tracks and hasattr(w, '_all_items'):
            from library.album_art import group_by_album
            def _norm(s):
                s = (s or '').strip().lower()
                return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii')
            for a, ar, tr in group_by_album(w._lib_ctrl.filtered_album_items()):
                if _norm(album) == _norm(a) or (album and _norm(album) in _norm(a)):
                    tracks = tr
                    album = a
                    artist = ar
                    break
        if not tracks:
            w._count.setText("Selecciona un álbum")
            return
        dur = sum(getattr(t, 'duration', 0) or 0 for t in tracks)
        mins = int(dur // 60)
        dur_str = f"{mins // 60} h {mins % 60} min" if mins >= 60 else f"{mins} min"
        year = str(tracks[0].year) if tracks and getattr(tracks[0], 'year', 0) else ""
        exts = set((getattr(t, 'ext', '') or '').upper().lstrip(".") for t in tracks if getattr(t, 'ext', ''))
        fmt = " · ".join(sorted(exts)) if exts else ""
        w._album_detail_view.set_album(
            title=album, artist=artist, year=year,
            cover_pixmap=getattr(cover_item, 'pixmap', None),
            tracks=tracks, total_duration=dur_str, format_info=fmt)
        w._albums_stack.setCurrentIndex(1)

        ctx = self._context_svc
        if ctx:
            ctx.update_selection(
                scope="album",
                album=album,
                artist=artist,
                genre="",
                playlist_id=None,
                playlist_name="",
                folder_name="",
                mix_key="",
                search_query="",
            )
        w._count.setText(album)
