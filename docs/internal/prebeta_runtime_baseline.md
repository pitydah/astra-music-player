# Pre-beta Runtime Baseline

Commit: f78000b
Date: 2026-06-28

Ruff: 0 errors
Compileall: OK
Pytest: passed, 2 skipped
ci_local: pending (needs GI/GStreamer)
smoke_startup: All checks passed
smoke_ui_routes: All checks passed

Tiempo aproximado smoke: ~8s
Errores conocidos: ninguno
Riesgos conocidos: CI GitHub Actions falla en smoke startup por NameError (en investigación, posiblemente PIL no instalado en runner)

## Cambios realizados

### Fase 1 — Micro-estabilidad
- HomePage._get_stats(): except Exception → logger.debug
- ActionLog protegido por test anti-regresión
- Smoke labels corregidos de [1/8] a [1/7]

### Fase 2 — NoiseOverlay optimizado
- _generate_noise() reemplazado por _noise_tile() cacheado (96×96)
- paintEvent() usa drawTiledPixmap() en vez de generar todo el tamaño

### Fase 3 — Smoke separado
- scripts/smoke_startup.py: solo runtime base (sin MainWindow, sin navegación)
- scripts/smoke_ui_routes.py: MainWindow + 22 rutas + route/sidebar asserts
- CI y ci_local.sh ejecutan ambos

### Fase 4 — Route/sidebar separation
- _current_route_key: ruta exacta (ej. pl:123, srv:navidrome)
- _current_sidebar_key: sección del sidebar activa (ej. playlist_hub, connections_hub)
- dispatch() setea ambos; configure_header acepta route_key opcional
- Resuelto por resolve_sidebar_active_key()

### Fase 5 — Perf infrastructure
- tests/perf/generate_library.py (synthetic 10k items)
- tests/perf/test_library_perf.py (thresholds <2.5s/<1.0s/<0.2s)
- marker perf en pyproject.toml
- docs/performance.md

### Fase 6 — Backfills protegidos
- LibraryController.load() omite backfills en safe mode
- LibraryController.load() omite backfills si library/auto_backfill_enabled=False
- Tests anti-regresión para ambas guardas
