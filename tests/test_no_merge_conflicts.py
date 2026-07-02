"""Verify no Git merge conflict markers remain in source files."""

from pathlib import Path


_MARKERS = ("<<<<<<<", "=======", ">>>>>>>")

_EXCLUDED_DIRS = {
    ".git", "__pycache__", ".venv", ".pytest_cache",
    ".ruff_cache", ".mypy_cache", "node_modules", "dist", "build",
}

_EXCLUDED_EXTENSIONS = {
    ".pyc", ".pyo", ".so", ".dll", ".dylib",
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico",
    ".ttf", ".otf", ".woff", ".woff2",
    ".db", ".sqlite",
    ".lock", ".whl",
}


def test_no_git_conflict_markers():
    bad = []
    root = Path(".")
    for path in root.rglob("*"):
        if any(part.startswith(".") for part in path.parts):
            continue
        if any(excluded in path.parts for excluded in _EXCLUDED_DIRS):
            continue
        if path.suffix in _EXCLUDED_EXTENSIONS:
            continue
        if not path.is_file():
            continue
        try:
            text = path.read_text(errors="ignore")
        except Exception:
            continue
        for marker in _MARKERS:
            if marker in text:
                for lineno, line in enumerate(text.split("\n"), 1):
                    stripped = line.strip()
                    if stripped.startswith(marker):
                        bad.append(f"{path}:{lineno}: {stripped[:80]}")
                        break
    assert not bad, f"Git conflict markers found ({len(bad)}):\n" + "\n".join(bad)
