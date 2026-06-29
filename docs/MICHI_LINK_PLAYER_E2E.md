# Michi Link — E2E Guide (Player → Mobile)

## Server status

Michi Music Player implements **Michi Link API v1.0.0-alpha** as a server.

| Field | Value |
|-------|-------|
| `service` | `michi-music-player` |
| `api_version` | `v1` |
| `michi_link_version` | `1.0.0-alpha` |
| `auth.strategy` | `PLAYER_PASSWORD` |
| `auth.token_refresh` | `false` |
| `features.events` | `false` |
| `features.receivers` | `false` |
| `features.rooms` | `false` |

## Endpoints ready for Mobile

### Public (no auth)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/v1/server/info` | Server metadata, auth strategy, features |
| GET | `/api/v1/status` | Server status, sync active |
| POST | `/api/v1/pair/start` | Start pairing, returns auth_methods |
| POST | `/api/v1/pair/confirm` | Confirm pairing with username+password |

### Protected (Bearer token + X-Michi-Device-Id)

| Method | Path | Permission |
|--------|------|------------|
| GET | `/api/v1/tracks` | `library.read` |
| GET | `/api/v1/search?q=...` | `library.read` |
| GET | `/api/v1/library/stats` | `library.read` |
| GET | `/api/v1/stream/{track_id}` | `stream.read` |
| GET | `/api/v1/artwork/{cover_id}` | `artwork.read` |
| GET | `/api/v1/sync/manifest?device_id=...` | `sync.read_manifest` |
| GET | `/api/v1/sync/manifest/delta?device_id=...&cursor=...` | `sync.read_manifest` |
| POST | `/api/v1/sync/state` | `sync.upload_state` |
| GET | `/api/v1/playback/state` | `playback.read` |
| POST | `/api/v1/playback/control` | `playback.control` |
| GET | `/api/v1/queue` | `queue.read` |
| POST | `/api/v1/queue/jump` | `queue.write` |
| POST | `/api/v1/queue/items` | `queue.write` |

### Not yet implemented (return NOT_IMPLEMENTED)

| Method | Path | Reason |
|--------|------|--------|
| POST | `/api/v1/token/refresh` | `auth.token_refresh=false` |
| GET | `/api/v1/events` | SSE not implemented, use polling |

## How to test with Mobile

### 1. Start server

1. Open Michi Music Player on desktop.
2. Go to Devices → Michi Sync Suite.
3. Click **Activar Michi Sync**.
4. (Optional) Click **Crear cuenta local** to enable password-based pairing.
5. Note the IP and port (default: 53318).

### 2. Pair from Mobile

1. Open Michi Music Mobile.
2. Server discovery shows "Michi Music Player" on LAN.
3. Mobile calls `GET /api/v1/server/info` → sees `auth.strategy=PLAYER_PASSWORD`.
4. Mobile calls `POST /api/v1/pair/start` → gets `auth_required=true`, `auth_methods=["password"]`.
5. User enters Player's local username + password.
6. Mobile calls `POST /api/v1/pair/confirm` with `client_device_id`, `username`, `password`.
7. Player responds with `device_token`, `device_id`, `permissions`.
8. Mobile stores token and device_id.

### 3. Use API

All subsequent requests need:
```
Authorization: Bearer <device_token>
X-Michi-Device-Id: <device_id>
```

### 4. Stream a track

```
GET /api/v1/stream/{track_id}
Range: bytes=0-1023    (optional, returns 206)
No Range → returns 200
```

### 5. Control playback

```json
POST /api/v1/playback/control
{
  "command": "play"
}
```

Supported commands: `play`, `pause`, `toggle`, `next`, `previous`, `stop`, `seek`, `set_volume`, `mute`, `unmute`, `shuffle`, `repeat`.

Seek uses `position_ms`:
```json
{"command": "seek", "position_ms": 90000}
```

Volume uses `volume` (0-100):
```json
{"command": "set_volume", "volume": 70}
```

### 6. Read queue

```
GET /api/v1/queue
```

Response does NOT expose local file paths. Tracks have `download_path` pointing to `/api/v1/stream/{track_id}`.

## Future endpoints (Phase 2-3: Player → Micro Server)

These will be implemented when Player acts as client to a remote Micro Server:

- `create_import_session()` — start a bulk import
- `upload_track()` — send a track to Micro Server
- `commit_import()` — finalize import
- `playback_session_continue_on_server()` — hand off queue to Micro Server

## What remains for Player → Micro Server

| Module | Status |
|--------|--------|
| `integrations/michi_link/client.py` | Ready — `MichiLinkClient` with discover, pair, library, control |
| `integrations/michi_link/micro_server_client.py` | Stub with method signatures |
| `integrations/michi_link/import_client.py` | Stub with method signatures |
| `integrations/michi_link/remote_library_provider.py` | Stub — will provide tracks from remote as browsable source |
| UI wiring | Not started — will go through controllers, not window.py |

## Contract reference

All v1 errors follow this format:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable description",
    "details": {}
  }
}
```

HTTP status codes used: 200, 206, 400, 401, 403, 404, 429, 500, 501, 503.

File paths are NEVER exposed in JSON responses. All track references use `track_id` and `download_path` API routes.
