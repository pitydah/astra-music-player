# Feature Status — Michi Music Player v0.2.0-beta

| Área | Estado | Ruta | Tests | Acción |
|---|---|---|---|---|
| **Versión** | `0.2.0-beta` | — | 164 QML + suite completa | Release |
| **QML Foundation** | ✅ 100% | 86+ archivos, 21 bridges, sidebar final | 164 | Mantener |
| **Sidebar QML** | ✅ 100% | 10 items, sin settings, sin géneros | ✅ | Mantener |
| **NavigationBridge** | ✅ 100% | VALID_ROUTES controladas | ✅ | Mantener |
| **CoverBridge** | ✅ 100% | QQuickPaintedItem, cache 256, paint sin DB | ✅ | Mantener |
| **Library QML** | ✅ 90% | Canciones, Álbumes, Artistas, Carpetas, Search, Sort, Filter | ✅ | Pulir |
| **Mix QML** | ✅ 80% | 6 categorías, hub, detalle, MixBridge | ✅ | Tests reales |
| **Michi AI** | ✅ 75% | Chat funcional + PlanBuilder real | ✅ | Mejorar respuestas |
| **NowPlayingBar QML** | ✅ 90% | Barra inferior, controles, seek, volumen, cover | ✅ | Conectar PlayerService |
| **Metadata Inspector** | ✅ 80% | Read-only + escritura segura (applyChanges) | 164 | UI pulido |
| **Audio Lab QML** | ✅ 70% | Bridge con library_health stats | 164 | UI pulido |
| **Playlists QML** | ✅ 80% | Hub + detail + PlaylistStore real | 164 | UI pulido |
| **Sync/Devices QML** | ✅ 70% | DevicesPage + SyncManager real | 164 | UI pulido |
| **Settings QML** | ✅ 70% | Bridge + settings_manager real | 164 | UI pulido |
| **Radio QML** | ✅ 60% | Bridge + RadioManager real | 164 | UI pulido |
| **Home Audio QML** | ✅ 60% | Bridge + HA/Snapcast real | 164 | UI pulido |
| **ContextMenu QML** | ✅ 50% | SongContextMenu básico | 164 | Expandir |
| **Michi Link UI** | ✅ 85% | ConnectionsBridge + MichiLinkController real | 164 | UI pulido |
| **QtWidgets (fallback)** | ✅ 100% | `python main.py` funciona | suite | Mantener |
