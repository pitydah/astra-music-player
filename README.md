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
astra-music-player/
├── main.py                     # Entry point
├── LICENSE                      # GPL-3.0-or-later
├── NOTICE                       # Miro Player origin credit
├── pyproject.toml               # Package config
├── requirements.txt             # Pip dependencies
├── install_arch.sh / install_ubuntu.sh
├── data/astra-music-player.desktop
│
├── audio/                       # Audio engine
│   ├── player.py                # GStreamer playback engine
│   ├── audio_chain.py           # DAC config, EQ sink builders
│   ├── eq_biquad.py            # Biquad filter calculations
│   ├── eq_basic.py             # Graphic EQ widget
│   ├── eq_advanced.py          # Parametric EQ widget
│   ├── eq_band_row.py          # EQ band row
│   ├── eq_curve.py             # Frequency response curve
│   ├── eq_presets.py           # EQ preset management
│   ├── eq_autoeq.py            # AutoEQ integration
│   ├── eq_convert.py           # EQ conversion
│   ├── spectrum.py             # Spectrum analyzer
│   └── dff_parser.py           # DFF/DSD parser
│
├── library/                     # Library & database
│   ├── library_db.py           # SQLite schema, scanner, metadata
│   ├── album_art.py            # Cover art extraction
│   └── coverflow.py            # 3D CoverFlow carousel
│
├── ui/                          # User interface
│   ├── window.py               # Main window + menus + sidebar
│   ├── nowplaying_bar.py       # Bottom playback bar
│   ├── sidebar_widget.py       # Collapsible section sidebar
│   ├── expanded_view.py        # Expanded player view
│   ├── eq_panel.py             # EQ dialog panel
│   ├── preferences_window.py   # 14-category settings dialog
│   ├── theme.py                # QPalette + QSS
│   ├── icons.py                # Icon resolution
│   └── blur_manager.py         # KWin blur utilities
│
├── streaming/                   # Streaming & radio
│   ├── subsonic_client.py      # Subsonic API client
│   ├── remote_browser.py       # Remote library browser
│   ├── server_dialog.py        # Server connection dialog
│   ├── radio_manager.py        # Radio station management
│   ├── radio_widget.py         # Radio station list widget
│   ├── radio_dialog.py         # Add/edit radio dialog
│   └── transmit_manager.py     # Audio transmission manager
│
├── sync/                        # Android sync
│   ├── sync_server.py          # HTTP REST API server
│   ├── sync_protocol.py        # Sync data protocol
│   ├── sync_discovery.py       # UDP multicast discovery
│   └── sync_manager.py         # Sync session manager
│
├── core/                        # Core infrastructure
│   └── settings_manager.py     # QSettings wrapper
│
├── adapters/                    # System integrations
│   └── mpris.py                # MPRIS DBus adapter (KDE)
│
├── docs/                        # Documentation
│   ├── architecture.md
│   └── roadmap.md
│
└── icons/                       # Icons (SVG + PNG)
```

## Tecnologías

- **Python 3.11+**
- **PySide6** (Qt 6)
- **GStreamer 1.0** (motor de audio)
- **SQLite** (biblioteca y persistencia)
- **mutagen** (metadatos)
- **dbus-python** (MPRIS / integración KDE)

## Estado de funcionalidades

> **Versión actual: v0.1.0-alpha** — 85 tests automatizados, 18 controladores/servicios modulares, Flatpak packaging listo. Última verificación: 2026-06-20.

### Arquitectura
| Métrica | Valor |
|---------|-------|
| `window.py` líneas | 2040 (era 2713, -25%) |
| Controladores/servicios | 18 extraídos |
| DI via AppContext | 168→1 accesos directos |
| Tests | 85 en 22 archivos |
| Ruff | 7 (sugerencias SIM) |
| Bugs (F-class) | 0 |
| excepciones silenciadas | 0 |

### Funcionalidades
| Funcionalidad | Estado |
|--------------|--------|
| Reproducción local (MP3, FLAC, OGG, WAV) | ✅ Alpha |
| Biblioteca SQLite + metadatos + carátulas | ✅ Alpha |
| Ecualizador gráfico + paramétrico | ✅ Alpha |
| Playlists (crear, editar, eliminar) | ✅ Alpha |
| CoverFlow 3D | ✅ Alpha |
| Persistencia de cola entre sesiones | ✅ Alpha |
| Glassmorphism oscuro | ✅ Alpha |
| Preferencias (16 categorías) | ✅ Alpha |
| Atajos de teclado | ✅ Alpha |
| Artistas (grid + ficha detalle) | ✅ Alpha |
| Playlist Hub | ✅ Alpha |
| Editor de metadatos (Mutagen) | ✅ Alpha |
| Flatpak packaging | ✅ Alpha |
| AppContext DI | ✅ Alpha |
| MPRIS (integración KDE Plasma) | ⚠️ Experimental |
| Subsonic / Navidrome / Jellyfin | ⚠️ Experimental |
| Radio por Internet | ⚠️ Experimental |
| Transmisión HTTP / Snapcast | ⚠️ Experimental |
| Sincronización Android (API REST) | ⚠️ Experimental |
| DSD/DFF nativo | ⚠️ Experimental |
| AutoEQ | ⚠️ Experimental |

### Instalación
```bash
git clone https://github.com/pitydah/astra-music-player
cd astra-music-player
pip install .
astra-music-player
```

### Flatpak
```bash
flatpak-builder --user --install build-dir data/com.astra.MusicPlayer.yml
flatpak run com.astra.MusicPlayer
```

## Licencia

GPL-3.0-or-later

> **Nota sobre la licencia**: Este proyecto se deriva de Miro Player. Si el código original estaba bajo GPL-2.0-only, la relicencia a GPL-3.0-or-later requiere verificación adicional. Ver el archivo NOTICE para más detalles.
