"""AudioLabBridge — connects Audio Lab QML to real diagnostics and health services."""

from PySide6.QtCore import QObject, Signal, Property, Slot
import logging

logger = logging.getLogger("michi.audio_lab.bridge")


class AudioLabBridge(QObject):
    dataChanged = Signal()

    def __init__(self, db_conn=None, parent=None):
        super().__init__(parent)
        self._conn = db_conn
        self._health = {}
        self._stats = {}

    @Property("QVariantList", notify=dataChanged)
    def modules(self):
        return [
            {"id": "diagnostics", "title": "Diagnóstico",
             "desc": "Analiza la calidad técnica de tus archivos de audio",
             "status": "available"},
            {"id": "health", "title": "Salud de biblioteca",
             "desc": "Archivos faltantes, metadata incompleta, carátulas",
             "status": "available"},
            {"id": "metadata_doctor", "title": "Metadata Doctor",
             "desc": "Revisa y repara metadatos inconsistentes",
             "status": "available"},
            {"id": "conversion", "title": "Conversión",
             "desc": "Convierte entre formatos de audio",
             "status": "experimental"},
            {"id": "vinyl", "title": "Vinilo",
             "desc": "Captura y digitaliza desde vinilo",
             "status": "experimental"},
            {"id": "analyzer", "title": "Análisis periódico",
             "desc": "Escaneo automático de calidad y metadata",
             "status": "experimental"},
        ]

    @Slot()
    def refresh(self):
        if not self._conn:
            self.dataChanged.emit()
            return
        try:
            from core.audio_lab.library_health import compute_health
            health = compute_health(self._conn)
            self._health = health
            self._stats = {
                "total_tracks": health.get("total_tracks", 0),
                "analysed": health.get("analysed_tracks", 0),
                "pending": health.get("pending_analysis", 0),
                "errors": health.get("error_analysis", 0),
                "hires": health.get("hires_count", 0),
                "lossless": health.get("lossless_count", 0),
                "lossy": health.get("lossy_count", 0),
                "dsd": health.get("dsd_count", 0),
                "missing_metadata": health.get("missing_metadata", 0),
                "missing_covers": health.get("missing_covers", 0),
                "total_size_mb": health.get("total_size_mb", 0),
            }
        except Exception:
            logger.debug("AudioLab health refresh failed", exc_info=True)
        self.dataChanged.emit()

    @Property(int, notify=dataChanged)
    def totalTracks(self):
        return self._stats.get("total_tracks", 0)

    @Property(int, notify=dataChanged)
    def missingMetadata(self):
        return self._stats.get("missing_metadata", 0)

    @Property(int, notify=dataChanged)
    def missingCovers(self):
        return self._stats.get("missing_covers", 0)

    @Slot(str)
    def navigateTo(self, module_id: str):
        pass
