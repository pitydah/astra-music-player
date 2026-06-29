# Player Service Layer — Reference

## Architecture

```
┌─────────────────────────────────────────────┐
│             UI Controllers                   │
│  (No window.py, no Qt in services)          │
├─────────────────────────────────────────────┤
│             Service Layer                    │
│  integrations/michi_link/services/          │
├─────────────────────────────────────────────┤
│             Client Layer                     │
│  integrations/michi_link/client.py          │
│  integrations/michi_link/micro_server_client│
├─────────────────────────────────────────────┤
│  urllib.request  (no aiohttp, no requests)  │
└─────────────────────────────────────────────┘
```

## Result object

```python
@dataclass
class Result:
    ok: bool
    code: str       # "OK" | "DISCOVERY_FAILED" | "PAIR_FAILED" | ...
    message: str    # Human-readable
    data: Any       # Payload on success
    error: str | None  # Error detail
```

## Service reference

### MicroServerService

| Method | Description | Timeout |
|--------|-------------|---------|
| `discover(host, port)` | GET /api/v1/server/info | 5s (via client) |
| `discover_servers([(h,p)])` | Bulk discover | 5s each |
| `test_connection(server)` | GET /api/v1/status | 5s |
| `get_capabilities(server)` | Returns server metadata | — |
| `pair(server, user, pass)` | POST /api/v1/pair/confirm | 10s |
| `pair_start(server)` | POST /api/v1/pair/start | 10s |
| `get_tracks(server)` | GET /api/v1/tracks | 10s |
| `get_library_stats(server)` | GET /api/v1/library/stats | 10s |
| `search(server, query)` | GET /api/v1/search | 10s |
| `get_playback_state(server)` | GET /api/v1/playback/state | 10s |
| `get_queue(server)` | GET /api/v1/queue | 10s |
| `control(server, cmd, **kw)` | POST /api/v1/playback/control | 10s |
| `create_import_session(server)` | POST /api/v1/import/session/create | 15s |

### ImportToServerService

| Method | Description | Timeout |
|--------|-------------|---------|
| `create_session(server, track_ids)` | Start import | — |
| `upload_track(sid, tid, local_data=)` | POST binary to Micro | 60s |
| `upload_artwork(sid, cover_id, path)` | Read local artwork | — |
| `upload_playlist(sid, playlist)` | Queue playlist metadata | — |
| `commit(sid)` | Finalize | — |
| `rollback(sid)` | Cancel | — |
| `status(sid)` | Progress | — |

### ContinueOnServerService

| Method | Description | Timeout |
|--------|-------------|---------|
| `transfer_queue(server, ids, ms)` | Send queue to Micro, pause local | 15s |
| `start_remote_playback(server)` | Tell Micro to start playing | 10s |
| `stop_remote_playback(server)` | Stop remote | 10s |

### RemoteLibraryService

| Method | Description |
|--------|-------------|
| `browse_tracks(server, offset, limit)` | Paginated remote tracks |
| `search(server, query)` | Remote search |
| `get_track_count(server)` | Total count |

### DiagnosticsService

| Method | Description |
|--------|-------------|
| `generate_report(...)` | Full health report (dict) |
| `check_player_api(handler)` | /api/v1/server/info |
| `check_sync_server(handler)` | Server running? |
| `check_pairing(registry)` | Devices, paired, revoked |
| `check_stream(handler)` | Track index built? |
| `check_playback(ps)` | Current state |
| `check_queue(ps)` | Queue length |
| `check_remote_micro(host, port)` | Micro Server reachable? |
| `check_micro_import(host, port)` | Import available? |
| `check_continue_readiness(ps)` | Has queue to continue? |

## Error codes

| Code | Service | Meaning |
|------|---------|---------|
| DISCOVERY_FAILED | MicroServerService | Cannot reach server |
| CONNECTION_FAILED | MicroServerService | Ping/status failed |
| PAIR_FAILED | MicroServerService | Pairing rejected |
| PAIR_START_FAILED | MicroServerService | pair/start error |
| LIBRARY_FAILED | MicroServerService | GET /api/v1/tracks failed |
| STATS_FAILED | MicroServerService | GET /api/v1/library/stats failed |
| SEARCH_FAILED | MicroServerService | Search error |
| STATE_FAILED | MicroServerService | Playback state error |
| QUEUE_FAILED | MicroServerService | Queue error |
| CONTROL_FAILED | MicroServerService | Command rejected |
| IMPORT_SESSION_FAILED | MicroServerService | Session create error |
| INVALID_SESSION | ImportToServerService | Session ID not found |
| NO_DATA | ImportToServerService | No file/data provided |
| FILE_READ_ERROR | ImportToServerService | Cannot read local file |
| UPLOAD_FAILED | ImportToServerService | HTTP error during upload |
| HAS_ERRORS | ImportToServerService | Commit blocked by errors |
| ARTWORK_NOT_FOUND | ImportToServerService | Artwork file missing |
| ARTWORK_READ_ERROR | ImportToServerService | Cannot read artwork |
| SESSION_NOT_FOUND | ImportToServerService | Status query failed |
| TRANSFER_FAILED | ContinueOnServerService | Queue transfer failed |
| REMOTE_PLAY_FAILED | ContinueOnServerService | Remote play failed |
| REMOTE_STOP_FAILED | ContinueOnServerService | Remote stop failed |
