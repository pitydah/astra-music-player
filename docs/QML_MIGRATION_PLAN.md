# Michi Music Player — QML Migration Plan

## Objective
Migrate Michi Music Player UI from QtWidgets to Qt Quick (QML) progressively,
without rewriting the entire app, without breaking the existing QtWidgets UI,
and without touching playback, sync, or Android integration.

## Hybrid Architecture

```
┌──────────────────────────────────────────────┐
│  main.py (QtWidgets)        qml_main.py (QML) │
│  ┌──────────────────┐   ┌──────────────────┐ │
│  │ QtWidgets UI     │   │ Qt Quick / QML   │ │
│  │ (fallback stable) │   │ (premium skin)   │ │
│  └──────┬───────────┘   └──────┬───────────┘ │
│         │                      │              │
│         ▼                      ▼              │
│  ┌──────────────────────────────────────────┐ │
│  │ Python / PySide6 (brain)                 │ │
│  │ ui_qml_bridge/ (bridges)                 │ │
│  │ core/ library/ audio/ (untouched)        │ │
│  └──────────────────────────────────────────┘ │
└──────────────────────────────────────────────┘
```

## What stays in Python
- All business logic (playback, DB, sync, recognition, etc.)
- All existing QtWidgets UI
- All controllers, services, and models
- Audio engine, pipeline, GStreamer, MPD

## What goes to QML
- New premium visual layer (ui_qml/)
- Bridges layer (ui_qml_bridge/) connecting QML to Python
- Theme, materials, components, shell, pages

## How to run QML
```bash
python -m ui_qml_bridge.qml_main
```

## How to run classic app
```bash
python main.py
```

## Phases Completed (Foundation)

| Phase | Description | Status |
|-------|-------------|--------|
| 0 | Baseline & safe branch | ✅ |
| 1 | QML directory structure | ✅ |
| 2 | Theme QML (Colors, Typography, Spacing, Motion) | ✅ |
| 3 | Glass Materials (Glass, Hero, Popup, Sidebar, Input, Acrylic) | ✅ |
| 4 | Base Components (GlassPanel, GlassCard, ActionButton, StatusBadge, etc.) | ✅ |
| 5 | Shell (AppShell, Sidebar, HeaderBar, PageStack) | ✅ |
| 6 | Bridges (AppBridge, NavigationBridge, CommandBus, ThemeBridge) | ✅ |
| 7 | Home QML (Hero, Continue, Library, Ecosystem, Assistant cards) | ✅ |
| 8 | Connections QML (MicroServerHero, external servers, discovery) | ✅ |
| 9 | Home Audio QML (HA panel, Michi Music Stream, zones, receivers) | ✅ |
| 10 | Placeholders (Library, Assistant, AudioLab, Settings) | ✅ |
| 11 | Documentation | ✅ |
| 12 | Tests & smoke validation | ✅ |

## Next Phases (Recommended)
1. **Library QML** — models, grids, lists, search
2. **Assistant QML** — real assistant page with chat UI
3. **ImageProvider** — cover art from Python to QML
4. **Metadata híbrido** — InspectorPanel with real data
5. **Audio Lab QML**
6. **NowPlayingBar QML** (last, most complex)

## Performance Rules (QML)
- No blur on list/grid/table items
- No shadows per item in lists/grids/tables
- No opacity on parent containers with text
- Use `Loader` for page lazy loading
- Lightweight delegates for data lists
- Future: ImageProvider for cover art (no base64 in QML)

## Contrast Rules
- TextPrimary: #F0F2F8 on bgApp #070A10 → ratio ~14:1
- TextSecondary: #D0D4E0 on bgApp #070A10 → ratio ~10:1
- TextMuted: #606878 on bgApp #070A10 → ratio ~5:1 (for non-critical text)
- AccentBlue: #8FB7FF on bgApp #070A10 → ratio ~7:1

## Do Not Touch (Protected)
- `ui/devices_page.py`
- `sync/` (entire directory)
- `sync_protocol.py`, `sync_server.py`, `sync_manager.py`
- Android integration
- `ui/nowplaying_bar.py`
- `ui/source_status_badge.py`
- Playback logic (`audio/player.py`, `audio/player_service.py`)
- `audio/pipeline_factory.py`
- `core/playback_controller.py`
- User database
- Existing SQLite migrations

## QML Migration Rules (for AI assistants)
1. QML does NOT access the database directly
2. QML emits intention; Python executes
3. Do NOT touch Sync or Android
4. Do NOT touch playback
5. No `opacity` on parent containers with text
6. No blur on lists/grids/tables
7. No per-item shadows in lists/grids/tables
8. Keep fallback QtWidgets intact
9. No fake data shown as real — use "No configurado", "Demo QML", "Experimental"
10. Theme tokens preferred over hardcoded colors
