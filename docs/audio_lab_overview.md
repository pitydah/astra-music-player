# Audio Lab — overview

Audio Lab es el centro de análisis, diagnóstico, organización y
configuración de audio de Michi Music Player.

## Estructura: cinco áreas

| Área | Ruta | Estado |
|---|---|---|
| Diagnóstico | `audio_lab_diagnostics` | Experimental |
| Identificador de Audios | `audio_lab_identifier` | Experimental |
| Respaldar | `audio_lab_backup` | Experimental |
| Perfiles de Salida | `audio_lab_output` | Experimental |
| Inteligencia Local | `audio_lab_intelligence` | Experimental |

Ninguna subpágina de Audio Lab está en el sidebar. Todas se navegan
desde el hub central.

## Diagnóstico

- Analiza archivos individuales o carpetas completas.
- Análisis de carpeta usa QThread (no bloquea UI).
- JobManager para análisis persistente de biblioteca completa.
- Sincroniza resultados con `media_items` para filtros `quality:`,
  `analysis:`, `spectral:` en SearchEngine.
- Análisis espectral WAV/FLAC experimental y probabilístico.
- Resultados espectrales se guardan en cache SQLite.
- Reporte exportable a TXT/CSV/JSON.
- Análisis periódico automático programable (desactivado por defecto).

## Identificador de Audios

- **Editor de Metadatos**: edita tags individuales.
- **MusicBrainz**: busca artista/álbum/canción. Confirmación antes de
  escribir metadatos. Experimental.
- **Carátulas**: busca e incrusta artwork. Confirmación antes de
  incrustar en múltiples archivos. Experimental.
- **Letras**: busca letras vía LRCLIB, edita y guarda con confirmación.
  Experimental.
- No implementa Discogs ni servicios privativos.

## Respaldar

- **Ripear CD**: extrae CDs a WAV usando herramientas externas.
  Requiere `abcde` o `cdparanoia`.
- **Digitalizar Vinilo**: captura desde ADC. Exportación requiere
  ffmpeg. Experimental.
- **Convertir Formatos**: convierte entre formatos usando herramientas
  externas (flac, lame, opusenc, ffmpeg). WAV es copia directa sin
  compresión. Los originales no se modifican.
- **Organizar Archivos**: renombra y reorganiza usando plantillas.
  Siempre genera preview y pide confirmación antes de mover. No se
  mueve nada sin confirmación del usuario.

## Perfiles de Salida

- Muestra perfil activo, bit-perfect, resample, EQ, ReplayGain, dispositivo.
- Bit-perfect muestra el estado del perfil (no verificación contra DAC real).
- Upsampling: UI preliminar deshabilitada — no conectada al pipeline.
- Room Correction: UI preliminar deshabilitada — no implementada.

## Inteligencia Local

- BPM, Key, Energy (extraídos por backend de análisis acústico).
- Radio local: genera lista de canciones similares.
- Smart Mix: genera mezcla basada en similitud acústica.
- Si el backend de análisis no está disponible, los botones se
  deshabilitan y se muestra aviso.

## Dependencias externas

| Herramienta | Opcional | Para qué |
|---|---|---|
| ffmpeg | Sí | FLAC spectral, conversión a ALAC, exportación vinilo |
| flac | Sí | Conversión a FLAC |
| lame | Sí | Conversión a MP3 |
| opusenc | Sí | Conversión a Opus |
| abcde | Sí | Ripeo de CD |

## Límites conocidos

- Análisis espectral: probabilístico, no concluyente.
- MusicBrainz: búsqueda HTTP síncrona (puede congelar UI brevemente).
- Letras: búsqueda HTTP síncrona (puede congelar UI brevemente).
- Organizar: rename/movimiento síncrono en UI.
- Perfiles de Salida: cambios solo persisten en settings — no
  reconectan el pipeline de audio en vivo.
- Vinilo: exportación síncrona (split+encode).
- No hay Discogs.
- No hay Room Correction real.
- No hay Upsampling real.
