"""AlbumImportWorker — background import of albums to Michi Micro Server."""
from __future__ import annotations

import logging
from dataclasses import dataclass

from PySide6.QtCore import QObject, Signal

from integrations.michi_link.client import RemoteServerInfo
from integrations.michi_link.services.import_to_server_service import (
    ImportToServerService,
)

logger = logging.getLogger("michi.album_import_worker")


@dataclass
class AlbumImportProgress:
    current: int = 0
    total: int = 0
    filepath: str = ""
    phase: str = "upload"
    message: str = ""


@dataclass
class AlbumImportResult:
    ok: bool = False
    uploaded: int = 0
    total: int = 0
    message: str = ""
    rolled_back: bool = False
    error: str = ""


class AlbumImportWorker(QObject):
    progress = Signal(object)
    finished = Signal(object)
    failed = Signal(str)

    def __init__(self, server: RemoteServerInfo, filepaths: list[str],
                 import_service: ImportToServerService | None = None):
        super().__init__()
        self._server = server
        self._filepaths = filepaths
        self._import = import_service or ImportToServerService()

    def run(self):
        try:
            # Preflight + session creation
            session_result = self._import.create_session(self._server, self._filepaths)
            if not session_result.ok:
                self.failed.emit(f"Preflight failed: {session_result.message}")
                return
            pd = session_result.data
            sid = pd.get("session_id", "")

            total = len(self._filepaths)
            uploaded = 0

            for i, fp in enumerate(self._filepaths):
                if not fp or not __import__("os").path.isfile(fp):
                    logger.warning("Skipping missing file: %s", fp)
                    continue
                self.progress.emit(AlbumImportProgress(
                    current=i, total=total, filepath=fp, phase="upload",
                    message=f"Subiendo {fp}",
                ))
                upload_result = self._import.upload_track(sid, str(i), local_filepath=fp)
                if upload_result.ok:
                    uploaded += 1
                else:
                    self._import.rollback(sid)
                    result = AlbumImportResult(
                        ok=False, uploaded=uploaded, total=total,
                        message=f"Upload failed: {upload_result.message}",
                        rolled_back=True,
                    )
                    self.finished.emit(result)
                    return

            # Commit
            commit_result = self._import.commit(sid)
            if commit_result.ok:
                result = AlbumImportResult(
                    ok=True, uploaded=uploaded, total=total,
                    message=f"{uploaded}/{total} canciones enviadas a {self._server.alias or 'servidor'}.",
                )
            else:
                self._import.rollback(sid)
                result = AlbumImportResult(
                    ok=False, uploaded=uploaded, total=total,
                    message=f"Commit failed: {commit_result.message}",
                    rolled_back=True,
                )
            self.finished.emit(result)

        except Exception as e:
            logger.exception("Album import worker failed")
            self.failed.emit(str(e))
