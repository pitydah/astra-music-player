"""Transmit controller — streaming, snapcast, audio output management."""
import os

from PySide6.QtWidgets import (
    QMenu, QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QPushButton, QListWidget, QListWidgetItem,
    QMessageBox, QDialogButtonBox,
)


class TransmitController:
    def __init__(self, window):
        self._win = window

    def show_transmit_menu(self):
        from ui.premium_menus import premium_menu_qss
        menu = QMenu(self._win)
        menu.setStyleSheet(premium_menu_qss())

        local = menu.addAction("Salida local")
        local.setCheckable(True)
        active = self._win._ctx.transmit_mgr.get_active()
        local.setChecked(active is None)
        local.triggered.connect(lambda: self.activate_transmit_device(None))

        devices = self._win._ctx.transmit_mgr.get_devices()
        if devices:
            menu.addSeparator()
            for dev in devices:
                label = f"{dev.name} · {dev.stype.upper()}"
                action = menu.addAction(label)
                action.setCheckable(True)
                action.setChecked(active is not None and active.name == dev.name)
                action.triggered.connect(
                    lambda checked=False, d=dev: self.activate_transmit_device(d))
        else:
            menu.addSeparator()
            empty = menu.addAction("No hay dispositivos configurados")
            empty.setEnabled(False)

        menu.addSeparator()
        menu.addAction("Añadir dispositivo…", self.add_transmit_device)
        menu.addAction("Administrar dispositivos…", self.manage_transmit_devices)

        btn = self._win._ctx.player_bar.transmit_button()
        menu.exec(btn.mapToGlobal(btn.rect().bottomLeft()))

    def activate_transmit_device(self, device):
        if device is None:
            self._win._ctx.transmit_mgr.set_active(None)
            self._win._ctx.playback.set_output_device(None)
            self._win._ctx.player_bar.set_transmit_active(False)
        else:
            self._win._ctx.transmit_mgr.set_active(device)
            self._win._ctx.playback.set_output_device(device)
            self._win._ctx.player_bar.set_transmit_active(True, device.name)

    def on_transmit_devices_changed(self):
        pass

    def on_transmit_active_changed(self):
        device = self._win._ctx.transmit_mgr.get_active()
        if device:
            self._win._ctx.player_bar.set_transmit_active(True, device.name)
        else:
            self._win._ctx.player_bar.set_transmit_active(False)

    def show_audio_output_menu(self):
        from ui.premium_menus import premium_menu_qss
        menu = QMenu(self._win)
        menu.setStyleSheet(premium_menu_qss())

        action_system = menu.addAction("Predeterminada del sistema")
        action_system.setCheckable(True)
        action_system.setChecked(True)
        action_system.triggered.connect(
            lambda: self._win._ctx.playback.set_output_device(None))

        menu.addSeparator()

        try:
            import gi
            gi.require_version("Gst", "1.0")
            from gi.repository import Gst
            monitor = Gst.DeviceMonitor()
            monitor.add_filter("Audio/Sink", None)
            monitor.start()
            devices = monitor.get_devices()
            monitor.stop()
            if devices:
                for dev in devices:
                    name = dev.get_display_name() or dev.get_device_class() or "Audio device"
                    action = menu.addAction(name)
                    action.setCheckable(True)
                    action.triggered.connect(
                        lambda checked=False, d=dev: self._win._ctx.playback.set_output_device(d))
        except Exception:
            import logging
            logging.getLogger("astra").debug("Audio device detection failed")

        menu.addSeparator()
        menu.addAction("PipeWire (sistema)", lambda: self._win._ctx.playback.set_output_device(None))
        menu.addAction("Actualizar dispositivos", self.show_audio_output_menu)
        menu.addAction("Preferencias de audio…", self._win._show_preferences)

        btn = self._win._ctx.player_bar.audio_output_button()
        menu.exec(btn.mapToGlobal(btn.rect().bottomLeft()))

    def open_mini_player(self):
        from ui.mini_player import MiniPlayer
        from audio.player import PlaybackState
        from library.cover_art_service import CoverArtService

        if not hasattr(self._win, '_mini_player'):
            self._win._ctx.mini_player = MiniPlayer(self._win._ctx.playback, self._win)
            self._win._ctx.mini_player.play_clicked.connect(self._win._ctx.playback.toggle)
            self._win._ctx.mini_player.prev_clicked.connect(self._win._ctx.playback.play_prev)
            self._win._ctx.mini_player.next_clicked.connect(self._win._ctx.playback.play_next)
            self._win._ctx.mini_player.seek_requested.connect(self._win._ctx.playback.seek)
            self._win._ctx.player.position_changed.connect(
                lambda s: self._win._ctx.mini_player.set_position(
                    s, getattr(self._win._ctx.player, '_duration', 0)))
            self._win._ctx.player.state_changed.connect(
                lambda s: self._win._ctx.mini_player.set_state(
                    "playing" if s == PlaybackState.PLAYING else
                    "paused" if s == PlaybackState.PAUSED else "stopped"))

        current = self._win._ctx.playback.current
        name = os.path.basename(current) if current else ""
        artist = ""
        if current:
            qual, _ = CoverArtService.quality_label(current)
            item = self._win._ctx.items_index.get(current)
            if item:
                artist = item.artist or qual or ""
                title = item.title or name
            else:
                title = name
        else:
            title = "Sin reproducción"
        self._win._ctx.mini_player.set_track(title, artist)
        self._win._ctx.mini_player.show()
        self._win._ctx.mini_player.raise_()
        self._win._ctx.mini_player.activateWindow()

    def add_transmit_device(self):
        from ui.theme import apply_dialog_shadow

        dlg = QDialog(self._win)
        dlg.setWindowTitle("Añadir dispositivo")
        dlg.setMinimumWidth(380)
        apply_dialog_shadow(dlg)

        layout = QFormLayout(dlg)
        name = QLineEdit()
        name.setPlaceholderText("ej: Altavoz Salón")
        stype = QComboBox()
        stype.addItem("HTTP Stream (servidor TCP)", "http")
        stype.addItem("Snapcast", "snapcast")
        addr = QLineEdit()
        addr.setPlaceholderText("192.168.1.10")
        port = QLineEdit()
        port.setPlaceholderText("8554")

        layout.addRow("Nombre:", name)
        layout.addRow("Tipo:", stype)
        layout.addRow("IP / URL:", addr)
        layout.addRow("Puerto:", port)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(dlg.accept)
        btns.rejected.connect(dlg.reject)
        layout.addRow(btns)

        if dlg.exec() == QDialog.DialogCode.Accepted and name.text().strip():
            try:
                port_val = int(port.text()) if port.text().strip() else 0
            except ValueError:
                port_val = 0
            self._win._ctx.transmit_mgr.add_device(
                name.text().strip(), stype.currentData(),
                addr.text().strip(), port_val)

    def manage_transmit_devices(self):
        from ui.theme import apply_dialog_shadow

        devices = self._win._ctx.transmit_mgr.get_devices()
        if not devices:
            QMessageBox.information(self._win, "Dispositivos",
                                    "No hay dispositivos configurados.")
            return

        dlg = QDialog(self._win)
        dlg.setWindowTitle("Administrar dispositivos")
        dlg.setMinimumWidth(400)
        apply_dialog_shadow(dlg)

        layout = QVBoxLayout(dlg)
        lst = QListWidget()
        for dev in devices:
            item = QListWidgetItem(
                f"{dev.name}  ·  {dev.stype.upper()}  ·  "
                f"{dev.address}:{dev.port or '-'}")
            lst.addItem(item)
        layout.addWidget(lst)

        btn_row = QHBoxLayout()

        def _do_delete():
            sel = lst.currentItem()
            if sel:
                dname = sel.text().split("  ·  ")[0]
                self._win._ctx.transmit_mgr.remove_device(dname)
                dlg.accept()
                self.manage_transmit_devices()

        def _do_activate():
            sel = lst.currentItem()
            if sel:
                dname = sel.text().split("  ·  ")[0]
                dev = next((d for d in self._win._ctx.transmit_mgr.get_devices()
                           if d.name == dname), None)
                if dev:
                    self.activate_transmit_device(dev)
                    dlg.accept()

        del_btn = QPushButton("Eliminar")
        del_btn.clicked.connect(_do_delete)
        act_btn = QPushButton("Activar")
        act_btn.clicked.connect(_do_activate)
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(dlg.accept)

        btn_row.addWidget(act_btn)
        btn_row.addWidget(del_btn)
        btn_row.addStretch()
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)
        dlg.exec()
