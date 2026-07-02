"""MetadataBridge — read-only metadata inspector for QML.

This bridge provides read-only access to track metadata.
It does NOT write tags, modify files, or call external services.
"""

from PySide6.QtCore import QObject, Signal, Property, Slot
import logging

logger = logging.getLogger("michi.metadata")

_NA = "No disponible"


def _read_metadata_safe(filepath: str) -> dict:
    from pathlib import Path
    p = Path(filepath)
    if not p.is_file():
        return {"error": "Archivo no encontrado"}

    result = {
        "title": p.stem or p.name,
        "artist": _NA,
        "album": _NA,
        "format": p.suffix.lower().lstrip(".").upper() if p.suffix else _NA,
        "size": "",
        "bitrate": _NA,
        "samplerate": _NA,
        "channels": _NA,
        "duration": _NA,
        "extractor": "basic",
    }

    try:
        from mutagen import File
        audio = File(filepath, easy=True)
        if audio is not None:
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

            result["extractor"] = "mutagen"
    except Exception:
        logger.debug("Mutagen read failed for %s", filepath, exc_info=True)

    try:
        size = p.stat().st_size
        if size > 0:
            if size > 1024 * 1024:
                result["size"] = f"{size / (1024 * 1024):.1f} MB"
            else:
                result["size"] = f"{size / 1024:.0f} KB"
    except Exception:
        logger.debug("Size read failed for %s", filepath, exc_info=True)

    return result


class MetadataBridge(QObject):
    dataChanged = Signal()
    selectionChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_filepath = ""
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
        self._current_filepath = filepath
        self._is_loading = True
        self._has_selection = True
        self._error_message = ""

        meta = _read_metadata_safe(filepath)

        if "error" in meta:
            self._error_message = meta["error"]
            self._track_title = _NA
            self._track_artist = _NA
            self._track_album = _NA
            self._fields = [
                {"label": "Archivo", "value": str(filepath)},
                {"label": "Estado", "value": "No encontrado"},
            ]
            self._quality_summary = "Archivo no accesible"
            self._artwork_status = _NA
            self._is_loading = False
            self.dataChanged.emit()
            return

        self._track_title = meta.get("title", _NA)
        self._track_artist = meta.get("artist", _NA)
        self._track_album = meta.get("album", _NA)

        extractor = meta.get("extractor", "basic")
        quality = "Inspección básica"
        if extractor == "mutagen":
            quality = "Lectura completa con mutagen"

        self._fields = [
            {"label": "Archivo", "value": str(filepath)},
            {"label": "Título", "value": meta.get("title", _NA)},
            {"label": "Artista", "value": meta.get("artist", _NA)},
            {"label": "Álbum", "value": meta.get("album", _NA)},
            {"label": "Formato", "value": meta.get("format", _NA)},
            {"label": "Duración", "value": meta.get("duration", _NA)},
            {"label": "Bitrate", "value": meta.get("bitrate", _NA)},
            {"label": "Frecuencia", "value": meta.get("samplerate", _NA)},
            {"label": "Canales", "value": meta.get("channels", _NA)},
            {"label": "Tamaño", "value": meta.get("size", _NA)},
            {"label": "Estado", "value": "Solo lectura"},
        ]
        self._quality_summary = quality
        self._artwork_status = "No verificada"
        self._is_loading = False
        self.dataChanged.emit()

    @Slot()
    def clear(self):
        self._current_filepath = ""
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
        if self._current_filepath:
            self.inspectTrack(self._current_filepath)
        elif self._has_selection:
            self.dataChanged.emit()

    @Slot()
    def previewSuggestedFixes(self):
        self._error_message = "Previsualización disponible en una fase posterior."
        self.dataChanged.emit()
