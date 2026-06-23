"""Tag writer — reads and writes metadata tags to audio files. STUB."""

from __future__ import annotations


class TagWriter:
    def read_tags(self, path: str) -> dict:
        return {}

    def write_tags(self, path: str, metadata: dict):
        pass

    def write_batch(self, paths: list[str], metadata: dict):
        pass

    def embed_cover(self, path: str, cover_path: str):
        pass
