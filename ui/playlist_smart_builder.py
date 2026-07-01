"""Playlist Smart Builder — rule-based smart playlist creation UI."""
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QComboBox, QFrame, QSpinBox, QCheckBox,
)

from ui.central.central_styles import glass_button_qss

_FIELDS = [
    ("title", "Título"), ("artist", "Artista"), ("album", "Álbum"),
    ("albumartist", "Artista álbum"), ("genre", "Género"),
    ("year", "Año"), ("ext", "Formato"), ("bit_depth", "Bit Depth"),
    ("sample_rate", "Sample Rate"), ("bitrate", "Bitrate"),
    ("duration", "Duración"), ("bpm", "BPM"), ("key", "Tonalidad"),
    ("favorite", "Favorito"), ("play_count", "Reproducciones"),
]
_OPERATORS = [
    ("equals", "igual a"), ("not_equals", "distinto de"),
    ("contains", "contiene"), ("not_contains", "no contiene"),
    ("greater_than", "mayor que"), ("less_than", "menor que"),
    ("is_empty", "vacío"), ("is_not_empty", "no vacío"),
]


class PlaylistSmartBuilder(QWidget):
    smart_playlist_created = Signal(int, str)  # pid, name

    def __init__(self, parent=None):
        super().__init__(parent)
        self._db_conn = None
        self._preview_ids = []
        self.setWindowTitle("Smart Playlist Builder")
        self.setStyleSheet("background: #090B11;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        title = QLabel("Constructor de playlists inteligentes")
        title.setStyleSheet("color: white; font-size: 20px; font-weight: 700; background: transparent;")
        layout.addWidget(title)

        # Name
        name_row = QHBoxLayout()
        name_row.addWidget(QLabel("Nombre:"))
        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText("Mi Smart Playlist")
        name_row.addWidget(self._name_input, 1)
        layout.addLayout(name_row)

        # Rule row
        rule_frame = QFrame()
        rule_frame.setStyleSheet("QFrame { background: rgba(255,255,255,0.02); border-radius: 8px; }")
        rule_layout = QHBoxLayout(rule_frame)
        rule_layout.setContentsMargins(8, 8, 8, 8)

        self._field_combo = QComboBox()
        for key, label in _FIELDS:
            self._field_combo.addItem(label, key)

        self._op_combo = QComboBox()
        for key, label in _OPERATORS:
            self._op_combo.addItem(label, key)

        self._value_input = QLineEdit()
        self._value_input.setPlaceholderText("Valor")

        rule_layout.addWidget(QLabel("Campo:"))
        rule_layout.addWidget(self._field_combo)
        rule_layout.addWidget(QLabel("Op:"))
        rule_layout.addWidget(self._op_combo)
        rule_layout.addWidget(QLabel("Valor:"))
        rule_layout.addWidget(self._value_input, 1)
        layout.addWidget(rule_frame)

        # Limit + sort
        opt_row = QHBoxLayout()
        opt_row.addWidget(QLabel("Límite:"))
        self._limit_input = QSpinBox()
        self._limit_input.setRange(0, 9999)
        self._limit_input.setValue(0)
        self._limit_input.setSpecialValueText("Sin límite")
        opt_row.addWidget(self._limit_input)

        self._random_check = QCheckBox("Aleatorio")
        opt_row.addWidget(self._random_check)

        opt_row.addStretch()
        layout.addLayout(opt_row)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        preview_btn = QPushButton("Previsualizar")
        preview_btn.setStyleSheet(glass_button_qss("primary"))
        preview_btn.clicked.connect(self._preview)
        btn_row.addWidget(preview_btn)

        save_btn = QPushButton("Guardar Smart Playlist")
        save_btn.setStyleSheet(glass_button_qss("primary"))
        save_btn.clicked.connect(self._save)
        btn_row.addWidget(save_btn)

        close_btn = QPushButton("Cerrar")
        close_btn.setStyleSheet(glass_button_qss("secondary"))
        close_btn.clicked.connect(self.close)
        btn_row.addWidget(close_btn)

        layout.addLayout(btn_row)

        # Preview count
        self._preview_label = QLabel("")
        self._preview_label.setStyleSheet("color: rgba(255,255,255,0.60); font-size: 12px; background: transparent;")
        layout.addWidget(self._preview_label)
        layout.addStretch()

    def set_db_conn(self, conn):
        self._db_conn = conn

    def _build_rules_json(self) -> str:
        import json
        rules = [{
            "field": self._field_combo.currentData(),
            "op": self._op_combo.currentData(),
            "value": self._value_input.text().strip(),
        }]
        rule_set = {"rules": rules}
        if self._limit_input.value() > 0:
            rule_set["limit"] = self._limit_input.value()
        if self._random_check.isChecked():
            rule_set["random"] = True
        return json.dumps(rule_set)

    def _preview(self):
        if not self._db_conn:
            self._preview_label.setText("Base de datos no disponible")
            return
        from library.playlists.playlist_smart_engine import evaluate_rules
        rules_json = self._build_rules_json()
        ids = evaluate_rules(rules_json, self._db_conn)
        self._preview_ids = ids
        limit = self._limit_input.value()
        shown = min(len(ids), limit) if limit else len(ids)
        self._preview_label.setText(f"{shown} canciones encontradas")

    def _save(self):
        if not self._db_conn:
            return
        name = self._name_input.text().strip()
        if not name:
            self._preview_label.setText("Ingresa un nombre")
            return
        from library.playlists.playlist_smart_engine import create_smart_playlist, refresh_smart_playlist
        from library.playlists.playlist_store import PlaylistStore
        store = PlaylistStore(self._db_conn)
        rules_json = self._build_rules_json()
        pid = create_smart_playlist(store, name, rules_json)
        count = refresh_smart_playlist(store, pid, self._db_conn)
        self.smart_playlist_created.emit(pid, name)
        self._preview_label.setText(f"Smart playlist '{name}' creada con {count} canciones")
