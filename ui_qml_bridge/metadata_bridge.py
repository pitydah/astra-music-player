"""MetadataBridge — read-only metadata inspector for QML.

This bridge provides read-only access to track metadata.
It does NOT write tags, modify files, or call external services.
"""

from PySide6.QtCore import QObject, Signal, Property, Slot


def _read_metadata_safe(filepath: str) -> dict:
    """Read metadata via mutagen in read-only mode. Returns dict or empty."""
    from pathlib import Path
    p = Path(filepath)
    if not p.is_file():
        return {"error": "Archivo no encontrado"}

    result = {
        "title": p.stem or p.name,
        "artist": "—",
        "album": "—",
        "format": p.suffix.lower().lstrip(".").upper() if p.suffix else "—",
        "size": "",
        "bitrate": "",
        "samplerate": "",
        "channels": "",
        "duration": "",
    }

    try:
        from mutagen import File
        audio = File(filepath, easy=True)
        if audio is None:
            return result

        tags = audio.get("title", [None])
        if tags and tags[0]:
            result["title"] = tags[0]
        artists = audio.get("artist", [None])
        if artists and artists[0]:
            result["artist"] = artists[0]
        albums = audio.get("album", [None])
        if albums and albums[0]:
            result["album"] = albums[0]


        if hasattr(audio, "info"):
            info = audio.info
            if hasattr(info, "bitrate") and info.bitrate:
                result["bitrate"] = f"{info.bitrate // 1000} kbps"
            if hasattr(info, "sample_rate") and info.sample_rate:
                result["samplerate"] = f"{info.sample_rate} Hz"
            if hasattr(info, "channels") and info.channels:
                result["channels"] = f"{info.channels} canales"
            if hasattr(info, "length") and info.length:
                secs = int(info.length)
                result["duration"] = f"{secs // 60}:{secs % 60:02d}"

        size = p.stat().st_size if p.exists() else 0
        if size > 0:
            if size > 1024 * 1024:
                result["size"] = f"{size / (1024 * 1024):.1f} MB"
            else:
                result["size"] = f"{size / 1024:.0f} KB"

    except Exception:
        pass

    return result


class MetadataBridge(QObject):
    dataChanged = Signal()
    selectionChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._has_selection = False
        self._is_loading = False
        self._error_message = ""
        self._track_title = ""
        self._track_artist = ""
        self._track_album = ""
        self._fields = []
        self._quality_summary = ""
        self._artwork_status = ""

    @Property(bool, notify=selectionChanged)
    def hasSelection(self):
        return self._has_selection

    @Property(bool, notify=dataChanged)
    def isLoading(self):
        return self._is_loading

    @Property(str, notify=dataChanged)
    def errorMessage(self):
        return self._error_message

    @Property(str, notify=dataChanged)
    def trackTitle(self):
        return self._track_title

    @Property(str, notify=dataChanged)
    def trackArtist(self):
        return self._track_artist

    @Property(str, notify=dataChanged)
    def trackAlbum(self):
        return self._track_album

    @Property("QVariantList", notify=dataChanged)
    def fields(self):
        return self._fields

    @Property(str, notify=dataChanged)
    def qualitySummary(self):
        return self._quality_summary

    @Property(str, notify=dataChanged)
    def artworkStatus(self):
        return self._artwork_status

    @Property(bool, constant=True)
    def canApply(self):
        return False

    @Slot(str)
    def inspectTrack(self, filepath: str):
        if not filepath:
            self.clear()
            return
        self._is_loading = True
        self._has_selection = True
        self._error_message = ""

        meta = _read_metadata_safe(filepath)

        if "error" in meta:
            self._error_message = meta["error"]
            self._track_title = "—"
            self._track_artist = "—"
            self._track_album = "—"
            self._fields = [
                {"label": "Archivo", "value": str(filepath)},
                {"label": "Estado", "value": "No encontrado"},
            ]
            self._quality_summary = "Archivo no accesible"
            self._artwork_status = "—"
            self._is_loading = False
            self.dataChanged.emit()
            return

        self._track_title = meta.get("title", "—")
        self._track_artist = meta.get("artist", "—")
        self._track_album = meta.get("album", "—")

        self._fields = [
            {"label": "Archivo", "value": str(filepath)},
            {"label": "Título", "value": meta.get("title", "—")},
            {"label": "Artista", "value": meta.get("artist", "—")},
            {"label": "Álbum", "value": meta.get("album", "—")},
            {"label": "Formato", "value": meta.get("format", "—")},
            {"label": "Duración", "value": meta.get("duration", "—")},
            {"label": "Bitrate", "value": meta.get("bitrate", "—")},
            {"label": "Frecuencia", "value": meta.get("samplerate", "—")},
            {"label": "Canales", "value": meta.get("channels", "—")},
            {"label": "Tamaño", "value": meta.get("size", "—")},
            {"label": "Estado", "value": "Solo lectura"},
        ]
        self._quality_summary = "Inspección básica completada"
        self._artwork_status = "No verificada"
        self._is_loading = False
        self.dataChanged.emit()

    @Slot()
    def clear(self):
        self._has_selection = False
        self._is_loading = False
        self._error_message = ""
        self._track_title = ""
        self._track_artist = ""
        self._track_album = ""
        self._fields = []
        self._quality_summary = ""
        self._artwork_status = ""
        self.dataChanged.emit()

    @Slot()
    def refresh(self):
        if self._has_selection:
            self.dataChanged.emit()

    @Slot()
    def previewSuggestedFixes(self):
        self._error_message = "Previsualización disponible en una fase posterior."
        self.dataChanged.emit()
