# Diagnóstico de Audio Lab

## ¿Qué hace?

Diagnóstico analiza archivos de audio individuales o carpetas completas y genera un reporte técnico con datos como formato, frecuencia de muestreo, profundidad de bits, canales, duración y calidad estimada (lossless, hires, lossy, DSD).

Incluye un análisis espectral experimental para archivos WAV PCM que evalúa si el contenido espectral es coherente con la resolución declarada.

## Arquitectura

```
core/audio_lab/diagnostics_service.py   → lógica de dominio (cache, análisis, reportes, badges)
library/audio_lab_badges.py             → adaptador para Biblioteca (sin PySide)
ui/audio_lab/diagnostics_page.py        → UI de Diagnóstico
ui/audio_lab/diagnostics_service.py     → wrapper (deprecated, redirige a core)
```

- `core/audio_lab/diagnostics_service.py` contiene: `DiagnosticsCache`, `analyse_file`, `analyse_directory`, `analyse_spectral`, `generate_report`, `get_badge_for_file`, `get_spectral_badge`, `close_global_cache`, `reset_global_cache_for_tests`.
- `library/audio_lab_badges.py` proporciona: `get_audio_lab_badge_for_path`, `get_audio_lab_badges_for_paths`, `get_spectral_badge_from_result`, `get_quality_filter_value`, `is_analysis_pending`, `matches_quality_filter`, `matches_analysis_filter`, `matches_spectral_filter`.
- La UI importa desde `core.audio_lab.diagnostics_service`. El wrapper en `ui/` solo existe para retrocompatibilidad.

## Servicios que reutiliza

| Servicio | Propósito |
|---|---|
| `audio/format_probe.py` | Detecta formato, codec, sample rate, bit depth, canales |
| `audio/quality_classifier.py` | Clasifica calidad (lossless/hires/lossy/dsd) desde metadatos |
| `core/audio_analysis/spectral_authenticator.py` | Análisis espectral vía FFT para WAV PCM |

## Cache

Los resultados de diagnóstico se almacenan en una base de datos SQLite (`diagnostics_cache.db`) para evitar recalibrar archivos que no han cambiado. La cache usa `mtime` + `size` como clave de invalidación.

- Si el archivo no ha cambiado, el segundo análisis devuelve el resultado cacheado.
- Si el archivo cambió (diferente `mtime` o `size`), se recalcula.
- Archivos inexistentes no se cachean.
- La cache tiene funciones de ciclo de vida: `close_global_cache()`, `reset_global_cache_for_tests()`.

## Coherencia espectral Hi-Res

El análisis espectral usa FFT (tamaño 8192, ventana Hann) para examinar el contenido espectral de un archivo WAV PCM y estimar si la resolución declarada es coherente con el contenido real.

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

## Formatos soportados

### Diagnóstico general
Todos los formatos que `format_probe` soporta: FLAC, WAV, MP3, Ogg, Opus, M4A, AIFF, WavPack, APE, DSF, DFF.

### Análisis espectral
Solo WAV PCM (8, 16, 24 y 32 bits, mono y estéreo). No soporta FLAC, MP3 ni otros formatos comprimidos. El soporte espectral para FLAC está planificado para una fase posterior.

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

## Filtros de búsqueda

Los siguientes filtros están disponibles en la barra de búsqueda:

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

- **Análisis de carpeta desde UI**: usa `QThread` local (`_FolderWorker`) para no bloquear la interfaz.
- **Análisis de biblioteca completa**: usa `JobManager` persistente mediante `analyse_directory_job()`. API lista pero no conectada a la UI por defecto.
- Ambos coexisten: el QThread es para análisis puntual rápido, el JobManager para trabajos largos con persistencia.

## Limitaciones actuales

- El análisis espectral no soporta FLAC (solo WAV PCM).
- No hay gráficos espectrales en la UI.
- La integración visual con Biblioteca (badges en la tabla) está en etapa inicial.
- El análisis QThread local no tiene límite de concurrencia.
- `analyse_directory_job()` con JobManager no tiene UI conectada todavía.

## Próximos pasos

- Análisis espectral de FLAC mediante decodificación temporal preservando resolución.
- Cola de análisis persistente con UI.
- Reporte exportable a texto/JSON.
- Integración visual completa de badges en la tabla de canciones.
