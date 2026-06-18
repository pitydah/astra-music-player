"""Main equalizer dialog — basic ↔ advanced toggle, spectrum, curve."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox,
    QLabel, QCheckBox, QMessageBox, QTabWidget, QWidget,
)

from eq_basic import GraphicEqWidget
from eq_advanced import AdvancedEqWidget
from eq_curve import EqCurveWidget
from spectrum import SpectrumWidget
from eq_presets import (
    GRAPHIC_PRESETS, PARAMETRIC_PRESETS,
    load_graphic_preset, load_parametric_preset,
)
from eq_convert import graphic_to_parametric, parametric_to_graphic


class EqDialog(QDialog):
    """Full equalizer panel with basic/advanced modes."""

    eq_bypass_changed = Signal(bool)
    eq_bands_graphic_changed = Signal(list)
    eq_bands_parametric_changed = Signal(list)
    preamp_changed = Signal(float)
    spectrum_mode_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ecualizador")
        self.resize(900, 620)
        self.setMinimumSize(750, 450)
        from theme import apply_dialog_shadow
        apply_dialog_shadow(self)
        self._mode = "basic"
        self._ab_state = None  # for A/B comparison

        layout = QVBoxLayout(self)

        # ── Mode toggle ──
        mode_row = QHBoxLayout()
        mode_row.addWidget(QLabel("Modo:"))
        self._mode_combo = QComboBox()
        self._mode_combo.addItem("Básico (31 bandas)", "basic")
        self._mode_combo.addItem("Avanzado (Paramétrico)", "advanced")
        self._mode_combo.currentIndexChanged.connect(self._on_mode)
        mode_row.addWidget(self._mode_combo)
        mode_row.addStretch()

        self._preset_combo = QComboBox()
        self._preset_combo.addItems(sorted(GRAPHIC_PRESETS.keys()))
        self._preset_combo.currentTextChanged.connect(self._on_preset)
        mode_row.addWidget(QLabel("Preset:"))
        mode_row.addWidget(self._preset_combo)

        save_btn = QPushButton("Guardar")
        save_btn.clicked.connect(self._save_preset)
        mode_row.addWidget(save_btn)

        ab_btn = QPushButton("A/B")
        ab_btn.setToolTip("Comparar dos configuraciones de EQ")
        ab_btn.clicked.connect(self._ab_compare)
        mode_row.addWidget(ab_btn)

        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self._reset)
        mode_row.addWidget(reset_btn)

        layout.addLayout(mode_row)

        # ── Spectrum + Curve ──
        self._spectrum = SpectrumWidget()
        layout.addWidget(self._spectrum, 2)

        self._curve = EqCurveWidget()
        layout.addWidget(self._curve, 2)

        # ── Stacked: basic ↔ advanced ──
        self._basic = GraphicEqWidget()
        self._advanced = AdvancedEqWidget()
        self._advanced.bands_changed.connect(self._on_advanced_change)
        self._advanced.preamp_changed.connect(self._on_preamp_adv)

        layout.addWidget(self._basic, 4)
        layout.addWidget(self._advanced, 4)
        self._advanced.hide()

        # ── Bottom toggles ──
        bottom = QHBoxLayout()
        self._bypass_cb = QCheckBox("Ecualizador activo")
        self._bypass_cb.setChecked(True)
        self._bypass_cb.toggled.connect(lambda v: self.eq_bypass_changed.emit(not v))
        bottom.addWidget(self._bypass_cb)

        self._spectrum_cb = QCheckBox("Analizador de espectro")
        self._spectrum_cb.setChecked(True)
        self._spectrum_cb.toggled.connect(
            lambda v: self._spectrum.setVisible(v))
        bottom.addWidget(self._spectrum_cb)

        bottom.addStretch()
        self._preamp_lbl = QLabel("Preamp: +0.0dB")
        self._preamp_lbl.setStyleSheet("color: #8e8e93;")
        bottom.addWidget(self._preamp_lbl)

        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.close)
        bottom.addWidget(close_btn)
        layout.addLayout(bottom)

        # ── Wire basic sliders ──
        self._basic.bands_changed.connect(self._on_basic_change)

    # ── Mode switching ──

    def _on_mode(self):
        mode = self._mode_combo.currentData()
        if mode == self._mode:
            return

        if self._mode == "basic":
            # Convert basic → advanced
            bands, preamp = graphic_to_parametric(self._basic.get_bands())
            self._advanced.load_preset(bands, preamp)
        else:
            # Convert advanced → basic
            configs, preamp = self._advanced.get_config()
            gbands = parametric_to_graphic(configs, preamp)
            self._basic.set_bands(gbands)

        self._mode = mode
        if mode == "basic":
            self._basic.show()
            self._advanced.hide()
        else:
            self._basic.hide()
            self._advanced.show()

    # ── Presets ──

    def _on_preset(self, name: str):
        if self._mode == "basic":
            bands = load_graphic_preset(name)
            self._basic.set_bands(bands)
            self.eq_bands_graphic_changed.emit(bands)
            # Update curve
            pbands, _ = graphic_to_parametric(bands)
            self._curve.set_bands(pbands, 0.0)
        else:
            bands = load_parametric_preset(name)
            self._advanced.load_preset(bands, 0.0)
            self.eq_bands_parametric_changed.emit(bands)
            self._curve.set_bands(bands, 0.0)

    def _save_preset(self):
        from eq_presets import save_custom_presets, load_custom_presets
        presets = load_custom_presets()
        if self._mode == "basic":
            presets[f"Custom_{len(presets)}"] = {
                "mode": "graphic",
                "bands": self._basic.get_bands(),
                "preamp": 0.0,
            }
        save_custom_presets(presets)
        # Refresh combo
        self._preset_combo.blockSignals(True)
        self._preset_combo.clear()
        self._preset_combo.addItems(sorted(GRAPHIC_PRESETS.keys()))
        for k in presets:
            if self._preset_combo.findText(k) < 0:
                self._preset_combo.addItem(k)
        self._preset_combo.blockSignals(False)

    def _ab_compare(self):
        if self._ab_state is None:
            # Save current as A
            if self._mode == "basic":
                self._ab_state = ("basic", self._basic.get_bands(), 0.0)
            else:
                self._ab_state = ("advanced", self._advanced.get_config())
            QMessageBox.information(self, "A/B",
                "Estado A guardado. Modifica el EQ y presiona A/B para comparar.")
        else:
            QMessageBox.information(self, "A/B", "Volviendo al estado A.")
            if self._ab_state[0] == "basic":
                self._basic.set_bands(self._ab_state[1])
            else:
                bands, preamp = self._ab_state[1]
                self._advanced.load_preset(bands, preamp)
            self._ab_state = None

    def _reset(self):
        if self._mode == "basic":
            self._basic.reset()
            self.eq_bands_graphic_changed.emit([0.0] * 31)
        else:
            self._advanced.reset()
            self.eq_bands_parametric_changed.emit([])

    # ── Slider handlers ──

    def _on_basic_change(self, idx: int, value: float):
        bands = self._basic.get_bands()
        self.eq_bands_graphic_changed.emit(bands)
        # Update curve
        pbands, _ = graphic_to_parametric(bands)
        self._curve.set_bands(pbands, 0.0)

    def _on_advanced_change(self, bands: list):
        self.eq_bands_parametric_changed.emit(bands)
        preamp = self._advanced.get_config()[1]
        self._curve.set_bands(bands, preamp)

    def _on_preamp_adv(self, db: float):
        self._preamp_lbl.setText(f"Preamp: {db:+.1f}dB")
        self.preamp_changed.emit(db)
