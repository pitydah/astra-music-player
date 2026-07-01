"""Playlist controller — Hub actions, import/export, smart playlists.

Uses PlaylistStore for all CRUD operations.
"""
import os

from PySide6.QtWidgets import QFileDialog, QInputDialog


class PlaylistController:
    def __init__(self, window, services=None):
        self._win = window
        self._ctx = window._ctx
        self._svc = services
        self._isfile_cache: dict[str, bool] = {}

    @property
    def _store(self):
        from library.playlists.playlist_store import PlaylistStore
        db = getattr(self._ctx, 'db', None)
        if db and hasattr(db, '_conn'):
            return PlaylistStore(db._conn)
        return None

    def _invalid_isfile_cache(self):
        self._isfile_cache.clear()

    @staticmethod
    def _cached_isfile(fp: str, cache: dict[str, bool]) -> bool:
        if not fp:
            return False
        if fp not in cache:
            cache[fp] = os.path.isfile(fp)
        return cache[fp]

    def _context(self):
        return (
            getattr(self._svc, "context_svc", None)
            or getattr(self._ctx, "context_svc", None)
        )

    def _select_playlist(self, pid: int, name: str = ""):
        ctx = self._context()
        if ctx:
            ctx.update_selection(
                scope="playlist",
                playlist_id=pid,
                playlist_name=name,
                album="", artist="", genre="",
                folder_name="", mix_key="", search_query="",
            )

    def _record_playlist_created(self, pid: int, name: str, count: int):
        self._select_playlist(pid, name)
        ctx = self._context()
        if ctx:
            ctx.record_playlist_created(playlist_id=pid, name=name, count=count)

    def _toast(self, text: str, level: str = "info"):
        if self._ctx and hasattr(self._ctx, 'toast'):
            self._ctx.toast.show(text, level)

    # ── M3U Import ──

    def import_m3u(self):
        from library.playlists.playlist_import import import_as_playlist
        path, _ = QFileDialog.getOpenFileName(
            self._win, "Importar M3U", "",
            "Playlist M3U (*.m3u *.m3u8);;Todos (*.*)")
        if not path:
            return
        store = self._store
        if not store:
            self._toast("Base de datos no disponible", "error")
            return
        result = import_as_playlist(path, store)
        if result.ok:
            self._toast(f"Importada '{result.playlist_name}' ({result.imported} temas)", "success")
            self._record_playlist_created(result.playlist_id, result.playlist_name, result.imported)
            ctx = self._context()
            if ctx and hasattr(ctx, 'record_playlist_imported'):
                ctx.record_playlist_imported(
                    playlist_id=result.playlist_id, name=result.playlist_name,
                    count=result.imported)
            if hasattr(self._ctx, 'rebuild_sidebar'):
                self._ctx.rebuild_sidebar()
        else:
            self._toast(f"Error al importar: {result.message}", "error")

    # ── M3U Export ──

    def export_playlists(self):
        self.export_m3u()

    def export_m3u(self):
        from library.playlists.playlist_export import export_m3u
        playlists = self._get_db().get_playlists()
        if not playlists:
            self._toast("No hay playlists para exportar", "info")
            return
        names = [p["name"] for p in playlists]
        name, ok = QInputDialog.getItem(
            self._win, "Exportar playlist", "Selecciona:",
            names, 0, False)
        if not ok or not name:
            return
        pl = next((p for p in playlists if p["name"] == name), None)
        if not pl:
            return
        path, _ = QFileDialog.getSaveFileName(
            self._win, "Guardar M3U", f"{name}.m3u",
            "Playlist M3U (*.m3u);;Todos (*.*)")
        if not path:
            return
        store = self._store
        if store:
            result = export_m3u(store, pl["id"], path)
            if result.get("ok"):
                self._toast(f"Exportada '{name}' con {result['count']} temas", "success")
                ctx = self._context()
                if ctx and hasattr(ctx, 'record_playlist_exported'):
                    ctx.record_playlist_exported(pl["id"], name, result["count"])

    def import_playlist(self, parent, db, playback, player_bar_ctrl, load_library):
        from PySide6.QtWidgets import QFileDialog, QMessageBox
        path, _ = QFileDialog.getOpenFileName(
            parent, "Importar playlist", os.path.expanduser("~"),
            "Playlists (*.m3u *.m3u8 *.pls);;Todos (*)")
        if not path:
            return
        from ui.playlist_io import parse_playlist_entries
        entries = parse_playlist_entries(path)
        if not entries:
            QMessageBox.information(
                parent, "Importar", "No se encontraron entradas en la playlist.")
            return

        valid_files = []
        missing = 0
        remote = 0
        for e in entries:
            if e.is_remote:
                remote += 1
                continue
            if e.exists:
                db.add_file(e.resolved_path)
                valid_files.append(e.resolved_path)
            else:
                missing += 1

        load_library()
        if valid_files:
            playback.enqueue(valid_files, play_now=False)
        player_bar_ctrl.set_track(
            f"Importados {len(valid_files)} temas", "Playlist")

        summary = f"<p><b>{len(valid_files)}</b> archivos añadidos a la biblioteca.</p>"
        if missing:
            summary += f"<p><b>{missing}</b> archivos no encontrados en disco.</p>"
        if remote:
            summary += f"<p><b>{remote}</b> entradas remotas ignoradas.</p>"
        summary += f"<p>Total entradas en playlist: <b>{len(entries)}</b></p>"
        QMessageBox.information(parent, "Importar playlist", summary)

        ctx = self._context()
        if ctx:
            ctx.record_playlist_imported(0, os.path.basename(path), len(valid_files))

    def export_queue(self, parent, playback):
        from PySide6.QtWidgets import QFileDialog, QMessageBox
        queue = playback.get_queue()
        if not queue:
            QMessageBox.information(
                parent, "Exportar", "La cola de reproducción está vacía.")
            return
        path, _ = QFileDialog.getSaveFileName(
            parent, "Exportar playlist", "playlist.m3u",
            "M3U (*.m3u);;Todos (*)")
        if not path:
            return
        from ui.playlist_io import export_m3u
        export_m3u(path, [q["filepath"] for q in queue])
        QMessageBox.information(
            parent, "Exportar", f"Playlist exportada a {path}")

        ctx = self._context()
        if ctx:
            ctx.record_playlist_exported(0, os.path.basename(path), len(queue))

    # ── Playlist from folder ──

    def hub_create_from_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self._win, "Seleccionar carpeta musical")
        if not folder:
            return
        from library.library_db import AUDIO_EXTS
        filepaths = []
        for root, _dirs, files in os.walk(folder):
            for f in files:
                if os.path.splitext(f)[1].lower() in AUDIO_EXTS:
                    filepaths.append(os.path.join(root, f))
        if not filepaths:
            self._toast("No se encontraron archivos de audio en la carpeta", "info")
            return
        name = os.path.basename(folder.rstrip("/"))
        store = self._store
        if store:
            pid = store.create_playlist(name)
            for fp in filepaths:
                store.add_track(pid, filepath=fp, source="folder_import")
            if hasattr(self._ctx, 'rebuild_sidebar'):
                self._ctx.rebuild_sidebar()
            self._toast(f"Creada '{name}' con {len(filepaths)} temas", "success")
            self._record_playlist_created(pid, name, len(filepaths))

    # ── Playlist from queue ──

    def hub_create_from_queue(self):
        playback = self._svc.playback if self._svc and hasattr(self._svc, 'playback') else self._ctx.playback
        queue = playback.get_queue() if hasattr(playback, 'get_queue') else []
        if not queue:
            self._toast("La cola de reproducción está vacía", "info")
            return
        name, ok = QInputDialog.getText(
            self._win, "Crear playlist desde cola", "Nombre:")
        if not ok or not name.strip():
            return
        name = name.strip()
        store = self._store
        if store:
            pid = store.create_playlist(name)
            for q in queue:
                fp = q.get("filepath", q) if isinstance(q, dict) else q
                if self._cached_isfile(fp, self._isfile_cache):
                    store.add_track(pid, filepath=fp, source="queue")
            if hasattr(self._ctx, 'rebuild_sidebar'):
                self._ctx.rebuild_sidebar()
            self._toast(f"Creada '{name}' con {len(queue)} temas", "success")
            self._record_playlist_created(pid, name, len(queue))

    # ── Create from album/artist/genre/search ──

    def _all_library_tracks(self) -> list:
        if self._svc and hasattr(self._svc, 'db'):
            return self._svc.db.get_all()
        return self._ctx.all_items_list

    def create_from_album(self):
        all_items = self._all_library_tracks()
        if not all_items:
            self._toast("No hay música en la biblioteca", "info")
            return
        from library.artist_grouping import build_artist_albums
        artist_data = build_artist_albums(all_items)
        albums = []
        album_tracks = {}
        for _akey, (agroups, _loose) in artist_data.items():
            for ag in agroups:
                label = f"{ag.title} — {ag.artist}" if ag.artist else ag.title
                albums.append(label)
                album_tracks[label] = ag.tracks
        if not albums:
            self._toast("No se encontraron álbumes", "info")
            return
        label, ok = QInputDialog.getItem(
            self._win, "Crear playlist desde album",
            "Selecciona:", sorted(albums), 0, False)
        if not ok or not label:
            return
        tracks = album_tracks.get(label, [])
        fps = [t.filepath for t in tracks if self._cached_isfile(t.filepath, self._isfile_cache)]
        if fps:
            store = self._store
            if store:
                pid = store.create_playlist(label[:64])
                for fp in fps:
                    store.add_track(pid, filepath=fp, source="album")
                if hasattr(self._ctx, 'rebuild_sidebar'):
                    self._ctx.rebuild_sidebar()
                self._toast(f"Playlist creada: {label[:48]} ({len(fps)} temas)", "success")
                self._record_playlist_created(pid, label[:64], len(fps))

    def create_from_artist(self):
        all_items = self._all_library_tracks()
        if not all_items:
            self._toast("No hay música en la biblioteca", "info")
            return
        from library.artist_grouping import build_artist_groups
        groups = build_artist_groups(all_items)
        names = sorted(g.display_name for g in groups if g.display_name)
        if not names:
            self._toast("No se encontraron artistas", "info")
            return
        name, ok = QInputDialog.getItem(
            self._win, "Crear playlist desde artista",
            "Selecciona:", names, 0, False)
        if not ok or not name:
            return
        group = next((g for g in groups if g.display_name == name), None)
        if group:
            fps = [t.filepath for t in group.all_tracks if self._cached_isfile(t.filepath, self._isfile_cache)]
            if fps:
                store = self._store
                if store:
                    pid = store.create_playlist(name)
                    for fp in fps:
                        store.add_track(pid, filepath=fp, source="artist")
                    if hasattr(self._ctx, 'rebuild_sidebar'):
                        self._ctx.rebuild_sidebar()
                    self._toast(f"Playlist creada: {name} ({len(fps)} temas)", "success")
                    self._record_playlist_created(pid, name, len(fps))

    def create_from_genre(self):
        all_items = self._all_library_tracks()
        if not all_items:
            self._toast("No hay música en la biblioteca", "info")
            return
        genres = sorted(set(i.genre for i in all_items if i.genre))
        if not genres:
            self._toast("No se encontraron géneros", "info")
            return
        genre, ok = QInputDialog.getItem(
            self._win, "Crear playlist desde genero",
            "Selecciona:", genres, 0, False)
        if not ok or not genre:
            return
        tracks = [i for i in all_items if i.genre == genre]
        fps = [t.filepath for t in tracks if self._cached_isfile(t.filepath, self._isfile_cache)]
        if fps:
            store = self._store
            if store:
                pid = store.create_playlist(genre)
                for fp in fps:
                    store.add_track(pid, filepath=fp, source="genre")
                if hasattr(self._ctx, 'rebuild_sidebar'):
                    self._ctx.rebuild_sidebar()
                self._toast(f"Playlist creada: {genre} ({len(fps)} temas)", "success")
                self._record_playlist_created(pid, genre, len(fps))

    def create_from_search(self):
        model = self._ctx.model
        if not model or model.rowCount() == 0:
            self._toast("No hay resultados de busqueda activos", "info")
            return
        name, ok = QInputDialog.getText(
            self._win, "Crear playlist desde busqueda", "Nombre:")
        if not ok or not name.strip():
            return
        name = name.strip()
        fps = []
        for row in range(model.rowCount()):
            ref = model.get_trackref(row)
            fp = ref.uri if ref else ""
            if fp and self._cached_isfile(fp, self._isfile_cache):
                fps.append(fp)
        if fps:
            store = self._store
            if store:
                pid = store.create_playlist(name)
                for fp in fps:
                    store.add_track(pid, filepath=fp, source="search")
                if hasattr(self._ctx, 'rebuild_sidebar'):
                    self._ctx.rebuild_sidebar()
                self._toast(f"Playlist creada: {name} ({len(fps)} temas)", "success")
                self._record_playlist_created(pid, name, len(fps))

    def open_smart_playlist(self, key: str):
        self._ctx.navigate_sidebar(
            f"mix_{key}" if not key.startswith("mix_") else key)

    def hub_playlist_play(self, pid: int):
        items = self._get_db().get_playlist_items(pid)
        fps = [i.filepath for i in items]
        playback = self._svc.playback if self._svc and hasattr(self._svc, 'playback') else self._ctx.playback
        if hasattr(playback, 'play_queue'):
            playback.play_queue(fps)
        else:
            playback.enqueue(fps, play_now=True)
        self._toast("Reproduciendo playlist", "success")
        pl = self.get_playlist_by_id(pid)
        name = pl.get("name", "") if pl else ""
        self._select_playlist(pid, name)
        ctx = self._context()
        if ctx:
            ctx.record_playlist_played(playlist_id=pid, name=name, count=len(fps))
            ctx.record_queue_updated(count=len(fps), source="playlist")

    def hub_playlist_queue(self, pid: int):
        items = self._get_db().get_playlist_items(pid)
        fps = [i.filepath for i in items]
        self._ctx.playback.enqueue(fps, play_now=False)
        self._toast("Playlist anadida a la cola", "success")

        pl = self.get_playlist_by_id(pid)
        name = pl.get("name", "") if pl else ""
        self._select_playlist(pid, name)
        ctx = self._context()
        if ctx:
            ctx.record_playlist_queued(playlist_id=pid, name=name, count=len(fps))
            ctx.record_queue_updated(count=len(fps), source="playlist")

    def _on_track_context_action(self, action: str, pid: int, filepath: str):
        if action == "queue":
            playback = self._svc.playback if self._svc and hasattr(self._svc, 'playback') else self._ctx.playback
            if hasattr(playback, 'enqueue'):
                playback.enqueue([filepath], play_now=False)
            self._toast("Canción añadida a la cola", "success")
        elif action == "remove":
            store = self._store
            if store:
                store.remove_track(pid, filepath=filepath)
                self._toast("Canción quitada de la playlist", "info")
        elif action == "locate":
            folder = os.path.dirname(filepath)
            if os.path.isdir(folder):
                import subprocess
                subprocess.Popen(["xdg-open", folder])
        elif action == "metadata":
            if hasattr(self._win, '_open_metadata_for_files'):
                self._win._open_metadata_for_files([filepath])
        elif action == "analyze":
            from core.audio_lab.diagnostics_service import analyse_file
            try:
                analyse_file(filepath)
                self._toast("Análisis completado", "success")
            except Exception as e:
                self._toast(f"Error al analizar: {e}", "error")
        elif action == "view_album":
            if hasattr(self._win, '_album_ctrl') and self._win._album_ctrl:
                self._win._album_ctrl.navigate_to_album_by_title(
                    os.path.basename(os.path.dirname(filepath)))
        elif action == "view_artist":
            self._toast("Ver artista: próximamente", "info")

    # ── CRUD helpers ──

    def _get_db(self):
        return self._ctx.db

    def get_all_playlists(self) -> list[dict]:
        return self._get_db().get_playlists()

    def get_playlist_items(self, pid: int) -> list:
        return self._get_db().get_playlist_items(pid)

    def get_playlist_by_id(self, pid: int) -> dict | None:
        return next(
            (p for p in self._get_db().get_playlists() if p["id"] == pid),
            None,
        )

    def create_playlist(self, name: str) -> int:
        store = self._store
        if store:
            pid = store.create_playlist(name.strip())
            if hasattr(self._ctx, 'rebuild_sidebar'):
                self._ctx.rebuild_sidebar()
            self._record_playlist_created(pid, name.strip(), 0)
            return pid
        return 0

    def delete_playlist(self, pid: int):
        store = self._store
        if store:
            pl = store.get_playlist(pid)
            name = pl.get("name", "") if pl else ""
            store.delete_playlist(pid)
            if hasattr(self._ctx, 'rebuild_sidebar'):
                self._ctx.rebuild_sidebar()
            if hasattr(self._ctx, 'load_library'):
                self._ctx.load_library()
            ctx = self._context()
            if ctx:
                ctx.record_playlist_deleted(playlist_id=pid, name=name)
            self._toast("Playlist eliminada.", "info")

    def add_track_to_playlist(self, pid: int, fp: str):
        store = self._store
        if store:
            store.add_track(pid, filepath=fp, source="manual")
            ctx = self._context()
            if ctx:
                pl = store.get_playlist(pid)
                name = pl.get("name", "") if pl else ""
                ctx.record_track_added_to_playlist(playlist_id=pid, name=name, count=1)

    @staticmethod
    def _add_files_to_playlist(db, pid: int, filepaths: list[str]) -> int:
        import os
        valid = 0
        for fp in filepaths:
            if os.path.isfile(fp):
                db.add_to_playlist(pid, fp)
                valid += 1
        return valid

    def create_playlist_from_tracks(self, tracks: list, name: str) -> int:
        if not tracks or not name:
            return 0
        store = self._store
        if not store:
            return 0
        pid = store.create_playlist(name.strip())
        valid_count = 0
        for t in tracks:
            fp = t.filepath if hasattr(t, 'filepath') else str(t)
            if self._cached_isfile(fp, self._isfile_cache):
                store.add_track(pid, filepath=fp, source="manual")
                valid_count += 1
        if hasattr(self._ctx, 'rebuild_sidebar'):
            self._ctx.rebuild_sidebar()
        self._toast(f"Playlist creada: {name[:48]} ({valid_count} temas)", "success")
        self._record_playlist_created(pid, name.strip(), valid_count)
        return pid

    def add_files_to_playlist_dialog(self, filepaths: list[str]):
        if not filepaths:
            return
        from PySide6.QtWidgets import QInputDialog
        store = self._store
        if not store:
            return
        playlists = store.get_all_playlists(include_stats=False)
        names = [p.name for p in playlists] + ["+ Nueva playlist"]
        name, ok = QInputDialog.getItem(
            self._win, "Agregar a playlist", "Selecciona playlist:",
            names, 0, False)
        if not ok:
            return
        if name == "+ Nueva playlist":
            name, ok = QInputDialog.getText(
                self._win, "Nueva playlist", "Nombre:")
            if not ok or not name.strip():
                return
            pid = store.create_playlist(name.strip())
        else:
            pl = next((p for p in playlists if p.name == name), None)
            if not pl:
                return
            pid = pl.id
        count = 0
        for fp in filepaths:
            if os.path.isfile(fp):
                store.add_track(pid, filepath=fp, source="dialog")
                count += 1
        if hasattr(self._ctx, 'rebuild_sidebar'):
            self._ctx.rebuild_sidebar()
        self._toast(f"Agregados {count} temas a '{name}'", "success")
        ctx = self._context()
        if ctx:
            ctx.record_track_added_to_playlist(playlist_id=pid, name=name, count=count)

    def metadata_saved(self, filepaths: list):
        self._toast(f"Metadatos guardados en {len(filepaths)} archivos", "success")

    def refresh_library(self):
        self._ctx.load_library()

    # ── DB read accessors ──

    def get_favorites(self) -> list[str]:
        return self._get_db().get_favorites()

    def get_play_history(self, limit: int = 50) -> list[dict]:
        return self._get_db().get_play_history(limit=limit)

    def get_all_tracks(self) -> list:
        return self._get_db().get_all()

    def save_queue(self, engine):
        try:
            if hasattr(engine, '_queue') and engine._queue:
                self._get_db().save_queue(engine._queue, engine._queue_index)
        except Exception:
            pass

    def add_files(self, filepaths: list[str]):
        for fp in filepaths:
            self._get_db().add_file(fp)

    def show_playlist_hub(self, key: str = ""):
        w = self._win
        store = self._store
        if store:
            summaries = store.get_all_playlists(include_stats=True)
            w._playlist_hub.set_playlists(summaries)
        w._fade_content("playlist_hub")

    def show_playlist_detail(self, key: str):
        w = self._win
        pid = int(key.split(":", 1)[1])
        w._current_playlist = pid
        store = self._store
        if store:
            tracks = store.get_playlist_items(pid)
            pl = store.get_playlist(pid) or {"name": "Playlist", "id": pid}
            w._playlist_detail.set_playlist(pl, tracks)
            total_dur = sum(t.duration for t in tracks)
            h = int(total_dur // 3600)
            m = int((total_dur % 3600) // 60)
            dur_str = f"{h} h {m} min" if h > 0 else f"{m} min" if m > 0 else ""
            subtitle = f"{len(tracks)} canciones"
            if dur_str:
                subtitle += f" · {dur_str}"
            w._section_title.setText(pl.get("name", "Playlist"))
            w._section_subtitle.setText(subtitle)
            w._search.show()
            w._fade_content("playlist_detail")

    def on_playlist_track_activated(self, row: int, filepath: str):
        w = self._win
        pid = getattr(w, '_current_playlist', 0)
        if not pid:
            return
        store = self._store
        if store:
            paths = [t.filepath for t in store.get_playlist_items(pid) if t.filepath]
            if not paths:
                return
            start_idx = max(0, min(row, len(paths) - 1))
            if hasattr(w._playback, 'play_queue'):
                w._playback.play_queue(paths, start_idx)

    def update_playlist(self, pid: int, **kwargs):
        store = self._store
        if store:
            store.update_playlist_metadata(pid, **kwargs)

    def audit_playlist(self, pid: int):
        from library.playlists.playlist_audit import audit_playlist
        store = self._store
        if store:
            report = audit_playlist(store, pid)
            score = report.score
            issues = len(report.issues)
            msg = f"Auditoría: {score}/100, {issues} issue(s)"
            self._toast(msg, "info" if score >= 70 else "warning")

    def relink_playlist(self, pid: int):
        from library.playlists.playlist_relinker import auto_relink
        store = self._store
        if store:
            db = getattr(self._ctx, 'db', None)
            conn = db._conn if db and hasattr(db, '_conn') else None
            if conn:
                result = auto_relink(store, pid, conn)
                self._toast(f"Re-enlazados: {result['relinked']}, fallos: {result['failed']}", "success")

    def clean_empty_playlists(self):
        from library.playlists.playlist_audit import find_empty_playlists
        store = self._store
        if store:
            empty = find_empty_playlists(store)
            for pid in empty:
                store.delete_playlist(pid)
            count = len(empty)
            if count:
                self._toast(f"Eliminadas {count} playlists vacías", "success")
            else:
                self._toast("No hay playlists vacías", "info")

    def find_lost_files(self):
        from library.playlists.playlist_audit import audit_all_playlists
        store = self._store
        if store:
            reports = audit_all_playlists(store)
            total_lost = sum(
                len([i for i in r.issues if i.issue_type == "lost"])
                for r in reports
            )
            self._toast(f"{total_lost} archivos perdidos en total", "warning" if total_lost else "info")

    def get_detected_tracks(self, limit: int = 100) -> list:
        return self._get_db().get_detected_tracks(limit)

    def clear_detected_tracks(self):
        self._get_db().clear_detected_tracks()

    def delete_detected_track(self, idx: int):
        if hasattr(self._get_db(), 'delete_detected_track'):
            self._get_db().delete_detected_track(idx)
