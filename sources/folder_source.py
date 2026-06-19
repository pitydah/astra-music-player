"""FolderSource — wraps folder_index as a MusicSource."""

import os

from sources.base_source import MusicSource, TrackRef
from library.folder_index import list_audio_files, list_subfolders


AUDIO_EXTS = {".mp3", ".flac", ".ogg", ".wav", ".m4a", ".aac", ".opus",
              ".dsf", ".dff", ".aiff", ".ape", ".wv", ".wma", ".spx"}


class FolderSource(MusicSource):
    def __init__(self, root: str):
        self.root = root

    def list_tracks(self) -> list[TrackRef]:
        return self._files_to_refs(list_audio_files(self.root))

    def search(self, query: str) -> list[TrackRef]:
        q = query.lower()
        return [t for t in self.list_tracks()
                if q in t.title.lower() or q in os.path.dirname(t.uri).lower()]

    def _files_to_refs(self, paths: list[str]) -> list[TrackRef]:
        return [TrackRef(
            uri=p,
            title=os.path.splitext(os.path.basename(p))[0],
            duration=0.0,
        ) for p in paths]

    def list_folders(self, path: str | None = None) -> list[str]:
        return list_subfolders(path or self.root)

    def list_folder_tracks(self, path: str) -> list[TrackRef]:
        return self._files_to_refs(list_audio_files(path))
