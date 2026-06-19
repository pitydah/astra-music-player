"""Folder Index — directory-based navigation for audio files."""

import os


def list_audio_files(directory: str) -> list[str]:
    """List all audio files in a directory (non-recursive)."""
    exts = {".mp3", ".flac", ".ogg", ".wav", ".m4a", ".aac", ".opus",
            ".dsf", ".dff", ".aiff", ".ape", ".wv", ".wma", ".spx"}
    files = []
    try:
        for f in sorted(os.listdir(directory)):
            if not f.startswith("."):
                full = os.path.join(directory, f)
                if os.path.isfile(full):
                    if os.path.splitext(f)[1].lower() in exts:
                        files.append(full)
    except PermissionError:
        pass
    return files


def list_subfolders(directory: str) -> list[str]:
    """List subdirectories (non-recursive)."""
    dirs = []
    try:
        for f in sorted(os.listdir(directory)):
            if not f.startswith("."):
                full = os.path.join(directory, f)
                if os.path.isdir(full):
                    dirs.append(full)
    except PermissionError:
        pass
    return dirs


def get_audio_tree(root: str, max_depth: int = 3) -> dict:
    """Return a nested dict of {name: {files: [...], folders: {...}}}."""
    result = {"files": list_audio_files(root), "folders": {}}
    if max_depth <= 0:
        return result
    for folder in list_subfolders(root):
        name = os.path.basename(folder)
        result["folders"][name] = get_audio_tree(folder, max_depth - 1)
    return result
