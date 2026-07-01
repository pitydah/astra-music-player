# Runtime Budget — QML Experimental

## RAM Target (QML mode)
- No automatic measurement tool required for foundation phase.
- Guidelines:
  - No blur per item in lists/grids/tables
  - No shadows per item
  - `Loader` for page lazy loading
  - Lightweight delegates for data lists
  - ImageProvider (future) for cover art — no base64 in QML

## Measurement Commands
```bash
# Process memory
ps -p $(pgrep -f qml_main) -o rss,vsz

# Detailed memory
smem -p -P "python.*qml_main"

# GPU (if AMD)
radeontop

# Execution time
/usr/bin/time -v python -m ui_qml_bridge.qml_main 2>&1 | grep -E "Maximum resident|User time|System time"
```

## Performance Rules
1. No blur on list/grid/table items
2. No shadows per item in lists/grids/tables
3. No opacity on parent containers with text
4. Use Loader for page lazy loading
5. Lightweight delegates for data lists
6. Future: ImageProvider for cover art
