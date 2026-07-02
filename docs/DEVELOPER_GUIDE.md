# Michi Music Player — Developer Guide

## Arquitectura general

```
main.py (entry point)
├── --qml flag → ui_qml_bridge/qml_main.py → QML UI
└── (default) → ui/window.py → QtWidgets UI

Ambos modos comparten:
├── audio/player_service.py (fachada de reproducción)
├── core/ (context, settings, home dashboard, genre)
├── library/ (SQLite, FTS5, metadata, playlists)
├── sync/ (Sync Server, protocolo, discovery)
├── integrations/michi_link/ (Michi Micro Server cliente/servidor)
└── michi_ai/ (asistente contextual con herramientas)
```

## Capa QML

```
ui_qml/                  → 86+ archivos QML
├── shell/               → AppShell, Sidebar, HeaderBar, PageStack
├── theme/               → MichiColors, Typography, Spacing, Motion
├── materials/           → Glass, Hero, Popup, Sidebar, Input
├── components/          → ActionButton, GlassCard, StatusBadge, etc.
├── pages/               → 12 rutas + placeholders
│   ├── home/            → HomePage (Centro Michi)
│   ├── library/         → Songs, Albums, Artists, Folders
│   ├── connections/     → Michi Micro Server, servidores externos
│   ├── home_audio/      → HA + Michi Music Stream
│   ├── assistant/       → Michi AI chat
│   ├── metadata/        → Metadata Inspector
│   ├── playlists/       → Playlists hub + detail
│   └── devices/         → Sync/Devices
└── effects/             → (reservado)

ui_qml_bridge/           → 21 bridges Python
├── qml_main.py          → Entry point, registra bridges y engine
├── navigation_bridge.py → VALID_ROUTES, navegación
├── cover_bridge.py      → CoverBridge (QQuickPaintedItem)
├── library_bridge.py    → Búsqueda FTS5, canciones, álbumes, artistas
├── metadata_bridge.py   → Inspector read/write (mutagen)
├── playback_bridge.py   → NowPlaying, PlayerService
├── michi_ai_bridge.py   → Chat + PlanBuilder
├── mix_bridge.py        → Mix categorías
├── playlists_bridge.py  → PlaylistStore
├── devices_bridge.py    → SyncManager
├── radio_bridge.py      → RadioManager
├── home_audio_bridge.py → HA/Snapcast
├── connections_bridge.py → MichiLinkController
├── settings_bridge.py   → settings_manager
├── audio_lab_bridge.py  → library_health
└── (app, command, theme, home, nowplaying, settings)
```

## Bridges — Propósito y conexión

| Bridge | Backend real | Props QML | Slots |
|---|---|---|---|
| navigation_bridge | VALID_ROUTES | currentRoute | navigate(route) |
| cover_bridge | QQuickPaintedItem | coverKey | — |
| library_bridge | SongsQueryService | songs, albums, artists, folders | search, refresh, sortBy, filterByArtist, filterByAlbum |
| metadata_bridge | mutagen | fields, trackTitle, canApply | inspectTrack, applyChanges |
| playback_bridge | PlayerService | trackTitle, isPlaying, volume, position | togglePlay, next, prev, seek, setVolume |
| michi_ai_bridge | MichiAIContextBridge, PlanBuilder | suggestions | sendMessage, refresh |
| mix_bridge | Mock (DB opcional) | categories, currentSongs | loadMix |
| playlists_bridge | PlaylistStore | playlists | refresh |
| devices_bridge | SyncManager | serverActive, peers, pairedDevices | startServer, stopServer, refresh |
| radio_bridge | RadioManager | stations, favorites | refresh, addStation |
| home_audio_bridge | HomeAudioController, SnapcastController | homeAssistantState, devices | refresh |
| connections_bridge | MichiLinkController | microServerState, discoveredServers | scanForServers, refresh |
| settings_bridge | settings_manager | sections | get(key), set(key, value) |
| audio_lab_bridge | compute_health | totalTracks, missingMetadata, modules | refresh |

## Rutas QML

| Ruta | Componente | Sidebar |
|---|---|---|
| home | HomePage | ✅ |
| library | LibraryPage (tabs) | ✅ |
| mix | MixHubPage | ✅ |
| playback | PlaybackPage | ✅ |
| connections | ConnectionsPage | ✅ |
| radio | RadioPage | ✅ |
| playlists | PlaylistsPage | ✅ |
| home_audio | HomeAudioPage | ✅ |
| assistant | AssistantPage (Michi AI) | ✅ |
| audio_lab | AudioLabPage | ✅ |
| metadata_inspector | MetadataInspectorPage | ❌ (interna) |
| mix_detail | MixDetailPage | ❌ (interna) |
| settings | SettingsPage | ❌ (interna) |
| devices | DevicesPage | ❌ (interna) |
| playlist_detail | PlaylistDetailPage | ❌ (interna) |

## Sidebar final (10 items)
```
Inicio, Biblioteca, Mix, Reproducción, Conexiones, Radio,
Playlists, Home Audio, Michi AI, Audio Lab
```

Sin Settings, sin Géneros, sin Ajustes.

## Cómo ejecutar

```bash
# QML experimental
python main.py --qml
python -m ui_qml_bridge.qml_main

# QtWidgets (fallback)
python main.py

# Tests QML
python -m pytest tests/qml/ -q

# Lint solo QML/bridge
ruff check ./ui_qml ./ui_qml_bridge ./tests/qml
```

## Cómo agregar un bridge nuevo

1. Crear `ui_qml_bridge/mi_bridge.py` con clase que hereda de QObject
2. Definir Properties (notify) y Slots
3. Registrar en `ui_qml_bridge/qml_main.py`:
   - Importar la clase
   - Instanciar con dependencias opcionales
   - `engine.rootContext().setContextProperty("miBridge", instancia)`
4. Usar en QML: `property var miBridge: typeof miBridge !== "undefined" ? miBridge : null`

## Reglas QML
- No opacity en padres con texto
- No blur en listas/grids/tablas
- No sombras por item
- No emojis como iconografía
- Usar theme tokens (MichiColors, MichiSpacing, etc.)
- CoverBridge para carátulas
- paint() nunca debe hacer DB reads ni decode de imágenes
