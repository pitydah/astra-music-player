"""Preferences Window — 14-category settings dialog with sidebar."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog, QHBoxLayout, QVBoxLayout, QListWidget, QStackedWidget,
    QLineEdit, QPushButton, QDialogButtonBox, QWidget, QFormLayout,
    QCheckBox, QComboBox, QSlider, QSpinBox, QLabel, QFileDialog,
    QGroupBox, QListWidgetItem, QFrame, QScrollArea,
)
from PySide6.QtGui import QColor, QIcon

from ui.icons import get_icon
import core.settings_manager as sm
import os


def _make_scroll(page_widget: QWidget) -> QScrollArea:
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QScrollArea.NoFrame)
    scroll.setWidget(page_widget)
    scroll.setStyleSheet("QScrollArea{background:transparent;border:none;} "
                         "QScrollArea QWidget{background:transparent;}")
    return scroll


class _GeneralPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QFormLayout(self)
        layout.setSpacing(12)
        self._theme = QComboBox()
        self._theme.addItems(["Oscuro (Glass)", "Claro", "Sistema"])
        self._theme.setCurrentText(
            str(sm.get("general/start_minimized")) if False else "Oscuro (Glass)")
        self._confirm = QCheckBox()
        self._confirm.setChecked(sm.get("general/confirm_exit"))
        self._remember = QCheckBox()
        self._remember.setChecked(sm.get("general/remember_session"))
        self._music = QLineEdit(sm.get("general/music_folder"))
        music_btn = QPushButton("...")
        music_btn.clicked.connect(lambda: self._browse(self._music))
        row = QHBoxLayout()
        row.addWidget(self._music); row.addWidget(music_btn)
        self._downloads = QLineEdit(sm.get("general/download_folder"))
        dl_btn = QPushButton("...")
        dl_btn.clicked.connect(lambda: self._browse(self._downloads))
        row2 = QHBoxLayout()
        row2.addWidget(self._downloads); row2.addWidget(dl_btn)

        layout.addRow("Tema:", self._theme)
        layout.addRow("Confirmar salida:", self._confirm)
        layout.addRow("Recordar sesión:", self._remember)
        layout.addRow("Carpeta de música:", row)
        layout.addRow("Carpeta descargas:", row2)

    def _browse(self, edit):
        path = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta")
        if path:
            edit.setText(path)

    def apply(self):
        sm.set_("general/confirm_exit", self._confirm.isChecked())
        sm.set_("general/remember_session", self._remember.isChecked())
        sm.set_("general/music_folder", self._music.text())
        sm.set_("general/download_folder", self._downloads.text())


class _InterfacePage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QFormLayout(self)
        layout.setSpacing(12)
        self._menubar = QCheckBox()
        self._menubar.setChecked(sm.get("interface/show_menubar"))
        self._badge = QCheckBox()
        self._badge.setChecked(sm.get("interface/show_quality_badge"))
        self._cover = QSlider(Qt.Horizontal)
        self._cover.setRange(120, 400)
        self._cover.setValue(sm.get("interface/cover_size"))
        self._compact = QCheckBox()
        self._compact.setChecked(sm.get("interface/compact_mode"))

        layout.addRow("Mostrar barra menú:", self._menubar)
        layout.addRow("Badge de calidad:", self._badge)
        layout.addRow("Tamaño carátula:", self._cover)
        layout.addRow("Modo compacto:", self._compact)

    def apply(self):
        sm.set_("interface/show_menubar", self._menubar.isChecked())
        sm.set_("interface/show_quality_badge", self._badge.isChecked())
        sm.set_("interface/cover_size", self._cover.value())
        sm.set_("interface/compact_mode", self._compact.isChecked())


class _LibraryPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QFormLayout(self)
        layout.setSpacing(12)
        self._auto = QCheckBox()
        self._auto.setChecked(sm.get("library/auto_scan"))
        self._hidden = QCheckBox()
        self._hidden.setChecked(sm.get("library/exclude_hidden"))
        self._cache = QSpinBox()
        self._cache.setRange(50, 500)
        self._cache.setValue(sm.get("library/covers_cache_size"))

        self._clean = QPushButton("Limpiar archivos huérfanos")
        self._rescan = QPushButton("Reescanear carátulas")

        layout.addRow("Escaneo al iniciar:", self._auto)
        layout.addRow("Excluir ocultos:", self._hidden)
        layout.addRow("Caché carátulas:", self._cache)
        layout.addRow(self._clean)
        layout.addRow(self._rescan)

    def apply(self):
        sm.set_("library/auto_scan", self._auto.isChecked())
        sm.set_("library/exclude_hidden", self._hidden.isChecked())
        sm.set_("library/covers_cache_size", self._cache.value())


class _PlaybackPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QFormLayout(self)
        layout.setSpacing(12)
        self._vol = QSlider(Qt.Horizontal)
        self._vol.setRange(0, 100)
        self._vol.setValue(sm.get("playback/default_volume"))
        self._repeat = QComboBox()
        self._repeat.addItems(["none", "all", "one"])
        self._repeat.setCurrentText(sm.get("playback/repeat_mode"))
        self._shuffle = QCheckBox()
        self._shuffle.setChecked(sm.get("playback/shuffle_default"))
        self._rg = QCheckBox()
        self._rg.setChecked(sm.get("playback/replaygain"))
        self._crossfade = QSlider(Qt.Horizontal)
        self._crossfade.setRange(0, 12)
        self._crossfade.setValue(sm.get("playback/crossfade"))
        self._gapless = QCheckBox()
        self._gapless.setChecked(sm.get("playback/gapless"))

        layout.addRow("Volumen inicial:", self._vol)
        layout.addRow("Repetición:", self._repeat)
        layout.addRow("Aleatorio:", self._shuffle)
        layout.addRow("ReplayGain:", self._rg)
        layout.addRow("Crossfade (s):", self._crossfade)
        layout.addRow("Gapless:", self._gapless)

    def apply(self):
        sm.set_("playback/default_volume", self._vol.value())
        sm.set_("playback/repeat_mode", self._repeat.currentText())
        sm.set_("playback/shuffle_default", self._shuffle.isChecked())
        sm.set_("playback/replaygain", self._rg.isChecked())
        sm.set_("playback/crossfade", self._crossfade.value())
        sm.set_("playback/gapless", self._gapless.isChecked())


class _AudioPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QFormLayout(self)
        layout.setSpacing(12)
        self._dev = QComboBox()
        self._dev.addItems(["default", "hw:0,0", "hw:1,0", "hw:0,3", "pipewire"])
        self._dev.setCurrentText(sm.get("audio/device"))
        self._mode = QComboBox()
        self._mode.addItems(["standard", "bitperfect", "dop"])
        self._mode.setCurrentText(sm.get("audio/mode"))
        self._rate = QComboBox()
        self._rate.addItems(["0 (auto)", "44100", "48000", "96000", "192000", "384000"])
        idx = self._rate.findText(str(sm.get("audio/sample_rate")))
        self._rate.setCurrentIndex(idx if idx >= 0 else 0)
        self._buf = QComboBox()
        self._buf.addItems(["50", "100", "200", "500", "1000"])
        self._buf.setCurrentText(str(sm.get("audio/buffer_ms")))

        layout.addRow("Dispositivo:", self._dev)
        layout.addRow("Modo:", self._mode)
        layout.addRow("Sample rate:", self._rate)
        layout.addRow("Buffer (ms):", self._buf)

    def apply(self):
        sm.set_("audio/device", self._dev.currentText())
        sm.set_("audio/mode", self._mode.currentText())
        sm.set_("audio/sample_rate", int(self._rate.currentText().split()[0]))
        sm.set_("audio/buffer_ms", int(self._buf.currentText()))


class _EQPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QFormLayout(self)
        layout.setSpacing(12)
        self._enabled = QCheckBox()
        self._enabled.setChecked(sm.get("eq/enabled"))
        self._mode = QComboBox()
        self._mode.addItems(["graphic", "parametric"])
        self._mode.setCurrentText(sm.get("eq/mode"))
        self._preset = QComboBox()
        self._preset.addItems(["Flat", "Rock", "Pop", "Jazz", "Classical", "Hip-Hop",
                              "Electronic", "Bass Boost", "Treble Boost", "Loudness"])
        self._preset.setCurrentText(sm.get("eq/preset"))
        self._preamp = QSlider(Qt.Horizontal)
        self._preamp.setRange(-12, 12)
        self._preamp.setValue(int(sm.get("eq/preamp")))
        self._spectrum = QCheckBox()
        self._spectrum.setChecked(sm.get("eq/show_spectrum"))

        layout.addRow("EQ activo:", self._enabled)
        layout.addRow("Modo:", self._mode)
        layout.addRow("Preset:", self._preset)
        layout.addRow("Pre‑amp (dB):", self._preamp)
        layout.addRow("Mostrar espectro:", self._spectrum)

    def apply(self):
        sm.set_("eq/enabled", self._enabled.isChecked())
        sm.set_("eq/mode", self._mode.currentText())
        sm.set_("eq/preset", self._preset.currentText())
        sm.set_("eq/preamp", float(self._preamp.value()))
        sm.set_("eq/show_spectrum", self._spectrum.isChecked())


class _TransmitPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QFormLayout(self)
        layout.setSpacing(12)
        self._quality = QComboBox()
        self._quality.addItems(["128", "256", "320", "lossless"])
        self._quality.setCurrentText(sm.get("transmit/quality"))
        self._latency = QSpinBox()
        self._latency.setRange(0, 500)
        self._latency.setValue(sm.get("transmit/latency"))
        self._local = QCheckBox()
        self._local.setChecked(sm.get("transmit/keep_local"))
        layout.addRow("Calidad (kbps):", self._quality)
        layout.addRow("Latencia (ms):", self._latency)
        layout.addRow("Mantener local:", self._local)

    def apply(self):
        sm.set_("transmit/quality", self._quality.currentText())
        sm.set_("transmit/latency", self._latency.value())
        sm.set_("transmit/keep_local", self._local.isChecked())


class _ServerPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(
            "Usa el menú Transmitir > Añadir servidor para gestionar servidores."))


class _SyncPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QFormLayout(self)
        layout.setSpacing(12)
        self._auto = QCheckBox()
        self._auto.setChecked(sm.get("sync/auto_start"))
        self._port = QSpinBox()
        self._port.setRange(1024, 65535)
        self._port.setValue(sm.get("sync/port"))
        self._alias = QLineEdit(sm.get("sync/alias"))
        self._discovery = QCheckBox()
        self._discovery.setChecked(sm.get("sync/discovery_enabled"))
        self._interval = QSpinBox()
        self._interval.setRange(1, 60)
        self._interval.setValue(sm.get("sync/announce_interval"))

        layout.addRow("Iniciar al abrir:", self._auto)
        layout.addRow("Puerto:", self._port)
        layout.addRow("Alias:", self._alias)
        layout.addRow("Descubrimiento:", self._discovery)
        layout.addRow("Intervalo (s):", self._interval)

    def apply(self):
        sm.set_("sync/auto_start", self._auto.isChecked())
        sm.set_("sync/port", self._port.value())
        sm.set_("sync/alias", self._alias.text())
        sm.set_("sync/discovery_enabled", self._discovery.isChecked())
        sm.set_("sync/announce_interval", self._interval.value())


class _RadioPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QFormLayout(self)
        layout.setSpacing(12)
        self._auto = QCheckBox()
        self._auto.setChecked(sm.get("radio/auto_update"))
        self._reconnect = QCheckBox()
        self._reconnect.setChecked(sm.get("radio/auto_reconnect"))
        self._reconn = QSpinBox()
        self._reconn.setRange(1, 30)
        self._reconn.setValue(sm.get("radio/reconnect_interval"))
        self._record = QCheckBox()
        self._record.setChecked(sm.get("radio/record_streams"))
        self._rec_folder = QLineEdit(sm.get("radio/record_folder"))
        rec_btn = QPushButton("...")
        rec_btn.clicked.connect(lambda: self._browse(self._rec_folder))
        row = QHBoxLayout()
        row.addWidget(self._rec_folder); row.addWidget(rec_btn)
        self._format = QComboBox()
        self._format.addItems(["mp3", "flac", "ogg"])

        layout.addRow("Actualizar al iniciar:", self._auto)
        layout.addRow("Auto‑reconectar:", self._reconnect)
        layout.addRow("Intervalo reconexión:", self._reconn)
        layout.addRow("Grabar streams:", self._record)
        layout.addRow("Carpeta grabaciones:", row)
        layout.addRow("Formato:", self._format)

    def _browse(self, edit):
        path = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta")
        if path:
            edit.setText(path)

    def apply(self):
        sm.set_("radio/auto_update", self._auto.isChecked())
        sm.set_("radio/auto_reconnect", self._reconnect.isChecked())
        sm.set_("radio/reconnect_interval", self._reconn.value())
        sm.set_("radio/record_streams", self._record.isChecked())
        sm.set_("radio/record_folder", self._rec_folder.text())


class _KeyboardPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QFormLayout(self)
        layout.setSpacing(12)
        self._global = QCheckBox()
        self._global.setChecked(sm.get("shortcuts/global_enabled"))
        info = QLabel(
            "Atajos predefinidos:\n"
            "  Espacio       — Reproducir/Pausa\n"
            "  Ctrl + →      — Siguiente\n"
            "  Ctrl + ←      — Anterior\n"
            "  Ctrl + ↑      — Subir volumen\n"
            "  Ctrl + ↓      — Bajar volumen\n"
            "  Ctrl + M      — Silencio\n"
            "  Ctrl + P      — Preferencias"
        )
        info.setStyleSheet("color: rgba(255,255,255,0.4); font-size: 12px;")
        layout.addRow("Atajos globales:", self._global)
        layout.addRow(info)

    def apply(self):
        sm.set_("shortcuts/global_enabled", self._global.isChecked())


class _AdvancedPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QFormLayout(self)
        layout.setSpacing(12)
        self._debug = QCheckBox()
        self._debug.setChecked(sm.get("advanced/debug_log"))
        self._level = QComboBox()
        self._level.addItems(["Error", "Warning", "Info", "Debug"])
        self._level.setCurrentText(sm.get("advanced/log_level"))
        self._threads = QSpinBox()
        self._threads.setRange(1, 16)
        self._threads.setValue(sm.get("advanced/thread_limit"))

        self._exp = QPushButton("Exportar configuración")
        self._imp = QPushButton("Importar configuración")
        self._exp.clicked.connect(self._export)
        self._imp.clicked.connect(self._import)

        layout.addRow("Debug log:", self._debug)
        layout.addRow("Nivel:", self._level)
        layout.addRow("Hilos:", self._threads)
        layout.addRow(self._exp)
        layout.addRow(self._imp)

    def _export(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Exportar", "astra_config.json", "JSON (*.json)")
        if path:
            sm.export_to_file(path)

    def _import(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Importar", "", "JSON (*.json)")
        if path:
            sm.import_from_file(path)

    def apply(self):
        sm.set_("advanced/debug_log", self._debug.isChecked())
        sm.set_("advanced/log_level", self._level.currentText())
        sm.set_("advanced/thread_limit", self._threads.value())


class _AboutPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        info = QLabel("""
        <h2>Astra Music Player</h2>
        <p>Versión 1.0.0</p>
        <p>Reproductor de música moderno para Linux.</p>
        <br>
        <p><b>Stack:</b> Python 3.11 · PySide6 · GStreamer 1.0</p>
        <p><b>Licencia:</b> MIT</p>
        <p><b>Autor:</b> Cristian</p>
        <br>
        <p><b>Dependencias:</b></p>
        <p>mutagen · numpy · PySide6 · PyGObject (GStreamer)</p>
        """)
        info.setStyleSheet("color: rgba(255,255,255,0.7);")
        info.setWordWrap(True)
        layout.addWidget(info)
        layout.addStretch()


class PreferencesWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preferencias — Astra Music Player")
        self.resize(860, 620)
        self.setModal(True)

        self.setStyleSheet("""
            QDialog { background: rgba(30,30,35,0.97); }
            QWidget { background: transparent; }
            QLabel { color: rgba(255,255,255,0.7); }
            QCheckBox { color: rgba(255,255,255,0.7); }
            QComboBox {
                background: rgba(255,255,255,0.06); color: rgba(255,255,255,0.85);
                border: 1px solid rgba(255,255,255,0.08); border-radius: 6px;
                padding: 4px 8px;
            }
            QLineEdit {
                background: rgba(255,255,255,0.06); color: rgba(255,255,255,0.85);
                border: 1px solid rgba(255,255,255,0.08); border-radius: 6px;
                padding: 4px 8px;
            }
            QPushButton {
                background: rgba(255,255,255,0.06); color: rgba(255,255,255,0.7);
                border: 1px solid rgba(255,255,255,0.08); border-radius: 6px;
                padding: 4px 12px;
            }
            QPushButton:hover { background: rgba(255,255,255,0.12); }
        """)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Sidebar
        self._nav = QListWidget()
        self._nav.setFixedWidth(140)
        self._nav.setStyleSheet("""
            QListWidget {
                background: rgba(20,20,25,200);
                border: none; border-right: 1px solid rgba(255,255,255,0.04);
                padding: 4px;
            }
            QListWidget::item {
                padding: 8px 12px; border-radius: 6px; margin: 1px 4px;
                color: rgba(255,255,255,0.5); font-size: 12px;
            }
            QListWidget::item:selected {
                background: rgba(255,122,0,0.2); color: #FF7A00; font-weight: 600;
            }
        """)
        pages_list = [
            "General", "Interfaz", "Biblioteca", "Reproducción",
            "Audio/DAC", "Ecualizador", "Transmisión", "Servidores",
            "Sincronización", "Radio", "Teclado", "Avanzado", "Acerca de",
        ]
        for i, name in enumerate(pages_list):
            item = QListWidgetItem(name)
            self._nav.addItem(item)
        self._nav.currentRowChanged.connect(self._switch)

        # Pages
        self._stack = QStackedWidget()
        self._stack.setStyleSheet("QStackedWidget{background:transparent;}")
        self._pages = [
            _GeneralPage(), _InterfacePage(), _LibraryPage(), _PlaybackPage(),
            _AudioPage(), _EQPage(), _TransmitPage(), _ServerPage(),
            _SyncPage(), _RadioPage(), _KeyboardPage(), _AdvancedPage(),
            _AboutPage(),
        ]
        for p in self._pages:
            s = _make_scroll(p)
            self._stack.addWidget(s)

        # Right panel
        right = QVBoxLayout()
        right.addWidget(self._stack)

        btns = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel |
            QDialogButtonBox.Apply | QDialogButtonBox.RestoreDefaults)
        btns.accepted.connect(self._on_ok)
        btns.rejected.connect(self.reject)
        btns.button(QDialogButtonBox.Apply).clicked.connect(self._apply_all)
        btns.button(QDialogButtonBox.RestoreDefaults).clicked.connect(self._restore)

        main_layout.addWidget(self._nav)
        main_layout.addLayout(right, 1)

        outer = QVBoxLayout()
        outer.addLayout(main_layout)
        outer.addWidget(btns)
        self.setLayout(outer)

    def _switch(self, idx):
        if idx >= 0:
            self._stack.setCurrentIndex(idx)

    def _apply_all(self):
        for p in self._pages:
            if hasattr(p, 'apply'):
                p.apply()

    def _on_ok(self):
        self._apply_all()
        self.accept()

    def _restore(self):
        sm.restore_defaults()
