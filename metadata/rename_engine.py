"""Rename engine — preview and rename files based on tag patterns."""
import os

from metadata.tag_model import TrackTags


_PATTERNS = {
    "%artist%/%album%/%track% - %title%":
        lambda t: f"{t.artist}/{t.album}/{t.tracknumber} - {t.title}",
    "%albumartist%/%album%/%track% - %title%":
        lambda t: f"{t.albumartist or t.artist}/{t.album}/{t.tracknumber} - {t.title}",
    "%genre%/%artist%/%album%/%track% - %title%":
        lambda t: f"{t.genre}/{t.artist}/{t.album}/{t.tracknumber} - {t.title}",
    "%artist% - %album%/%track% - %title%":
        lambda t: f"{t.artist} - {t.album}/{t.tracknumber} - {t.title}",
    "%artist% - %title%":
        lambda t: f"{t.artist} - {t.title}",
    "%track% - %title%":
        lambda t: f"{t.tracknumber} - {t.title}",
}


def _sanitize(name: str) -> str:
    """Remove unsafe filename characters."""
    for ch in '<>:"/\\|?*':
        name = name.replace(ch, "")
    return name.strip().strip(".")


def preview_rename(items: list[TrackTags], pattern: str) -> list[tuple[str, str]]:
    """Generate (old_path, new_path) pairs for preview. Does not rename."""
    results = []
    fn = _PATTERNS.get(pattern)
    if not fn:
        return results

    for t in items:
        old = t.filepath
        ext = os.path.splitext(old)[1]
        base_dir = os.path.dirname(old)
        relative = _sanitize(fn(t))
        new = os.path.join(base_dir, relative + ext)
        results.append((old, new))
    return results


def apply_rename(preview: list[tuple[str, str]]) -> tuple[int, int]:
    """Actually rename files. Returns (success_count, fail_count)."""
    ok = 0
    fail = 0
    for old, new in preview:
        if old == new:
            continue
        try:
            os.makedirs(os.path.dirname(new), exist_ok=True)
            os.rename(old, new)
            ok += 1
        except OSError:
            fail += 1
    return ok, fail
