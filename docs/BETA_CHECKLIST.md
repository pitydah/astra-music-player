# Michi Music Player — Beta Checklist v0.2.0

## Arranque
- [x] `python main.py` arranca sin errores
- [x] `python main.py --qml` arranca modo QML
- [x] `QT_QPA_PLATFORM=offscreen python -m ui_qml_bridge.qml_main` sin crash
- [x] Safe mode (`MICHI_SAFE_MODE=1`) arranca sin servicios remotos
- [x] MPRIS se registra en KDE

## Navegación
- [x] Sidebar QML (10 items) funciona
- [x] PageStack carga cada ruta correctamente
- [x] NavigationBridge valida rutas
- [x] Rutas inválidas caen a placeholder

## Biblioteca
- [x] Library QML: Canciones, Álbumes, Artistas, Carpetas
- [x] SearchField con bridge
- [x] AlbumGrid + AlbumDetail
- [x] ArtistList + ArtistDetail
- [x] FolderBrowser

## Reproducción
- [x] NowPlayingBar QML visible con controles
- [x] Play/pause/next/prev desde controles QML
- [x] Seek bar responde a posición/duration
- [x] Volumen ajustable
- [x] CoverBridge con fallback premium

## Mix
- [x] MixHubPage con 6 categorías
- [x] MixDetailPage con lista de canciones
- [x] MixBridge conectado a backend

## Michi AI
- [x] AssistantPage con chat funcional
- [x] ChatBubble con estilo glass
- [x] Sugerencias contextuales
- [x] PlanBuilder real (fallback a respuestas por palabra clave)

## Playlists
- [x] PlaylistsPage con grid de playlists
- [x] PlaylistDetailPage
- [x] PlaylistCard con CoverBridge
- [x] PlaylistsBridge conectado a PlaylistStore

## Radio
- [x] RadioPage con emisoras desde RadioManager
- [x] Favoritas + todas las emisoras

## Sync / Devices
- [x] DevicesPage con SyncStatusPanel
- [x] DevicesBridge conectado a SyncManager
- [x] Iniciar/detener servidor Sync
- [x] Discovery de peers

## Home Audio
- [x] HomeAudioPage con mode selector
- [x] HomeAssistantPanel + MichiMusicStreamPanel
- [x] HomeAudioBridge conectado a HA/Snapcast

## Settings
- [x] SettingsPage con 8 categorías
- [x] SettingsBridge conectado a settings_manager

## Metadata Inspector
- [x] MetadataInspectorPage con campos reales
- [x] MetadataBridge read-only + escritura segura (applyChanges)
- [x] CoverBridge integrado

## Audio Lab
- [x] AudioLabPage con stats de library_health
- [x] AudioLabBridge conectado a compute_health

## CoverBridge
- [x] QQuickPaintedItem registrado como MichiCover 1.0
- [x] paint() solo dibuja pixmap/fallback (sin DB)
- [x] Cache limitado a 256 entradas
- [x] Fallback premium con gradiente + glyph

## Sidebar QML
- [x] 10 items exactos: Inicio, Biblioteca, Mix, Reproducción, Conexiones, Radio, Playlists, Home Audio, Michi AI, Audio Lab
- [x] Sin Settings, sin Géneros, sin Ajustes

## Tests
- [x] `pytest tests/qml/ -q` — 164 tests pasan
- [x] `ruff check ./ui_qml ./ui_qml_bridge ./tests/qml` — 0 errores
- [x] `python -m compileall .` — 0 errores
- [x] `python scripts/check_no_touch_contract.py` — ALL CLEAR

## Documentación
- [x] `FEATURE_STATUS.md` actualizado
- [x] `KNOWN_ISSUES.md` con issues reales
- [x] `FINALIZATION_REPORT.md` con estado de cierre
- [x] `QML_MIGRATION_PLAN.md` con estado de migración
- [x] `DEVELOPER_GUIDE.md` con arquitectura QML
