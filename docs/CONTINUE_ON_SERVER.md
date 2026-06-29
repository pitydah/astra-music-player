# Continue on Server — Playback Handoff

## Overview

The "Continue on Server" feature allows Michi Music Player to hand off its current playback queue to a paired Michi Micro Server. The Micro Server then streams tracks from the Player and continues playback independently.

## Flow

1. Player has an active queue
2. User selects "Continue on Server"
3. Player calls `transfer_queue(server, track_ids, position_ms)` — sends the queue to Micro Server
4. Player calls `start_remote_playback(server)` — instructs Micro Server to play
5. Micro Server streams each track from Player's `/api/v1/stream/{track_id}`
6. User can call `stop_remote_playback(server)` to stop

## Service API

```
POST /api/v1/queue/transfer
  Body: { "track_ids": [...], "position_ms": 0.0, "source": "michi-music-player" }
  Response: { "ok": true }
```

## Implementation status

| Component | Status |
|-----------|--------|
| Player transfer_queue() | ✅ Implemented with mock test |
| Player start_remote_playback() | ✅ Implemented with mock test |
| Player stop_remote_playback() | ✅ Implemented with mock test |
| Micro Server /api/v1/queue/transfer | ❌ Not yet implemented |
| Micro Server stream from Player | ❌ Not yet implemented |

## Test coverage

18 tests in `tests/e2e/test_player_micro_import_flow.py`
