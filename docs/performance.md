# Performance Testing

## Running

```bash
# All perf tests
pytest tests/perf/ -m perf -v

# Specific test
pytest tests/perf/test_library_perf.py -m perf -v -k test_get_all_tracks
```

## Thresholds

| Operation | Threshold | Notes |
|-----------|-----------|-------|
| `get_all_tracks` (10k) | < 2.5s | Ordered by title |
| `search_tracks` (10k) | < 1.0s | FTS5 prefix search |
| `get_stats` (10k) | < 1.0s | Counts, durations |
| `cleanup_missing` | < 0.2s | Non-existent root |
| `get_albums` (10k) | < 2.0s | All albums |

## Generating Synthetic Data

```python
from tests.perf.generate_library import generate
from library.library_db import LibraryDB
db = LibraryDB(":memory:")
generate(db, count=10_000)
```
