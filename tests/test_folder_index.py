"""Tests for folder_index — caching, file listing, subfolder listing."""

import os
import tempfile


class TestListAudioFiles:
    def test_empty_directory(self):
        from library.folder_index import list_audio_files, clear_cache
        clear_cache()
        with tempfile.TemporaryDirectory() as tmpdir:
            files = list_audio_files(tmpdir)
            assert files == []

    def test_finds_audio_files(self):
        from library.folder_index import list_audio_files, clear_cache
        clear_cache()
        with tempfile.TemporaryDirectory() as tmpdir:
            for name in ("song.mp3", "track.flac", "album/cover.jpg"):
                p = os.path.join(tmpdir, name)
                os.makedirs(os.path.dirname(p), exist_ok=True)
                open(p, "w").close()
            files = list_audio_files(tmpdir)
            paths = [os.path.basename(f) for f in files]
            assert "song.mp3" in paths
            assert "track.flac" in paths

    def test_ignores_hidden_files(self):
        from library.folder_index import list_audio_files, clear_cache
        clear_cache()
        with tempfile.TemporaryDirectory() as tmpdir:
            for name in (".hidden.mp3", "visible.mp3"):
                open(os.path.join(tmpdir, name), "w").close()
            files = list_audio_files(tmpdir)
            names = [os.path.basename(f) for f in files]
            assert ".hidden.mp3" not in names
            assert "visible.mp3" in names

    def test_ignores_non_audio(self):
        from library.folder_index import list_audio_files, clear_cache
        clear_cache()
        with tempfile.TemporaryDirectory() as tmpdir:
            for name in ("song.mp3", "doc.txt", "image.png"):
                open(os.path.join(tmpdir, name), "w").close()
            files = list_audio_files(tmpdir)
            assert len(files) == 1


class TestListSubfolders:
    def test_empty_directory(self):
        from library.folder_index import list_subfolders, clear_cache
        clear_cache()
        with tempfile.TemporaryDirectory() as tmpdir:
            assert list_subfolders(tmpdir) == []

    def test_finds_subfolders(self):
        from library.folder_index import list_subfolders, clear_cache
        clear_cache()
        with tempfile.TemporaryDirectory() as tmpdir:
            for name in ("Music", "Podcasts", ".hidden"):
                os.makedirs(os.path.join(tmpdir, name), exist_ok=True)
            dirs = list_subfolders(tmpdir)
            names = [os.path.basename(d) for d in dirs]
            assert "Music" in names
            assert "Podcasts" in names
            assert ".hidden" not in names


class TestCache:
    def test_cache_hit(self):
        from library.folder_index import list_audio_files, clear_cache, _cache
        clear_cache()
        with tempfile.TemporaryDirectory() as tmpdir:
            open(os.path.join(tmpdir, "song.mp3"), "w").close()
            list_audio_files(tmpdir)
            assert f"files:{tmpdir}" in _cache

    def test_clear_cache(self):
        from library.folder_index import list_audio_files, clear_cache, _cache
        clear_cache()
        with tempfile.TemporaryDirectory() as tmpdir:
            open(os.path.join(tmpdir, "song.mp3"), "w").close()
            list_audio_files(tmpdir)
            clear_cache()
            assert f"files:{tmpdir}" not in _cache
