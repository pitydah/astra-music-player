"""Alias resolution dialog — pick which artist name to keep as canonical."""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QWidget,
)
from PySide6.QtCore import Qt, Signal


class AliasResolutionDialog(QDialog):
    """Dialog for resolving artist duplicates/aliases.

    Shows potential alias pairs and lets the user pick the canonical name.
    """

    def __init__(self, artist_name: str, candidates: list[tuple[str, str, float]],
                 group_lookup, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Resolver alias: {artist_name}")
        self.setMinimumSize(500, 350)
        self.setModal(True)
        self.setStyleSheet(
            "QDialog { background: #0d1116; }"
            "QLabel { background: transparent; }")

        self._selected_target: str | None = None
        self._group_lookup = group_lookup

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        title = QLabel(f"Posibles duplicados para \"{artist_name}\"")
        title.setStyleSheet(
            "font-size: 16px; font-weight: 700; color: rgba(255,255,255,0.88);")
        layout.addWidget(title)

        sub = QLabel(
            "Selecciona el nombre canónico o ignora si no son duplicados.")
        sub.setStyleSheet("font-size: 11px; color: rgba(255,255,255,0.48);")
        sub.setWordWrap(True)
        layout.addWidget(sub)
        layout.addSpacing(6)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setStyleSheet(
            "QScrollArea { background: transparent; border: none; }")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        cl = QVBoxLayout(container)
        cl.setSpacing(8)

        for k1, k2, score in candidates:
            card = _AliasCandidateCard(k1, k2, score, group_lookup)
            card.chosen.connect(lambda target=k1 if k1 else k2: self._on_choose(target))
            cl.addWidget(card)

        cl.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll)

        btns = QHBoxLayout()
        btns.addStretch()
        skip_btn = QPushButton("No son duplicados")
        skip_btn.setStyleSheet(
            "QPushButton { color: rgba(255,255,255,0.52); font-size: 12px;"
            "  background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.07);"
            "  border-radius: 10px; padding: 8px 18px; }"
            "QPushButton:hover { background: rgba(255,255,255,0.08); }")
        skip_btn.setCursor(Qt.PointingHandCursor)
        skip_btn.clicked.connect(self._on_skip)
        btns.addWidget(skip_btn)
        layout.addLayout(btns)

    def _on_choose(self, target_key: str):
        self._selected_target = target_key
        self.accept()

    def _on_skip(self):
        self._selected_target = None
        self.reject()

    def selected_key(self) -> str | None:
        return self._selected_target


class _AliasCandidateCard(QFrame):
    chosen = Signal()

    def __init__(self, key1: str, key2: str, score: float, group_lookup):
        super().__init__()
        self._key1 = key1
        self._key2 = key2
        self._score = score
        self.setStyleSheet(
            "QFrame { background: rgba(255,255,255,0.035);"
            "  border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; }"
            "QFrame:hover { background: rgba(255,255,255,0.06);"
            "  border: 1px solid rgba(255,255,255,0.11); }")
        self.setCursor(Qt.PointingHandCursor)

        g1 = group_lookup(key1)
        g2 = group_lookup(key2)
        name1 = g1.display_name if g1 else key1
        name2 = g2.display_name if g2 else key2

        v = QVBoxLayout(self)
        v.setContentsMargins(14, 12, 14, 12)
        v.setSpacing(8)

        pair_row = QHBoxLayout()
        pair_row.setSpacing(12)

        left = QLabel(name1)
        left.setStyleSheet(
            "font-size: 13px; font-weight: 700; color: rgba(255,255,255,0.88);")
        pair_row.addWidget(left)

        arrow = QLabel("↔")
        arrow.setStyleSheet(
            "font-size: 13px; color: rgba(255,255,255,0.30);")
        arrow.setAlignment(Qt.AlignCenter)
        pair_row.addWidget(arrow)

        right = QLabel(name2)
        right.setStyleSheet(
            "font-size: 13px; font-weight: 700; color: rgba(255,255,255,0.88);")
        pair_row.addWidget(right)

        pair_row.addStretch()

        score_lbl = QLabel(f"similitud: {score:.0%}")
        score_lbl.setStyleSheet(
            "font-size: 10px; color: rgba(255,255,255,0.35);"
            "background: rgba(255,255,255,0.03); border-radius: 6px; padding: 2px 8px;")
        pair_row.addWidget(score_lbl)

        btn = QPushButton("Usar")
        btn.setFixedSize(80, 30)
        btn.setStyleSheet(
            "QPushButton { color: #FFFFFF; font-size: 11px; font-weight: 600;"
            "  background: rgba(70,145,255,0.20);"
            "  border: 1px solid rgba(90,165,255,0.35);"
            "  border-radius: 8px; }"
            "QPushButton:hover { background: rgba(90,165,255,0.30); }")
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(self.chosen.emit)
        pair_row.addWidget(btn)
        v.addLayout(pair_row)

        meta1 = self._group_meta(g1)
        meta2 = self._group_meta(g2)
        if meta1 or meta2:
            meta_row = QHBoxLayout()
            meta_row.setSpacing(12)
            ml1 = QLabel(meta1)
            ml1.setStyleSheet(
                "font-size: 10px; color: rgba(255,255,255,0.38);")
            meta_row.addWidget(ml1)
            ml2 = QLabel(meta2)
            ml2.setStyleSheet(
                "font-size: 10px; color: rgba(255,255,255,0.38);")
            meta_row.addWidget(ml2)
            meta_row.addStretch()
            v.addLayout(meta_row)

    def _group_meta(self, group) -> str:
        if not group:
            return ""
        parts = []
        if group.album_count:
            parts.append(f"{group.album_count} alb")
        if group.track_count:
            parts.append(f"{group.track_count} canc")
        if group.genres:
            parts.append(", ".join(group.genres[:2]))
        return " · ".join(parts)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.chosen.emit()
        super().mousePressEvent(event)
