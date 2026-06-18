# Astra Music Player

Reproductor de música moderno para Linux con soporte para streaming, ecualizador paramétrico, sincronización Android y más.

![Astra](icons/app_icon.png)

## Características

- 🎵 **Reproducción local** — MP3, FLAC, OGG, Opus, WAV, DSD, AIFF
- 🌐 **Streaming** — Navidrome, Jellyfin (API Subsonic)
- 📻 **Radio** — Añade y reproduce emisoras por URL
- 🎛️ **Ecualizador** — Gráfico 31-bandas + paramétrico con biquads
- 📡 **Transmitir** — Envía audio a dispositivos remotos (HTTP, Snapcast)
- 📱 **Sincronización Android** — API REST para sincronizar biblioteca
- 🌀 **CoverFlow 3D** — Carrusel de carátulas con física de desplazamiento
- 🎨 **Fondo adaptativo** — Gradiente basado en colores de la carátula
- 📋 **Playlists** — Crea, edita y gestiona listas de reproducción
- 💾 **Persistencia** — Cola de reproducción, favoritos e historial en SQLite
- 🖥️ **KDE Plasma** — Integración con temas claro/oscuro del sistema

## Instalación

```bash
# Dependencias
pip install PySide6 mutagen numpy

# Requisitos del sistema
sudo apt install python3-gi gir1.2-gstreamer-1.0 gstreamer1.0-plugins-*

# Ejecutar
python3 main.py
```

## Atajos de teclado

| Atajo | Acción |
|-------|--------|
| `Ctrl+O` | Abrir archivo |
| `Ctrl+D` | Añadir carpeta |
| `Ctrl+P` | Preferencias |
| `Ctrl+Q` | Salir |

## Estructura del proyecto

```
music_player/
├── main.py               # Punto de entrada
├── window.py             # Ventana principal
├── player.py             # Motor GStreamer
├── nowplaying_bar.py     # Barra de reproducción
├── sidebar_widget.py     # Sidebar con secciones colapsables
├── library_db.py         # Base de datos SQLite
├── album_art.py          # Gestión de carátulas
├── coverflow.py          # Carrusel 3D de álbumes
├── expanded_view.py      # Vista expandida
├── eq_panel.py           # Panel del ecualizador
├── eq_basic.py           # EQ gráfico
├── eq_advanced.py        # EQ paramétrico
├── eq_biquad.py          # Cálculo de biquads
├── eq_band_row.py        # Fila de banda EQ
├── eq_curve.py           # Curva de respuesta
├── eq_presets.py         # Presets de EQ
├── eq_autoeq.py          # AutoEQ
├── spectrum.py           # Analizador de espectro
├── audio_chain.py        # Cadena de audio GStreamer
├── dff_parser.py         # Parser DFF (DSD)
├── theme.py              # Paleta y QSS
├── icons.py              # Resolución de iconos
├── blur_manager.py       # Efecto blur KWin
├── subsonic_client.py    # Cliente API Subsonic
├── remote_browser.py     # Navegador remoto
├── server_dialog.py      # Diálogo de servidor
├── sync_manager.py       # Sincronización Android
├── sync_server.py        # Servidor HTTP sync
├── sync_protocol.py      # Protocolo sync
├── sync_discovery.py     # Descubrimiento UDP
├── transmit_manager.py   # Transmisión a dispositivos
├── radio_manager.py      # Gestión de emisoras
├── radio_widget.py       # Widget de radio
├── radio_dialog.py       # Diálogo de radio
└── icons/                # Iconos SVG y PNG
```

## Tecnologías

- **Python 3.11+**
- **PySide6** (Qt 6)
- **GStreamer 1.0** (motor de audio)
- **SQLite** (biblioteca y persistencia)
- **mutagen** (metadatos)
- **dbus-python** (MPRIS / integración KDE)

## Estado de funcionalidades

| Funcionalidad | Estado |
|--------------|--------|
| Reproducción local (MP3, FLAC, OGG, WAV, DSD) | ✅ Estable |
| Biblioteca SQLite + metadatos + carátulas | ✅ Estable |
| Ecualizador gráfico 31-bandas + paramétrico | ✅ Estable |
| Playlists (crear, editar, eliminar) | ✅ Estable |
| CoverFlow 3D | ✅ Estable |
| Persistencia de cola entre sesiones | ✅ Estable |
| Fondo adaptativo (colores de carátula) | ✅ Estable |
| Glassmorphism oscuro con textura interna | ✅ Estable |
| Preferencias (14 categorías) | ✅ Estable |
| Atajos de teclado | ✅ Estable |
| MPRIS (integración KDE Plasma) | ✅ Estable |
| Sidebar con secciones colapsables | ✅ Estable |
| Subsonic / Navidrome / Jellyfin | ⚠️ Experimental |
| Radio por Internet | ⚠️ Experimental |
| Transmisión HTTP / Snapcast | ⚠️ Experimental |
| Sincronización Android (API REST) | ⚠️ Experimental |
| DSD/DFF nativo | ⚠️ Experimental |
| AutoEQ | ⚠️ Experimental |

## Licencia

GPL-3.0-or-later
