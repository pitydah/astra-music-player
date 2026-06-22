"""Genre Controller — genre navigation and actions."""
import os


class GenreController:
    def __init__(self, window):
        self._win = window

    def show_genres_overview(self, mode: str = "grid"):
        repo = self._win._ctx.genre_repo
        repo.build(self._win._ctx.all_items)
        self._win._ctx.genre_grid.set_genres(repo.groups, repo.families)
        self._win._ctx.configure_header("genres")
        self._win._ctx.fade_to("genre_grid")

    def open_genre_detail(self, genre_key: str):
        repo = self._win._ctx.genre_repo
        g = repo.get_group(genre_key)
        if not g:
            return
        repo.current_key = genre_key
        self._win._ctx.genre_detail.set_genre(g)
        self._win._ctx.section_title.setText(g.name)
        parts = [f"{g.track_count} canciones", f"{g.artist_count} artistas",
                 f"{g.album_count} álbumes"]
        self._win._ctx.section_subtitle.setText(" · ".join(parts))
        self._win._ctx.view_switcher.set_available_modes([])
        self._win._ctx.fade_to("genre_detail")

    def back_to_overview(self):
        self._win._ctx.genre_repo.current_key = None
        self.show_genres_overview()

    def play_genre(self, genre_key: str, shuffle: bool = False):
        fps = self._win._ctx.genre_repo.filepaths_for_genre(genre_key)
        if fps:
            if shuffle:
                import random
                random.shuffle(fps)
            self._win._play_filepaths(fps, play_now=True)

    def queue_genre(self, genre_key: str):
        fps = self._win._ctx.genre_repo.filepaths_for_genre(genre_key)
        if fps:
            self._win._ctx.playback.enqueue(fps, play_now=False)

    def create_playlist_from_genre(self, genre_key: str):
        repo = self._win._ctx.genre_repo
        g = repo.get_group(genre_key)
        if not g:
            return
        pid = self._win._ctx.db.create_playlist(g.name)
        for fp in [t.filepath for t in g.tracks if os.path.isfile(t.filepath)]:
            self._win._ctx.db.add_to_playlist(pid, fp)
        self._win._ctx.rebuild_sidebar()
        self._win._ctx.toast.show(f"Playlist creada: {g.name}", "success")

    def edit_genre_metadata(self, genre_key: str):
        fps = self._win._ctx.genre_repo.filepaths_for_genre(genre_key)
        if fps:
            self._open_metadata(fps)

    def normalize_genre(self, genre_key: str):
        repo = self._win._ctx.genre_repo
        g = repo.get_group(genre_key)
        if not g:
            return
        self._win._ctx.toast.show(
            f"Normalización de '{g.name}': usa el Editor de metadatos para limpiar tags", "info")
        self.edit_genre_metadata(genre_key)

    def _open_metadata(self, filepaths: list[str]):
        self._win._ctx.metadata_editor.load_files(filepaths)
        self._win._ctx.configure_header("metadata_editor")
        self._win._ctx.fade_to("metadata_editor")
