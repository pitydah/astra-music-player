# Songs Premium — Biblioteca > Canciones

## Propósito
Convertir la sección `Biblioteca > Canciones` en un centro maestro de gestión musical:
tabla premium basada en `MediaItem`, filtros avanzados, estados visuales, selección múltiple,
acciones masivas y panel lateral.

## Arquitectura

```
SongsPremiumPage (UI pasiva)
  ├── SongsFilterBar → emite SongsFilterState
  ├── MediaItemTableModel (QAbstractTableModel) basado en MediaItem
  ├── SongsBulkActionBar → emite señales sin payload
  └── SongsDetailPanel → emite señales con item

SongsController (coordinador)
  ├── SongsQueryService → consultas + filtros (sin UI)
  └── SongsStatusService → badges + favoritos (sin UI)

LibraryController → crea SongsController + SongsPremiumPage
SearchRouter  → usa SongsController si existe, fallback legacy
ViewModeRouter → list = premium, grid = SongGridWidget
```

## Flujo de datos
1. `LibraryController.show_library_hub()` crea `SongsController` + `SongsPremiumPage`.
2. `SongsController.load()` carga items + calcula status badges.
3. `SongsPremiumPage.load_data()` pobla `MediaItemTableModel`.
4. El usuario filtra → `SongsFilterBar` emite `SongsFilterState`.
5. `SongsPremiumPage._on_filters_changed()` → `SongsController.apply_filter()`.
6. `SongsQueryService.filter()` aplica filtros en memoria.
7. `SongsPremiumPage.load_data()` refresca el modelo.
8. El usuario selecciona filas → bulk bar o detail panel.
9. Acciones → `SongsController.play_items/queue_items/edit_metadata/etc`.

## Filtros soportados
- Formato (extensión normalizada)
- Calidad (Hi-Res, Lossless, Lossy, DSD)
- Género (desde la biblioteca)
- Año mínimo / máximo
- Sample rate mínimo (kHz → Hz)
- Bitrate mínimo (kbps → bps)
- Solo favoritos (por filepath)
- Sin metadata (título/artista/álbum/género incompleto)
- Archivo perdido (os.path.isfile)
- Audio Lab warning (post-filtro via status cache)
- Búsqueda textual global

## Acciones masivas
1. Reproducir selección
2. Añadir a cola
3. Editar metadata
4. Agregar a playlist (diálogo: existente o nueva)
5. Marcar/desmarcar favorito
6. Analizar calidad (vía WorkerManager)
7. Localizar archivo (xdg-open)
8. Placeholder: Micro Server, Mobile Sync, conversión

## Estados visuales
- Hi-Res, Lossless, Lossy, DSD
- Favorito (★)
- Metadata incompleta
- Sin carátula
- Archivo perdido
- Audio Lab warning
- Calidad desconocida

## Columnas configurables
Click derecho en el header de la tabla para activar/desactivar:
Bitrate, Sample Rate, Bit Depth, Canales, BPM, Tonalidad,
Reproducciones, Rating, Tamaño, RG Track, RG Album.

Persiste en QSettings entre sesiones.

## Próximos pasos
- Michi Micro Server (enviar canciones al servidor)
- Michi Mobile (sincronizar a móvil)
- Conversión de formato batch
- Fake Hi-Res avanzado (espectral)
- Análisis batch profundo de Audio Lab
- Columnas configurables con UI completa
