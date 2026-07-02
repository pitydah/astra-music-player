#!/usr/bin/env python3
"""Verify no protected files were modified in the current branch.

Exit codes:
  0 = all clear
  1 = protected files modified
"""

import subprocess
import sys

BASE = "HEAD~30"

PROTECTED = [
    "sync/",
    "ui/nowplaying_bar.py",
    "ui/source_status_badge.py",
    "audio/player.py",
    "audio/player_service.py",
    "audio/pipeline_factory.py",
    "core/playback_controller.py",
]

CONDITIONAL = {
    "integrations/michi_link/": "Playlists API (conditional)",
    "library/playlists/": "Playlists backend (conditional)",
}


def get_modified_files() -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", f"{BASE}..HEAD"],
        capture_output=True, text=True, check=True,
    )
    return [f.strip() for f in result.stdout.split("\n") if f.strip()]


def main():
    modified = get_modified_files()
    violations = []

    for pattern in PROTECTED:
        for f in modified:
            if f.startswith(pattern) or f == pattern:
                violations.append(f)

    if violations:
        print("NO-TOUCH CONTRACT VIOLATION")
        print("Protected files modified:")
        for v in violations:
            print(f"  {v}")
        sys.exit(1)

    print("NO-TOUCH CONTRACT: ALL CLEAR")
    print(f"Total files modified: {len(modified)}")

    for pattern, label in CONDITIONAL.items():
        found = [f for f in modified if f.startswith(pattern)]
        if found:
            print(f"Conditional: {label} — {len(found)} file(s)")
            for f in found:
                print(f"  {f}")

    sys.exit(0)


if __name__ == "__main__":
    main()
