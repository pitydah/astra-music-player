# Player ↔ Micro Server Quality Leap

## Audit results

| Check | Result |
|-------|--------|
| Qt/PySide imports in services | 0 violations |
| window.py / MainWindow refs | 0 violations |
| All services return Result | ✅ (except DiagnosticsService which returns dicts) |
| v1 error format (code, message) | ✅ |
| HTTP timeouts on all requests | ✅ (5s-60s depending on operation) |
| urllib.error exceptions caught | ✅ |

## Service layer overview

```
services/
├── result.py                 → Result(ok, code, message, data, error)
├── micro_server_service.py   → discover, pair, test_connection, library, control
├── import_to_server_service.py → session-based import with push/pull
├── continue_on_server_service.py → queue transfer + remote control
├── remote_library_service.py → browse remote tracks
├── diagnostics_service.py    → health report
```

## Key improvements

1. **Push model for imports**: Player POSTs track data to Micro Server (faster, simpler).
2. **Pull model fallback**: Micro Server can also fetch from Player's stream endpoint.
3. **Hash verification**: SHA-256 computed before upload, sent in `X-Checksum` header.
4. **Session lifecycle**: create → upload → commit/rollback, with progress callback.
5. **Continue on Server**: reads Player queue, resolves tracks, transfers, pauses local.
6. **Latency tracking**: `test_connection` measures response time in milliseconds.
7. **No Qt**: zero PySide/PyQt imports in the services directory.
