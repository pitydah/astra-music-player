"""DSPPage — control panel for audio output profiles, upsampling, and room correction.

Connects to existing audio profiles (output_profiles.py), DspState, and EQ system.
"""

from __future__ import annotations

import logging

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QComboBox, QCheckBox,
    QScrollArea, QFileDialog,
)

from ui.central.central_styles import (
    glass_card_qss, glass_button_qss, glass_combo_qss,
)
from core.settings_manager import get_str, get_bool, set_

logger = logging.getLogger("michi.dsp.ui")


class DSPPage(QWidget):
    navigate_requested = Signal(str)

    def __init__(self):
        super().__init__()
        self.setObjectName("dspPage")
        self.setStyleSheet("#dspPage { background: #090B11; }")
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        cl = QVBoxLayout(content)
        cl.setContentsMargins(40, 32, 40, 32)
        cl.setSpacing(16)

        title = QLabel("Perfiles de Salida")
        title.setStyleSheet(
            "color: rgba(255,255,255,0.92); font-size: 22px; "
            "font-weight: 700; background: transparent;"
        )
        cl.addWidget(title)

        sub = QLabel(
            "EXPERIMENTAL — Controla la ruta de audio: perfil de salida, "
            "upsampling, corrección de sala y estado del DAC.\n"
            "Upsampling y Room Correction son solo UI preliminar — "
            "no están conectados al pipeline de audio."
        )
        sub.setStyleSheet(
            "color: rgba(255,255,255,0.56); font-size: 13px; "
            "background: transparent;"
        )
        sub.setWordWrap(True)
        cl.addWidget(sub)

        # ── Current status ──
        self._status_card = self._build_card("Estado actual", self._build_status_panel())
        cl.addWidget(self._status_card)

        # ── Hybrid engine ──
        self._engine_card = self._build_card("Motor de audio", self._build_engine_panel())
        cl.addWidget(self._engine_card)

        # ── Output profile ──
        self._profile_card = self._build_card("Perfil de salida", self._build_profile_panel())
        cl.addWidget(self._profile_card)

        # ── Upsampling ──
        self._upsample_card = self._build_card("Upsampling", self._build_upsample_panel())
        cl.addWidget(self._upsample_card)

        # ── Room correction ──
        self._room_card = self._build_card("Corrección de sala", self._build_room_panel())
        cl.addWidget(self._room_card)

        cl.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)

        self._refresh_status()

    def _build_card(self, card_title: str, panel: QWidget) -> QFrame:
        card = QFrame()
        card.setObjectName(f"dspCard_{card_title[:20]}")
        card.setStyleSheet(glass_card_qss(card.objectName(), "base"))
        vl = QVBoxLayout(card)
        vl.setContentsMargins(20, 16, 20, 16)
        vl.setSpacing(10)

        t = QLabel(card_title)
        t.setStyleSheet(
            "color: rgba(255,255,255,0.88); font-size: 15px; "
            "font-weight: 600; background: transparent; border: none;"
        )
        vl.addWidget(t)
        vl.addWidget(panel)
        return card

    def _build_status_panel(self) -> QWidget:
        w = QWidget()
        wl = QVBoxLayout(w)
        wl.setContentsMargins(0, 0, 0, 0)
        wl.setSpacing(4)

        self._status_lines = {}
        for label_text, key in [
            ("Perfil activo", "profile"),
            ("Bit-perfect", "bitperfect"),
            ("Resample", "resample"),
            ("EQ", "eq"),
            ("ReplayGain", "replaygain"),
            ("Upsampling", "upsampling"),
            ("Room Correction", "room"),
            ("Motor", "engine"),
            ("Dispositivo", "device"),
        ]:
            row = QHBoxLayout()
            row.setSpacing(8)
            lbl = QLabel(label_text)
            lbl.setStyleSheet(
                "color: rgba(255,255,255,0.56); font-size: 11px; "
                "background: transparent;"
            )
            val = QLabel("--")
            val.setStyleSheet(
                "color: rgba(255,255,255,0.78); font-size: 11px; "
                "font-weight: 600; background: transparent;"
            )
            row.addWidget(lbl)
            row.addWidget(val, 1)
            wl.addLayout(row)
            self._status_lines[key] = val
            self._status_lines[key] = val

        self._refresh_btn = QPushButton("Actualizar estado")
        self._refresh_btn.setCursor(Qt.PointingHandCursor)
        self._refresh_btn.setStyleSheet(glass_button_qss("ghost"))
        self._refresh_btn.clicked.connect(self._refresh_status)
        wl.addWidget(self._refresh_btn)
        return w

    def _build_engine_panel(self) -> QWidget:
        w = QWidget()
        wl = QVBoxLayout(w)
        wl.setContentsMargins(0, 0, 0, 0)
        wl.setSpacing(8)

        row = QHBoxLayout()
        lbl = QLabel("Backend activo:")
        lbl.setStyleSheet("color: rgba(255,255,255,0.72); font-size: 13px; background: transparent;")
        row.addWidget(lbl)
        self._engine_status = QLabel("GStreamer")
        self._engine_status.setStyleSheet("color: #8FB7FF; font-size: 13px; font-weight: 600; background: transparent;")
        row.addWidget(self._engine_status)
        row.addStretch()
        wl.addLayout(row)

        self._mpd_status_label = QLabel("")
        self._mpd_status_label.setStyleSheet("color: rgba(255,255,255,0.56); font-size: 11px; background: transparent;")
        self._mpd_status_label.setWordWrap(True)
        wl.addWidget(self._mpd_status_label)

        btn_row = QHBoxLayout()
        self._mpd_start_btn = QPushButton("Iniciar MPD local")
        self._mpd_start_btn.setCursor(Qt.PointingHandCursor)
        self._mpd_start_btn.setStyleSheet(glass_button_qss("primary"))
        self._mpd_start_btn.clicked.connect(self._start_mpd)
        btn_row.addWidget(self._mpd_start_btn)

        self._mpd_stop_btn = QPushButton("Detener MPD local")
        self._mpd_stop_btn.setCursor(Qt.PointingHandCursor)
        self._mpd_stop_btn.setStyleSheet(glass_button_qss("secondary"))
        self._mpd_stop_btn.clicked.connect(self._stop_mpd)
        btn_row.addWidget(self._mpd_stop_btn)

        self._refresh_engine_btn = QPushButton("Actualizar")
        self._refresh_engine_btn.setCursor(Qt.PointingHandCursor)
        self._refresh_engine_btn.setStyleSheet(glass_button_qss("ghost"))
        self._refresh_engine_btn.clicked.connect(self._refresh_engine_status)
        btn_row.addWidget(self._refresh_engine_btn)

        btn_row.addStretch()
        wl.addLayout(btn_row)

        hint = QLabel(
            "Cambia a un perfil MPD (Hi-Fi MPD, Bit-Perfect MPD, etc.) "
            "para activar el motor MPD automáticamente.")
        hint.setStyleSheet("color: rgba(255,255,255,0.42); font-size: 11px; background: transparent;")
        hint.setWordWrap(True)
        wl.addWidget(hint)

        return w

    def _refresh_engine_status(self):
        try:
            from core.settings_manager import get_str
            profile_key = get_str("audio/profile") or "standard"
            from audio.output_profiles import get_profile
            prof = get_profile(profile_key)
            if prof.preferred_backend == "mpd":
                self._engine_status.setText("MPD")
                self._engine_status.setStyleSheet(
                    "color: #4caf50; font-size: 13px; font-weight: 600; background: transparent;")
                self._mpd_status_label.setText(
                    "Modo Hi-Fi activo — EQ, ReplayGain, Spectrum y volumen digital desactivados")
            else:
                self._engine_status.setText("GStreamer")
                self._engine_status.setStyleSheet(
                    "color: #8FB7FF; font-size: 13px; font-weight: 600; background: transparent;")
                self._mpd_status_label.setText(
                    "Todas las funciones DSP disponibles")
            self._update_mpd_buttons()
        except Exception as e:
            logger.warning("Engine status refresh error: %s", e)

    def _update_mpd_buttons(self):
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if not app:
            return
        for w in app.topLevelWidgets():
            ctx = getattr(w, '_ctx', None) or getattr(w, '_app_context', None)
            if ctx and hasattr(ctx, 'playback') and ctx.playback:
                try:
                    status = ctx.playback.get_mpd_status()
                    running = status.get("running", False)
                    installed = status.get("installed", False)
                    self._mpd_start_btn.setEnabled(installed and not running)
                    self._mpd_stop_btn.setEnabled(running)
                    self._mpd_start_btn.setText(
                        "Iniciar MPD local" if not running else "MPD en ejecución")
                except Exception:
                    pass
                break

    def _start_mpd(self):
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if not app:
            return
        for w in app.topLevelWidgets():
            ctx = getattr(w, '_ctx', None) or getattr(w, '_app_context', None)
            if ctx and hasattr(ctx, 'playback') and ctx.playback:
                ok = ctx.playback.start_mpd_service()
                if ok:
                    self._mpd_status_label.setText("MPD local iniciado")
                else:
                    self._mpd_status_label.setText("Error al iniciar MPD local")
                self._update_mpd_buttons()
                break

    def _stop_mpd(self):
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if not app:
            return
        for w in app.topLevelWidgets():
            ctx = getattr(w, '_ctx', None) or getattr(w, '_app_context', None)
            if ctx and hasattr(ctx, 'playback') and ctx.playback:
                ctx.playback.stop_mpd_service()
                self._mpd_status_label.setText("MPD local detenido")
                self._update_mpd_buttons()
                break

    def _build_profile_panel(self) -> QWidget:
        w = QWidget()
        wl = QHBoxLayout(w)
        wl.setContentsMargins(0, 0, 0, 0)
        wl.setSpacing(10)

        from audio.output_profiles import PROFILES
        self._profile_combo = QComboBox()
        self._profile_combo.setStyleSheet(glass_combo_qss())
        for key, prof in PROFILES.items():
            label = f"{prof.name} {'🔒' if prof.bitperfect else ''}"
            self._profile_combo.addItem(label, key)
        current = get_str("audio/profile") or "standard"
        for i in range(self._profile_combo.count()):
            if self._profile_combo.itemData(i) == current:
                self._profile_combo.setCurrentIndex(i)
                break

        wl.addWidget(self._profile_combo)

        self._apply_profile_btn = QPushButton("Aplicar")
        self._apply_profile_btn.setCursor(Qt.PointingHandCursor)
        self._apply_profile_btn.setStyleSheet(glass_button_qss("primary"))
        self._apply_profile_btn.clicked.connect(self._apply_profile)
        wl.addWidget(self._apply_profile_btn)

        self._bitperfect_btn = QPushButton("Modo Bit-perfect")
        self._bitperfect_btn.setCursor(Qt.PointingHandCursor)
        self._bitperfect_btn.setStyleSheet(glass_button_qss("secondary"))
        self._bitperfect_btn.clicked.connect(self._set_bitperfect)
        wl.addWidget(self._bitperfect_btn)

        wl.addStretch()
        return w

    def _build_upsample_panel(self) -> QWidget:
        w = QWidget()
        wl = QVBoxLayout(w)
        wl.setContentsMargins(0, 0, 0, 0)
        wl.setSpacing(8)

        row = QHBoxLayout()
        self._upsample_enable = QCheckBox("Activar upsampling")
        self._upsample_enable.setEnabled(False)
        self._upsample_enable.setStyleSheet(
            "color: rgba(255,255,255,0.42); font-size: 12px; "
            "background: transparent;"
        )
        row.addWidget(self._upsample_enable)

        self._upsample_rate = QComboBox()
        self._upsample_rate.setEnabled(False)
        self._upsample_rate.setStyleSheet(glass_combo_qss())
        for label, sr in [("2x (88.2/96 kHz)", 2), ("4x (176.4/192 kHz)", 4)]:
            self._upsample_rate.addItem(label, sr)
        row.addWidget(self._upsample_rate)
        row.addStretch()
        wl.addLayout(row)

        hint = QLabel(
            "⚠ UI preliminar — el upsampling no está conectado "
            "al pipeline de GStreamer. Esta sección es solo "
            "interfaz de configuración futura."
        )
        hint.setStyleSheet(
            "color: rgba(255,255,255,0.42); font-size: 11px; "
            "background: transparent;"
        )
        hint.setWordWrap(True)
        wl.addWidget(hint)
        return w

    def _build_room_panel(self) -> QWidget:
        w = QWidget()
        wl = QVBoxLayout(w)
        wl.setContentsMargins(0, 0, 0, 0)
        wl.setSpacing(8)

        row = QHBoxLayout()
        self._room_enable = QCheckBox("Activar corrección de sala")
        self._room_enable.setEnabled(False)
        self._room_enable.setStyleSheet(
            "color: rgba(255,255,255,0.42); font-size: 12px; "
            "background: transparent;"
        )
        row.addWidget(self._room_enable)

        self._room_file_btn = QPushButton("Cargar impulso WAV...")
        self._room_file_btn.setEnabled(False)
        self._room_file_btn.setCursor(Qt.PointingHandCursor)
        self._room_file_btn.setStyleSheet(glass_button_qss("secondary"))
        self._room_file_btn.clicked.connect(self._load_impulse)
        row.addWidget(self._room_file_btn)

        self._room_file_label = QLabel("(ninguno)")
        self._room_file_label.setStyleSheet(
            "color: rgba(255,255,255,0.50); font-size: 11px; "
            "background: transparent;"
        )
        row.addWidget(self._room_file_label, 1)
        row.addStretch()
        wl.addLayout(row)

        hint = QLabel(
            "⚠ UI preliminar — la convolución FIR no está implementada. "
            "Seleccionar un WAV no activa la corrección de sala. "
            "Pendiente de motor FIR."
        )
        hint.setStyleSheet(
            "color: rgba(255,255,255,0.42); font-size: 11px; "
            "background: transparent;"
        )
        hint.setWordWrap(True)
        wl.addWidget(hint)
        return w

    # ── Actions ──

    def _refresh_status(self):
        try:
            profile_key = get_str("audio/profile") or "standard"
            from audio.output_profiles import PROFILES
            prof = PROFILES.get(profile_key)
            self._status_lines["profile"].setText(
                prof.name if prof else profile_key
            )
            self._status_lines["bitperfect"].setText(
                "Perfil bit-perfect solicitado" if prof and prof.bitperfect
                else "No solicitado"
            )
            self._status_lines["resample"].setText(
                "Permitido" if get_bool("audio/allow_resample")
                else "No permitido"
            )
            self._status_lines["eq"].setText(
                "Activo" if get_bool("audio/eq/enabled") else "Inactivo"
            )
            self._status_lines["replaygain"].setText(
                get_str("audio/replaygain/mode") or "off"
            )
            self._status_lines["device"].setText(
                get_str("audio/output_device") or "auto"
            )
            self._status_lines["engine"].setText(
                "MPD" if prof and prof.preferred_backend == "mpd" else "GStreamer"
            )
            self._refresh_engine_status()
        except Exception as e:
            logger.warning("Status refresh error: %s", e)

    def _apply_profile(self):
        key = self._profile_combo.currentData()
        if key:
            set_("audio/profile", key)
            self._refresh_status()
            self._refresh_engine_status()
            self._notify_backend_switch(key)
            from audio.output_profiles import get_profile
            prof = get_profile(key)
            logger.info("Audio profile set to: %s (backend: %s)",
                        key, prof.preferred_backend)

    def _set_bitperfect(self):
        set_("audio/profile", "bitperfect_pcm")
        set_("audio/allow_resample", False)
        for i in range(self._profile_combo.count()):
            if self._profile_combo.itemData(i) == "bitperfect_pcm":
                self._profile_combo.setCurrentIndex(i)
                break
        self._refresh_status()
        self._refresh_engine_status()
        self._notify_backend_switch("bitperfect_pcm")
        logger.info("Bit-perfect mode activated")

    def _notify_backend_switch(self, profile_key: str):
        """Notify PlayerService to switch backend for this profile."""
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if not app:
            return
        for w in app.topLevelWidgets():
            ctx = getattr(w, '_ctx', None) or getattr(w, '_app_context', None)
            if ctx and hasattr(ctx, 'playback') and ctx.playback:
                try:
                    ctx.playback.switch_backend_for_profile(profile_key)
                except Exception as exc:
                    logger.warning("Backend switch failed: %s", exc)
                break

    def _load_impulse(self):
        fp, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar respuesta al impulso", "",
            "WAV (*.wav)"
        )
        if fp:
            self._room_file_label.setText(fp.split("/")[-1])
            logger.info("Impulse response loaded: %s", fp)
