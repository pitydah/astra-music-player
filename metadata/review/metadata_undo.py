"""Metadata undo — reverts applied metadata changes from a review."""

from __future__ import annotations

import logging
from typing import Any

from metadata.review.metadata_review_repository import MetadataReviewRepository

logger = logging.getLogger("michi.metadata.undo")


class MetadataUndo:
    def __init__(self, db: Any, repository: MetadataReviewRepository):
        self._db = db
        self._repo = repository

    def undo(self, review_id: str) -> dict[str, Any]:
        review = self._repo.load_review(review_id)
        if not review:
            return {"status": "error", "error": "Revision no encontrada."}
        if review.status != "applied":
            return {"status": "error", "error": "Esta revision no fue aplicada."}
        if review.apply_target == "file_tags":
            return {"status": "error", "error": "Deshacer cambios en archivos no soportado — restaura desde backup manual."}

        stack = self._repo.get_undo_stack(review_id)
        if not stack:
            return {"status": "error", "error": "No hay datos para deshacer."}

        restored = 0
        failed = 0
        for entry in stack:
            ok = self._db.update_media_item_field(
                entry["track_id"], entry["field"], entry["old_value"],
            )
            if ok:
                restored += 1
            else:
                failed += 1

        self._repo.clear_undo(review_id)
        self._repo.log_action(
            review_id, "undo", "undone",
            f"Deshechos {restored} cambios, fallidos {failed}",
        )

        if restored > 0:
            review.status = "undone"
        return {"status": "undone", "restored": restored, "failed": failed}
