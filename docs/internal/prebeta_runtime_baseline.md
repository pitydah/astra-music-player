# Pre-beta Runtime Baseline

Commit: 596811e
Date: 2026-06-28

## Validación local

| Métrica | Resultado |
|---------|-----------|
| Ruff | 0 errors |
| Compileall | OK |
| Pytest (anti-regression) | 57 passed |
| Pytest (completo) | Pendiente (timeout en suite completa, requiere --timeout o excluir tests lentos) |
| ci_local.sh | Pendiente (needs GI/GStreamer) |
| smoke_startup | All checks passed |
| smoke_ui_routes | All checks passed |
| pytest -m perf | Pendiente (needs GStreamer + synthetic data) |

## CI remoto (GitHub Actions)

GitHub Actions: **pending verification** — no visible workflow run yet.
El workflow anterior fallaba con `NameError("name 'Image' is not defined")`
(posiblemente Pillow no instalado en runner). Aún no se ha verificado si persiste.

## Errores conocidos

- `test_is_enabled_returns_true_from_settings` en `test_ai_assistant_controller.py`: pre-existente,
  no relacionado con este hardening.
- Suite pytest completa puede tomar >2min en entornos sin aceleración.

## Riesgos conocidos

- CI GitHub Actions requiere verificación manual.
- Perf tests no integrados en CI — solo manual con `-m perf`.

## Cambios realizados (commit f78000b + 596811e + hardening final)

### Hardening final (este commit)
- `scripts/ci_local.sh`: Ruff restaurado como paso [8/10] independiente.
  `compileall` movido a paso [9/10]. Sin summary final (10 pasos reales).
- `scripts/smoke_ui_routes.py`: cierre robusto con `finally` conteniendo
  `w.close()`, `w.deleteLater()`, `app.processEvents()`. Route/sidebar ahora
  es obligatorio (asserts directos, sin `hasattr`/skip). Agregados asserts para
  `srv:navidrome` → `connections_hub` y `dev:usb` → `devices_page`.
- `ui/window.py:_rebuild_sidebar()`: usa `_current_sidebar_key` como fuente
  primaria, con fallback a `resolve_sidebar_active_key(_current_route_key)`.
  Ya no usa `_current_section_key` para restaurar sidebar.
- `ui/controllers/navigation_controller.py:dispatch()`: setea explícitamente
  `_current_route_key`, `_current_sidebar_key` y `_current_section_key`
  (legacy alias) después de `configure_header()`.
- `tests/perf/generate_library.py`: eliminados `rebuild_indexes()` periódicos
  cada 1000 items — solo uno al final.
- `docs/performance.md`: actualizado con estado "preliminary synthetic suite",
  tabla real (5k tracks), notas sobre overhead de `add_file()`.
- Tests anti-regresión: 6 tests nuevos (ci_local Ruff, smoke_startup runtime
  base, smoke_ui finally, route/sidebar mandatory, _rebuild_sidebar key, etc.)

### Fase 6 — Backfills protegidos (f78000b)
- LibraryController.load() omite backfills en safe mode
- LibraryController.load() omite backfills si library/auto_backfill_enabled=False
- Tests anti-regresión para ambas guardas

### Fase 5 — Perf infrastructure (f78000b)
- tests/perf/generate_library.py (synthetic items via add_file)
- tests/perf/test_library_perf.py (thresholds <2.5s/<1.0s/<0.2s)
- marker perf en pyproject.toml
- docs/performance.md

### Fase 4 — Route/sidebar separation (f78000b + este commit)
- _current_route_key: ruta exacta (ej. pl:123, srv:navidrome)
- _current_sidebar_key: sección del sidebar activa
- dispatch() setea los 3 estados explícitamente
- _rebuild_sidebar() usa _current_sidebar_key como fuente primaria
