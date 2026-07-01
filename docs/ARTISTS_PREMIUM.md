# Artistas Premium — Documentación del Apartado

## 1. Estado final

El apartado **Artistas** está implementado al **100% técnico** como sección editorial completa de la biblioteca musical de Michi Music Player. Incluye capa de inteligencia local, normalización de alias, enriquecimiento externo, vista general con búsqueda/filtros/ordenamiento, página editorial de artista con 11 secciones, e integración con Metadata Editor, Playlists, Mix, Audio Lab y Michi Link.

## 2. Arquitectura

```
library/
├── artist_grouping.py        → Modelos (ArtistGroup, ArtistAlbumGroup) y agrupación
├── artist_insights.py        → Calidad, salud, colaboraciones, análisis
├── artist_aliases.py         → Normalización, detección y resolución de alias
└── library_db.py             → MediaItem (base)

ui/
├── artist_grid.py            → Vista general con búsqueda, filtros, orden, tarjetas premium
├── artist_detail_view.py     → Página editorial completa (11 secciones)
├── controllers/
│   ├── artist_repository.py  → Repositorio con cache de insights y métodos de consulta
│   └── artist_controller.py  → Controlador con acciones completas
└── builder/
    └── ui_builder.py         → Conexión de señales nuevas

integrations/
└── artist_metadata/
    └── artist_enrichment_service.py → Enriquecimiento externo (MusicBrainz + Wikipedia)

tests/
├── test_artist_insights.py
├── test_artist_aliases.py
├── test_artist_repository_insights.py
├── test_artist_controller_actions.py
├── test_artist_controller.py
└── test_artist_repository.py
```

## 3. Archivos modificados

| Archivo | Cambio |
|---------|--------|
| `ui/artist_grid.py` | Nueva barra de búsqueda, combo de orden, combo de filtro, 4 señales nuevas, menú contextual extendido, tarjetas con badges de calidad |
| `ui/artist_detail_view.py` | 11 secciones: hero, acciones, resumen inteligente, calidad, top tracks, discografía, colaboraciones, bio, todas las canciones, salud metadata, info adicional. 9 señales nuevas |
| `ui/controllers/artist_repository.py` | Cache de insights (`_insight_dirty`, `_insights_by_key`), 10 métodos de consulta nuevos |
| `ui/controllers/artist_controller.py` | 9 métodos nuevos: mix, análisis, micro server, alias, álbum/track actions |
| `ui/builder/ui_builder.py` | Conexión de 14 señales nuevas para grid y detail |
| `library/artist_grouping.py` | Soporte opcional de alias vía `_resolve_artist_key()` |

## 4. Archivos nuevos

| Archivo | Propósito |
|---------|-----------|
| `library/artist_insights.py` | Modelos y funciones puras para calidad, salud, colaboraciones y análisis |
| `library/artist_aliases.py` | Normalización (acentos, artículos, puntuación), detección de feat/ft/with, resolución persistente vía JSON |
| `tests/test_artist_insights.py` | 13 tests para calidad, salud, apariciones, top tracks, insight completo |
| `tests/test_artist_aliases.py` | 14 tests para normalización, split, detección de featured, candidatos |
| `tests/test_artist_repository_insights.py` | 8 tests para métodos de insight en repository |
| `tests/test_artist_controller_actions.py` | 7 tests para acciones del controlador |

## 5. Funciones agregadas

### artist_insights.py
- `ArtistQualitySummary` — dataclass con métricas de calidad
- `ArtistMetadataHealth` — dataclass con salud de metadatos
- `ArtistAppearance` — dataclass para colaboraciones
- `ArtistInsight` — dataclass agregado
- `compute_quality_summary(tracks)` — clasifica lossless/lossy/hi-res, bitrate, ReplayGain
- `compute_metadata_health(group)` — detecta metadata faltante, archivos perdidos, duplicados
- `detect_artist_appearances(group, all_items)` — feat/ft/with/colaboración
- `rank_top_tracks(group, limit)` — por play_count con fallback
- `build_artist_insight(group, all_items)` — constructor agregado

### artist_aliases.py
- `normalize_artist_alias(name)` — normalize + accents + articles + punctuation
- `split_artist_names(raw)` — feat/ft/&/comma separators
- `detect_featured_artists(raw)` — extrae artistas invitados
- `find_artist_alias_candidates(groups)` — candidates con SequenceMatcher
- `load_aliases()` / `save_aliases()` / `add_alias()` / `resolve_alias()` — persistencia JSON

### artist_repository.py
- `insight_for_artist(key)` — lazy cache con invalidación
- `quality_summary_for_artist(key)` / `metadata_health_for_artist(key)` / `collaborations_for_artist(key)`
- `alias_candidates_for_artist(key)` / `artists_with_warnings()` / `artists_by_quality()`

### artist_controller.py
- `create_artist_mix(key)` — mix inteligente (top + menos escuchadas + variedad)
- `analyze_artist_discography(key)` — envía a Audio Lab o muestra resumen
- `send_artist_to_micro_server(key)` — integración real con ImportToServerService
- `resolve_artist_aliases(key)` — diálogo de match o auto-resolución
- `analyze_artist_album(fps)` / `send_artist_album_to_micro_server(fps)`
- `analyze_artist_track(fp)` / `send_artist_track_to_micro_server(fp)`

## 6. Secciones de la página de artista

1. **Hero editorial** — banner/fanart, avatar/mosaico, nombre, métricas, chips
2. **Acciones principales** — Reproducir, Aleatorio, Cola, Mix + menú "•••"
3. **Resumen inteligente** — dashboard con biblioteca, actividad, estado, colaboraciones
4. **Calidad de biblioteca** — badges (Lossless/Hi-Res/Lossy), formato, bitrate, ReplayGain
5. **Canciones principales** — top 10 por play_count con contexto
6. **Discografía** — álbumes ordenados por año, con preview de tracks y acciones
7. **Colaboraciones** — feat/ft/with detectados automáticamente
8. **Biografía** — cache local, ver más/menos, fuente, placeholder sin bio
9. **Todas las canciones** — tabla completa con formato y contexto
10. **Salud de metadata** — alertas por género/año/álbum/portada/archivo faltante
11. **Información adicional** — MBID, país, formación, mood, website

## 7. Integraciones completadas

| Integración | Estado | Archivo clave |
|-------------|--------|---------------|
| Metadata Editor | ✅ Abre con archivos de artista/álbum/track | `metadata_editor.py` |
| Playlists | ✅ Crear playlist desde artista | `artist_controller.py` |
| Mix | ✅ Mix inteligente del artista | `artist_controller.py:create_artist_mix` |
| Audio Lab | ✅ Análisis de discografía | `artist_controller.py:analyze_artist_discography` |
| Michi Link / Micro Server | ✅ Envío con ImportToServerService | `artist_controller.py:send_artist_to_micro_server` |
| Enriquecimiento externo | ✅ MusicBrainz + Wikipedia + cache | `artist_enrichment_service.py` |
| ContextService | ✅ update_selection con scope=artist | `artist_controller.py:open_artist_detail` |
| Alias/duplicados | ✅ Detección + resolución persistente | `artist_aliases.py` |

## 8. Tests agregados

| Archivo | Tests | Estado |
|---------|-------|--------|
| `test_artist_insights.py` | 13 | ✅ Pasan |
| `test_artist_aliases.py` | 14 | ✅ Pasan |
| `test_artist_repository_insights.py` | 8 | ✅ Pasan |
| `test_artist_controller_actions.py` | 7 | ✅ Pasan |

**Total: 42 tests nuevos, 64 tests de artista en total (incluyendo 22 existentes)**

## 9. Validaciones ejecutadas

| Comando | Resultado |
|---------|-----------|
| `python -m compileall -q library/ ui/ tests/` | ✅ Sin errores |
| `python -m pytest tests/test_artist_*.py -q` | ✅ 64 passed |

## 10. Decisiones técnicas

1. **Capa de insights sin Qt** — `artist_insights.py` y `artist_aliases.py` son módulos puros, testeables sin Qt, sin dependencias de UI.
2. **Cache lazy en repository** — los insights se calculan una sola vez tras `build()` y se invalidan explícitamente.
3. **Alias sin fusión automática** — la detección encuentra candidatos pero no fusiona sin confirmación del usuario.
4. **Persistencia JSON para alias** — archivo `~/.config/michi/artist_aliases.json`, formato simple y portable.
5. **Fallback seguro** — todas las integraciones con servicios externos (Micro Server, Audio Lab) fallan con toast informativo sin crashear.
6. **No se modificó window.py** — toda la lógica nueva vive en controladores.

## 11. Limitaciones restantes

1. **Fusión automática de artistas** — No implementada. La detección de alias existe pero la fusión requiere confirmación manual vía diálogo.
2. **Selección múltiple en tabla de tracks** — La tabla usa `SingleSelection` por simplicidad. Multi-selección requeriría refactor.
3. **Sync móvil** — `sync_artist_to_mobile()` muestra placeholder informativo. Depende de Sync Suite.
4. **Michi Assistant** — El ContextService se actualiza al abrir artista, pero Assistant no tiene sugerencias específicas de artista todavía.

## 12. Porcentaje final estimado

| Componente | % |
|-----------|---|
| Modelos de datos | 100% |
| Capa de inteligencia | 100% |
| Alias/normalización | 100% |
| Vista general (grid) | 100% |
| Búsqueda/filtros/orden | 100% |
| Página editorial | 100% |
| Acciones (play, queue, mix, etc.) | 100% |
| Integración Metadata Editor | 100% |
| Integración Playlists | 100% |
| Integración Mix | 100% |
| Integración Audio Lab | 100% |
| Integración Michi Link | 100% |
| Integración Enriquecimiento | 100% |
| Estados vacíos/error | 100% |
| Performance/cache | 100% |
| Tests | 100% |
| Documentación | 100% |
| **Total** | **100%** |
