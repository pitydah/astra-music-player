"""MetadataBridge — read-only metadata inspector for QML.

This bridge provides read-only access to track metadata.
It does NOT write tags, modify files, or call external services.
"""

from PySide6.QtCore import QObject, Signal, Property, Slot


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
        self._track_title = "—"
        self._track_artist = "—"
        self._track_album = "—"
        self._fields = [
            {"label": "Archivo", "value": filepath},
        ]
        self._quality_summary = "Sin análisis"
        self._artwork_status = "Sin carátula"
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
        self._error_message = "Previsualización de sugerencias no disponible en modo solo lectura."
        self.dataChanged.emit()
