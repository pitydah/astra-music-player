"""Radio Widget — list of radio stations with playback."""

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
    QListWidgetItem, QPushButton, QLabel, QMenu, QMessageBox,
)

from icons import get_icon
from radio_manager import RadioManager, RadioStation
from radio_dialog import RadioDialog


class RadioWidget(QWidget):
    station_selected = Signal(str, str)  # url, name

    def __init__(self, parent=None):
        super().__init__(parent)
        self._manager = RadioManager()
        self._stations: list[RadioStation] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        toolbar = QHBoxLayout()
        self._add_btn = QPushButton(QIcon(get_icon("add")), " Añadir emisora")
        self._add_btn.clicked.connect(self._add_station)
        self._refresh_btn = QPushButton(QIcon(get_icon("search")), "")
        self._refresh_btn.setToolTip("Recargar lista")
        self._refresh_btn.setFixedSize(30, 30)
        self._refresh_btn.setFlat(True)
        self._refresh_btn.clicked.connect(self._load_stations)
        toolbar.addWidget(self._add_btn)
        toolbar.addStretch()
        toolbar.addWidget(self._refresh_btn)
        layout.addLayout(toolbar)

        self._list = QListWidget()
        self._list.setFrameShape(QListWidget.NoFrame)
        self._list.setStyleSheet("""
            QListWidget {
                background: transparent;
                border: none;
                outline: none;
            }
            QListWidget::item {
                padding: 10px 14px;
                border-bottom: 1px solid rgba(0,0,0,0.04);
            }
            QListWidget::item:hover {
                background: rgba(255,122,0,0.08);
            }
            QListWidget::item:selected {
                background: rgba(255,122,0,0.15);
            }
        """)
        self._list.itemDoubleClicked.connect(self._on_item_double_click)
        self._list.setContextMenuPolicy(Qt.CustomContextMenu)
        self._list.customContextMenuRequested.connect(self._on_context_menu)
        layout.addWidget(self._list)

        self._status = QLabel("")
        self._status.setAlignment(Qt.AlignCenter)
        self._status.setStyleSheet("color: #8e8e93; font-size: 12px; padding: 8px;")
        layout.addWidget(self._status)

        self._load_stations()

    def _load_stations(self):
        self._stations = self._manager.get_all()
        self._list.clear()
        if not self._stations:
            self._status.setText("No hay emisoras. ¡Añade una!")
            self._status.show()
        else:
            self._status.hide()
            for station in self._stations:
                item = QListWidgetItem(f"📻  {station.name}")
                item.setData(Qt.UserRole, station.id)
                self._list.addItem(item)

    def _add_station(self):
        dialog = RadioDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name, url = dialog.get_data()
            if name and url:
                self._manager.add(name, url)
                self._load_stations()
            else:
                QMessageBox.warning(self, "Datos incompletos",
                                    "Por favor, ingresa nombre y URL.")

    def _on_item_double_click(self, item):
        station_id = item.data(Qt.UserRole)
        for station in self._stations:
            if station.id == station_id:
                self.station_selected.emit(station.url, station.name)
                break

    def _on_context_menu(self, pos):
        item = self._list.itemAt(pos)
        if not item:
            return
        station_id = item.data(Qt.UserRole)
        station = next((s for s in self._stations if s.id == station_id), None)
        if not station:
            return

        menu = QMenu(self)
        menu.addAction("Editar", lambda: self._edit_station(station))
        menu.addAction("Eliminar", lambda: self._delete_station(station))
        menu.exec(self._list.viewport().mapToGlobal(pos))

    def _edit_station(self, station: RadioStation):
        dialog = RadioDialog(self, station.name, station.url)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name, url = dialog.get_data()
            if name and url:
                self._manager.update(station.id, name, url)
                self._load_stations()

    def _delete_station(self, station: RadioStation):
        reply = QMessageBox.question(
            self, "Eliminar emisora",
            f"¿Eliminar '{station.name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self._manager.remove(station.id)
            self._load_stations()
