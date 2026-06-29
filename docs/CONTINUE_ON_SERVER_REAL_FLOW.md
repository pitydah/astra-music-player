# Continue on Server — Real Flow

## Sequence

```
Player                          Micro Server
  │                                  │
  │  1. Read local queue             │
  │     queue_provider() →           │
  │     (track_ids, idx, pos)        │
  │                                  │
  │  2. Resolve track_ids            │
  │     resolve_track(t) → id        │
  │                                  │
  │  3. POST /api/v1/queue/transfer ─┤
  │     { track_ids,                 │
  │       current_index,             │
  │       position_ms,               │
  │       source }                   │
  │                                  │
  │  4.  ← 200 { ok: true }          │
  │                                  │
  │  5. Pause local playback         │
  │     pause_local()                │
  │                                  │
  │  6. POST /api/v1/playback/control┤
  │     { command: "play" }          │
  │                                  │
  │  7.  ← 200 { status: "ok" }      │
  │                                  │
  │  [Micro Server starts            │
  │   streaming from                 │
  │   Player's stream endpoint]      │
  │                                  │
  │  8. POST /api/v1/playback/control┤  (on user stop)
  │     { command: "stop" }          │
```

## Error handling

| Failure point | Player behavior |
|---------------|-----------------|
| Queue transfer fails | Do NOT pause local. Return Result.fail("TRANSFER_FAILED") |
| Remote play fails | Queue was transferred but not playing. User can start manually from Micro |
| Local pause fails | Log warning, continue anyway |

## Service configuration

```python
svc = ContinueOnServerService(
    queue_provider=get_current_queue,  # () → (track_ids, index, position_ms)
    pause_local=pause_playback,         # () → None
    resolve_track=resolve_to_stream_id  # (str) → str
)
```
