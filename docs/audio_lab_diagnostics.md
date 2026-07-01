# Diagnóstico de Audio Lab

## ¿Qué hace?

Diagnóstico analiza archivos de audio individuales o carpetas completas y genera un reporte técnico con datos como formato, frecuencia de muestreo, profundidad de bits, canales, duración y calidad estimada (lossless, hires, lossy, DSD).

Incluye un análisis espectral experimental para archivos WAV PCM y FLAC que evalúa si el contenido espectral es coherente con la resolución declarada.

## Arquitectura

```
core/audio_lab/diagnostics_service.py   → lógica de dominio (cache, análisis, reportes, badges, sync)
core/audio_lab/audio_lab_sync.py         → sincronización cache → media_items
library/audio_lab_badges.py             → adaptador para Biblioteca (sin PySide)
ui/audio_lab/diagnostics_page.py        → UI de Diagnóstico
ui/audio_lab/diagnostics_service.py     → wrapper (deprecated, redirige a core)
```

- `core/audio_lab/diagnostics_service.py` contiene: `DiagnosticsCache`, `analyse_file`, `analyse_directory`, `analyse_spectral`, `attach_spectral_analysis`, `generate_report`, `get_badge_for_file`, `get_badges_for_files`, `get_spectral_badge`, `close_global_cache`, `reset_global_cache_for_tests`.
- `core/audio_lab/audio_lab_sync.py` contiene: `sync_audio_lab_result_to_media_item`, `sync_audio_lab_cache_to_media_items`, `mark_audio_lab_pending`, `mark_audio_lab_error`.
- `library/audio_lab_badges.py` proporciona: `get_audio_lab_badge_for_path`, `get_audio_lab_badges_for_paths`, `get_spectral_badge_from_result`, `get_quality_filter_value`, `is_analysis_pending`, `matches_quality_filter`, `matches_analysis_filter`, `matches_spectral_filter`, `get_analysis_pending_map`, `get_spectral_filter_values`.
- La UI importa desde `core.audio_lab.diagnostics_service`. El wrapper en `ui/` solo existe para retrocompatibilidad.

## Servicios que reutiliza

| Servicio | Propósito |
|---|---|
| `audio/format_probe.py` | Detecta formato, codec, sample rate, bit depth, canales |
| `audio/quality_classifier.py` | Clasifica calidad (lossless/hires/lossy/dsd) desde metadatos |
| `core/audio_analysis/spectral_authenticator.py` | Análisis espectral vía FFT para WAV PCM y FLAC |

## Cache

Los resultados de diagnóstico se almacenan en una base de datos SQLite (`diagnostics_cache.db`) para evitar recalibrar archivos que no han cambiado. La cache usa `mtime` + `size` como clave de invalidación.

- Si el archivo no ha cambiado, el segundo análisis devuelve el resultado cacheado.
- Si el archivo cambió (diferente `mtime` o `size`), se recalcula.
- Archivos inexistentes no se cachean.
- La cache incluye campos espectrales: `spectral_verdict`, `spectral_label`, `spectral_confidence`, `spectral_metrics_json`.
- Migración idempotente de columnas vía `_migrate_columns()`.
- La cache tiene funciones de ciclo de vida: `close_global_cache()`, `reset_global_cache_for_tests()`.

## Coherencia espectral Hi-Res

El análisis espectral usa FFT (tamaño 8192, ventana Hann) para examinar el contenido espectral de un archivo WAV PCM o FLAC y estimar si la resolución declarada es coherente con el contenido real.

**Formatos soportados:**
- WAV PCM: directo (8, 16, 24 y 32 bits, mono y estéreo).
- FLAC: experimental vía ffmpeg, preservando sample rate y bit depth originales.
- Si ffmpeg no está instalado, devuelve error controlado para FLAC.

**Etiquetas de resultado:**

| Veredicto | Significado |
|---|---|
| `HI_RES_COHERENT` | El contenido espectral alcanza frecuencias propias de la resolución declarada |
| `LOSSLESS_COHERENT` | El contenido espectral es compatible con una fuente sin pérdidas |
| `SUSPICIOUS_UPSAMPLING` | El techo espectral está muy por debajo de lo esperado |
| `POSSIBLE_LOSSY_SOURCE` | Baja energía en frecuencias altas, sugiere origen lossy |
| `INCONCLUSIVE` | No hay suficiente información para concluir |
| `ANALYSIS_ERROR` | No se pudo completar el análisis |

**Importante:** Los resultados son **probabilísticos**. No deben interpretarse como:
- Prueba definitiva de autenticidad
- Confirmación de fraude
- Reemplazo de análisis profesional

## Badges técnicos

Los badges se pueden consultar desde `library/audio_lab_badges.py` sin depender de PySide.

### Significado de badges

| kind | Significado |
|---|---|
| `hires` | Archivo Hi-Res (>= 96kHz, >= 24-bit) analizado por Audio Lab |
| `lossless` | Archivo sin pérdida |
| `lossy` | Archivo con pérdida (MP3, AAC, etc.) |
| `dsd` | Archivo DSD |
| `unknown` | Formato no clasificado |
| `warning` | Resultado espectral sospechoso |
| `error` | Error de análisis |

### Visualización en Biblioteca

- **Columna "Calidad"** en la tabla de canciones, con colores: hires=verde, lossless=azul, lossy=ámbar, dsd=púrpura, warning=naranja.
- **Panel de detalles**: al seleccionar una pista, se muestra badge técnico con tooltip.
- **Refresh automático**: al analizar desde Audio Lab, los badges se actualizan sin reiniciar la app.

## Filtros de búsqueda

Los siguientes filtros están disponibles en la barra de búsqueda y funcionan de extremo a extremo contra `media_items`:

| Filtro | Valores | Ejemplo |
|---|---|---|
| `quality:` | `hires`, `lossless`, `lossy`, `dsd`, `unknown` | `quality:hires` |
| `analysis:` | `pending`, `error` | `analysis:pending` |
| `spectral:` | `suspicious`, `inconclusive` | `spectral:suspicious` |

Las funciones de filtro puro también están disponibles en `library/audio_lab_badges.py`:
- `matches_quality_filter(path, value)`
- `matches_analysis_filter(path, value)`
- `matches_spectral_filter(path, value)`

## Estrategia de ejecución

- **Análisis de archivo individual**: síncrono desde UI.
- **Análisis de carpeta desde UI**: usa `QThread` local (`_FolderWorker`) para no bloquear la interfaz. Incluye cancelación, progreso y errores por archivo.
- **Análisis de biblioteca completa**: usa `JobManager` persistente mediante `analyse_directory_job()`. Botón "Analizar biblioteca completa" en la UI. Incluye cancelación, progreso y sincronización automática al finalizar.
- **Auto-análisis en indexación**: el `Indexer` ejecuta `analyse_file()` en su Phase 9 para archivos nuevos/actualizados.
- Ambos coexisten: el QThread es para análisis puntual rápido, el JobManager para trabajos largos con persistencia.

## Sincronización con Biblioteca

Los resultados del diagnóstico se sincronizan automáticamente con `media_items`:

1. `sync_audio_lab_result_to_media_item()` escribe `quality`, `analysis_status`, `spectral_verdict` para un archivo.
2. `sync_audio_lab_cache_to_media_items()` batch para múltiples paths.
3. Usa `cursor.rowcount` para conteo exacto de filas actualizadas.
4. La señal `diagnostics_updated` dispara refresco de badges en Biblioteca.

## Gráfico espectral

`DiagnosticsPage` incluye un `SpectralGraphWidget` que muestra un gráfico de barras FFT logarítmico (60 bandas de 20 Hz a 20 kHz) para archivos WAV y FLAC analizados.

- Los datos del gráfico preservan la resolución original del archivo.
- El gráfico es estático (sin zoom/pan).

## Reporte exportable

El reporte técnico se puede exportar a:
- **TXT**: texto plano formateado.
- **CSV**: tabla con métricas por fila.
- **JSON**: estructura de datos completa.

## Limitaciones actuales

- El gráfico espectral es estático (sin zoom/pan interactivo).
- El análisis espectral FLAC requiere ffmpeg.
- Los resultados espectrales son probabilísticos, no concluyentes.
- El análisis masivo de bibliotecas muy grandes puede tardar.
- No hay análisis periódico automático (solo bajo demanda o al indexar).

## Próximos pasos

- Gráfico espectral interactivo con zoom y pan.
- Análisis periódico automático programable.
- Integración visual de advertencias espectrales en la tabla de canciones.
