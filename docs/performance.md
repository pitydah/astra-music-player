# Performance Testing

Current status: **preliminary synthetic suite**.

The generator creates empty placeholder files and uses `LibraryDB.add_file()`.
This is useful for smoke-level performance checks, but it also measures file creation,
metadata fallback and indexing overhead. It is **not** yet a pure database benchmark.

Future improvement:
- replace file-based generation with `BatchWriter` or direct synthetic DB insert helper;
- add 10k/50k datasets;
- separate generation time from query timings.

## Running

```bash
# All perf tests
pytest tests/perf/ -m perf -v

# Specific test
pytest tests/perf/test_library_perf.py -m perf -v -k test_get_all_tracks
```

## Thresholds (5,000 tracks)

| Operation | Threshold |
|---:|---:|
| get_all | < 2.5s |
| search_advanced | < 1.0s |
| get_stats | < 1.0s |
| cleanup_missing_under_root | < 0.2s |

## Generating Synthetic Data

```python
from tests.perf.generate_library import generate
from library.library_db import LibraryDB
import tempfile
db = LibraryDB(":memory:")
generate(db, root=str(tempfile.mkdtemp()), count=5_000)
```
