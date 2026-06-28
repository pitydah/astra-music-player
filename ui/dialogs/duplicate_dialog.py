"""DuplicateDialog — find and manage duplicate tracks in the library."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTreeWidget, QTreeWidgetItem, QHeaderView, QMessageBox,
)


class DuplicateDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self._db = db
        self.setWindowTitle("Duplicados en la biblioteca")
        self.setMinimumSize(700, 400)
        self.setStyleSheet("""
            QDialog { background: #090B11; border-radius: 14px; }
            QLabel { color: rgba(255,255,255,0.78); font-size: 13px; }
            QPushButton {
                background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.10);
                border-radius: 8px; color: #fff; padding: 8px 16px; font-size: 12px;
            }
            QPushButton:hover { background: rgba(255,255,255,0.10); }
            QTreeWidget {
                background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06);
                border-radius: 10px; color: #fff; outline: none;
            }
            QTreeWidget::item { min-height: 32px; padding: 4px 8px; }
            QHeaderView::section {
                background: rgba(255,255,255,0.04); color: rgba(255,255,255,0.68);
                border: none; padding: 6px 8px; font-size: 11px; font-weight: 600;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel("Canciones duplicadas en la biblioteca")
        title.setStyleSheet("font-size: 15px; font-weight: 700; color: #fff;")
        layout.addWidget(title)

        desc = QLabel(
            "Se agrupan por track_uid (MusicBrainz ID) o content_hash "
            "(contenido idéntico). Podés eliminar los duplicados que no "
            "necesites.")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        self._tree = QTreeWidget()
        self._tree.setColumnCount(4)
        self._tree.setHeaderLabels(["Grupo", "Archivo", "Artista", "Álbum"])
        self._tree.setRootIsDecorated(False)
        self._tree.setAlternatingRowColors(True)
        hdr = self._tree.header()
        hdr.setStretchLastSection(True)
        hdr.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(1, QHeaderView.Stretch)
        layout.addWidget(self._tree, 1)

        btn_layout = QHBoxLayout()
        self._scan_btn = QPushButton("Escanear duplicados")
        self._scan_btn.clicked.connect(self._scan)
        btn_layout.addWidget(self._scan_btn)

        self._remove_btn = QPushButton("Eliminar seleccionados")
        self._remove_btn.clicked.connect(self._remove_selected)
        self._remove_btn.setEnabled(False)
        btn_layout.addWidget(self._remove_btn)

        btn_layout.addStretch()

        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

    def _scan(self):
        self._tree.clear()
        duplicates = self._db.find_duplicates()
        if not duplicates:
            self._tree.setHeaderLabels(["", "No se encontraron duplicados", "", ""])
            self._tree.setRootIsDecorated(False)
            return

        for group in duplicates:
            key = group["key"]
            dup_type = group["type"]
            label = f"{'UID' if dup_type == 'uid' else 'Hash'}: {key[:12]}..."
            for fp, rid in zip(group["filepaths"], group["ids"], strict=False):
                item = QTreeWidgetItem(self._tree)
                item.setText(0, label)
                item.setText(1, fp)
                item.setData(1, Qt.UserRole, rid)
                # Look up metadata from DB
                row = self._db.conn.execute(
                    "SELECT artist, album FROM media_items WHERE id=?",
                    (rid,)).fetchone()
                item.setText(2, row[0] if row else "")
                item.setText(3, row[1] if row else "")
                item.setCheckState(0, Qt.Unchecked)
                label = ""

        self._remove_btn.setEnabled(True)

    def _remove_selected(self):
        to_remove = []
        for i in range(self._tree.topLevelItemCount()):
            item = self._tree.topLevelItem(i)
            if item.checkState(0) == Qt.Checked:
                rid = item.data(1, Qt.UserRole)
                if rid:
                    to_remove.append(rid)

        if not to_remove:
            QMessageBox.information(self, "Eliminar", "Seleccioná duplicados para eliminar.")
            return

        reply = QMessageBox.question(
            self, "Confirmar",
            f"¿Eliminar {len(to_remove)} archivo(s) de la biblioteca?\n"
            "Esto solo los remueve de la biblioteca, no del disco.",
            QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return

        for rid in to_remove:
            row = self._db.conn.execute(
                "SELECT filepath FROM media_items WHERE id=?", (rid,)).fetchone()
            if row:
                self._db.remove_file(row[0])
        self._scan()
