# Player → Micro Server Import Protocol

## Overview

Michi Music Player can import tracks into a paired Michi Micro Server using a session-based protocol.

## Flow

1. **Discover** — Player calls `GET /api/v1/server/info` on Micro Server
2. **Pair** — Player calls `POST /api/v1/pair/start` → `POST /api/v1/pair/confirm`
3. **Create session** — Player calls `create_import_session()` with track list
4. **Upload tracks** — Player calls `upload_track(session_id, track_id, download_path)` for each track.
   The Micro Server streams the track from the Player's stream endpoint.
5. **Commit** — Player calls `commit_session(session_id)` to finalize
6. **Rollback** — If any track fails, Player calls `rollback_session(session_id)`

## API between Player and Micro Server (future)

The Micro Server should implement:

```
POST /api/v1/import/session/create
POST /api/v1/import/track/upload
POST /api/v1/import/session/commit
POST /api/v1/import/session/rollback
```

## Services

| Service | Method | Description |
|---------|--------|-------------|
| ImportToServerService | `create_session(server, track_ids)` | Start import session |
| ImportToServerService | `upload_track(session_id, track_id, download_path)` | Stream track to Micro Server |
| ImportToServerService | `commit_session(session_id)` | Finalize import |
| ImportToServerService | `rollback_session(session_id)` | Cancel import |

## Continue on server

After import, Player can hand off playback:

| Service | Method | Description |
|---------|--------|-------------|
| ContinueOnServerService | `transfer_queue(server, track_ids, position_ms)` | Send queue to Micro Server |
| ContinueOnServerService | `start_remote_playback(server)` | Start playing on Micro Server |
| ContinueOnServerService | `stop_remote_playback(server)` | Stop playing on Micro Server |
