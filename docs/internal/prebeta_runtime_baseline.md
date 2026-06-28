# Pre-beta Runtime Baseline

Commit: 2a48c43
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
- Smoke labels corregidos de [1/7] a [1/8]

### Fase 2 — NoiseOverlay optimizado
- _generate_noise() reemplazado por _noise_tile() cacheado (96×96)
- paintEvent() usa drawTiledPixmap() en vez de generar todo el tamaño

### Fase 4 — Smoke separado
- scripts/smoke_ui_routes.py creado
- CI (ci.yml) ejecuta ambos smoke scripts
- ci_local.sh ejecuta ambos smoke scripts

### Fase 6 — Backfills protegidos
- LibraryController.load() omite backfills en safe mode
