"""MichiDiscLabPage — CD ripping, encoding, and import interface. STUB."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QComboBox, QTableWidget,
    QHeaderView, QProgressBar,
    QScrollArea, QFileDialog,
)

from ui.audio_lab.models import RIP_PROFILES, EXTRACTION_MODES
from ui.audio_lab.services.external_tools import check_all_tools
from ui.central.central_styles import glass_button_qss


class MichiDiscLabPage(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("michiDiscLabPage")
        self._tools = check_all_tools()
        self._build_ui()
        self._update_diagnostics()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setObjectName("discLabScroll")

        content = QWidget()
        content.setObjectName("discLabContent")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 16, 20, 16)
        content_layout.setSpacing(12)

        title = QLabel("Michi Disc Lab")
        title.setObjectName("discLabTitle")
        content_layout.addWidget(title)

        subtitle = QLabel(
            "Importacion Hi-Fi, ripeo seguro y conversion inteligente "
            "de discos de musica."
        )
        subtitle.setObjectName("discLabSubtitle")
        subtitle.setWordWrap(True)
        content_layout.addWidget(subtitle)

        content_layout.addWidget(self._build_drive_panel())
        content_layout.addWidget(self._build_track_table())
        content_layout.addWidget(self._build_settings_panel())
        content_layout.addWidget(self._build_progress_panel())
        content_layout.addWidget(self._build_diagnostics_panel())
        content_layout.addStretch()

        scroll.setWidget(content)
        layout.addWidget(scroll)

        self._apply_qss()

    def _build_drive_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("discLabDrivePanel")
        p_layout = QVBoxLayout(panel)
        p_layout.setContentsMargins(16, 12, 16, 12)
        p_layout.setSpacing(8)

        self._drive_status = QLabel("Esperando disco de musica...")
        self._drive_status.setObjectName("driveStatus")
        p_layout.addWidget(self._drive_status)

        btn_row = QHBoxLayout()
        self._scan_drive_btn = QPushButton("Buscar unidad optica")
        self._scan_drive_btn.setObjectName("scanDriveBtn")
        self._scan_drive_btn.setCursor(Qt.PointingHandCursor)
        self._scan_drive_btn.clicked.connect(self._on_scan_drive)
        btn_row.addWidget(self._scan_drive_btn)

        self._analyze_disc_btn = QPushButton("Analizar disco")
        self._analyze_disc_btn.setObjectName("analyzeDiscBtn")
        self._analyze_disc_btn.setCursor(Qt.PointingHandCursor)
        self._analyze_disc_btn.setEnabled(False)
        btn_row.addWidget(self._analyze_disc_btn)

        btn_row.addStretch()
        p_layout.addLayout(btn_row)

        return panel

    def _build_track_table(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("discLabTrackPanel")
        p_layout = QVBoxLayout(panel)
        p_layout.setContentsMargins(16, 12, 16, 12)

        self._track_table = QTableWidget()
        self._track_table.setObjectName("discLabTable")
        self._track_table.setColumnCount(5)
        self._track_table.setHorizontalHeaderLabels(
            ["#", "Titulo", "Artista", "Duracion", "Estado"]
        )
        self._track_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._track_table.setSelectionBehavior(QTableWidget.SelectRows)
        p_layout.addWidget(self._track_table)

        return panel

    def _build_settings_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("discLabSettingsPanel")
        p_layout = QHBoxLayout(panel)
        p_layout.setContentsMargins(16, 12, 16, 12)
        p_layout.setSpacing(12)

        profile_label = QLabel("Perfil:")
        profile_label.setStyleSheet("color: rgba(255,255,255,0.62); font-size: 12px;")
        p_layout.addWidget(profile_label)

        self._profile_combo = QComboBox()
        for p in RIP_PROFILES:
            self._profile_combo.addItem(p.name)
        p_layout.addWidget(self._profile_combo)

        mode_label = QLabel("Modo:")
        mode_label.setStyleSheet("color: rgba(255,255,255,0.62); font-size: 12px;")
        p_layout.addWidget(mode_label)

        self._mode_combo = QComboBox()
        for value, text, _desc in EXTRACTION_MODES:
            self._mode_combo.addItem(text, value)
        p_layout.addWidget(self._mode_combo)

        dest_label = QLabel("Destino:")
        dest_label.setStyleSheet("color: rgba(255,255,255,0.62); font-size: 12px;")
        p_layout.addWidget(dest_label)

        self._dest_btn = QPushButton("Seleccionar carpeta...")
        self._dest_btn.setObjectName("destBtn")
        self._dest_btn.setCursor(Qt.PointingHandCursor)
        self._dest_btn.clicked.connect(self._on_select_destination)
        p_layout.addWidget(self._dest_btn)

        p_layout.addStretch()

        self._import_btn = QPushButton("Importar disco")
        self._import_btn.setObjectName("importBtn")
        self._import_btn.setCursor(Qt.PointingHandCursor)
        self._import_btn.setEnabled(False)
        p_layout.addWidget(self._import_btn)

        return panel

    def _build_progress_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("discLabProgressPanel")
        p_layout = QVBoxLayout(panel)
        p_layout.setContentsMargins(16, 8, 16, 12)

        self._progress = QProgressBar()
        self._progress.setObjectName("discLabProgress")
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        self._progress.setVisible(False)
        p_layout.addWidget(self._progress)

        self._progress_label = QLabel("")
        self._progress_label.setObjectName("discLabProgressLabel")
        self._progress_label.setVisible(False)
        p_layout.addWidget(self._progress_label)

        return panel

    def _build_diagnostics_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("discLabDiagPanel")
        p_layout = QVBoxLayout(panel)
        p_layout.setContentsMargins(16, 8, 16, 12)

        diag_title = QLabel("Diagnostico de herramientas externas")
        diag_title.setObjectName("diagTitle")
        p_layout.addWidget(diag_title)

        self._diag_text = QLabel("")
        self._diag_text.setObjectName("diagText")
        self._diag_text.setWordWrap(True)
        p_layout.addWidget(self._diag_text)

        return panel

    def _update_diagnostics(self):
        lines = []
        for name, tool in self._tools.items():
            icon = "+" if tool.available else "-"
            note = ""
            if not tool.available and tool.recommended_for:
                note = f" ({tool.recommended_for} no disponible)"
            lines.append(f"{icon} {name}: {'Disponible' if tool.available else 'No instalado'}{note}")
        self._diag_text.setText("\n".join(lines))

    def _on_scan_drive(self):
        self._drive_status.setText(
            "No se detectaron unidades opticas. "
            "Conecta una unidad de CD/DVD/Blu-ray."
        )
        self._scan_drive_btn.setText("Reintentar")

    def _on_select_destination(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Seleccionar carpeta de destino",
        )
        if folder:
            self._dest_btn.setText(folder)

    def _apply_qss(self):
        self.setStyleSheet("""
            QWidget#michiDiscLabPage {
                background: #090B11;
            }
            QScrollArea#discLabScroll {
                background: transparent;
                border: none;
            }
            QWidget#discLabContent {
                background: transparent;
            }
            QLabel#discLabTitle {
                color: rgba(255,255,255,0.92);
                font-size: 18px;
                font-weight: 700;
            }
            QLabel#discLabSubtitle {
                color: rgba(255,255,255,0.58);
                font-size: 13px;
                margin-bottom: 4px;
            }
            QFrame#discLabDrivePanel, QFrame#discLabTrackPanel,
            QFrame#discLabSettingsPanel, QFrame#discLabProgressPanel,
            QFrame#discLabDiagPanel {
                background: rgba(255,255,255,0.020);
                border: 1px solid rgba(255,255,255,0.04);
                border-radius: 12px;
            }
            QLabel#driveStatus {
                color: rgba(143,183,255,0.70);
                font-size: 14px;
            }
            QTableWidget#discLabTable {
                background: transparent;
                border: none;
                gridline-color: transparent;
                color: rgba(255,255,255,0.78);
            }
            QTableWidget#discLabTable::item {
                padding: 4px 8px;
            }
            QHeaderView::section {
                background: rgba(255,255,255,0.025);
                color: rgba(255,255,255,0.62);
                font-size: 11px;
                font-weight: 600;
                padding: 4px 8px;
                border: none;
            }
            QLabel#diagTitle {
                color: rgba(255,255,255,0.52);
                font-size: 11px;
                font-weight: 600;
            }
            QLabel#diagText {
                color: rgba(255,255,255,0.38);
                font-size: 11px;
            }
            QLabel#discLabProgressLabel {
                color: rgba(255,255,255,0.52);
                font-size: 11px;
            }
            QComboBox {
                background: rgba(255,255,255,0.04);
                border: 1px solid rgba(255,255,255,0.06);
                border-radius: 8px;
                padding: 6px 10px;
                color: rgba(255,255,255,0.78);
                font-size: 12px;
            }
        """)
        for btn_name in ("scanDriveBtn", "analyzeDiscBtn", "destBtn"):
            btn = self.findChild(QPushButton, btn_name)
            if btn:
                btn.setStyleSheet(glass_button_qss("ghost"))
        import_btn = self.findChild(QPushButton, "importBtn")
        if import_btn:
            import_btn.setStyleSheet(glass_button_qss("primary"))
