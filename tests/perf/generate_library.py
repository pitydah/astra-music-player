"""Generate a synthetic library of tracks for performance testing."""

import random
import string
import time
from pathlib import Path


def random_title(length: int = 10) -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def generate(db, root: str, count: int = 10_000):
    """Create synthetic audio files via db.add_file()."""
    start = time.perf_counter()
    root_path = Path(root)
    root_path.mkdir(parents=True, exist_ok=True)

    for i in range(count):
        artist_dir = root_path / f"Artist_{random.randint(0, count // 100)}"
        album_dir = artist_dir / f"Album_{random.randint(0, count // 50)}"
        album_dir.mkdir(parents=True, exist_ok=True)
        fp = str(album_dir / f"track_{i:06d}.flac")
        Path(fp).write_text("")

        db.add_file(fp)

        if (i + 1) % 1000 == 0:
            print(f"  generated {i + 1} / {count}")
            db.rebuild_indexes()

    db.rebuild_indexes()
    elapsed = time.perf_counter() - start
    print(f"  done in {elapsed:.2f}s")
    return elapsed
