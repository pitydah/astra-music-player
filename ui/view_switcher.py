"""Segmented view switcher — premium capsule control with QButtonGroup."""
from PySide6.QtCore import Signal, Qt, QSize, QPropertyAnimation
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QButtonGroup, QGraphicsOpacityEffect

from ui.design_tokens import VIEW_BUTTON_W, VIEW_BUTTON_H, VIEW_ICON_W, VIEW_ICON_H

VIEW_MODE_DEFS = {
    "list": {
        "icon": "warm_view_list",
        "label": "Lista",
        "short_label": "Lista",
        "tooltip": "Cambiar a vista de lista",
        "active_tooltip": "Vista actual: Lista",
        "description": "Muestra los elementos en una tabla ordenada.",
    },
    "grid": {
        "icon": "warm_view_grid",
        "label": "Mosaico",
        "short_label": "Mosaico",
        "tooltip": "Cambiar a vista de mosaico",
        "active_tooltip": "Vista actual: Mosaico",
        "description": "Muestra tarjetas visuales con carátulas.",
    },
    "coverflow": {
        "icon": "warm_view_coverflow",
        "label": "CoverFlow",
        "short_label": "Cover",
        "tooltip": "Cambiar a CoverFlow de álbumes",
        "active_tooltip": "Vista actual: CoverFlow",
        "description": "Carrusel visual de álbumes.",
    },
    "tree": {
        "icon": "warm_view_tree",
        "label": "Árbol",
        "short_label": "Árbol",
        "tooltip": "Cambiar a vista de árbol",
        "active_tooltip": "Vista actual: Árbol",
        "description": "Explora carpetas y jerarquías.",
    },
    "details": {
        "icon": "warm_view_details",
        "label": "Detalles",
        "short_label": "Detalle",
        "tooltip": "Cambiar a vista de detalles",
        "active_tooltip": "Vista actual: Detalles",
        "description": "Muestra información ampliada.",
    },
}

_QSS = """
    QWidget#segmentedViewSwitcher {
        background: rgba(255,255,255,0.045);
        border: 1px solid rgba(255,255,255,0.090);
        border-radius: 17px;
    }
    QWidget#segmentedViewSwitcher QPushButton {
        background: transparent;
        color: rgba(255,255,255,0.70);
        border: 1px solid transparent;
        border-radius: 14px;
        margin: 2px;
        padding: 0px 10px;
        font-size: 11.5px;
        font-weight: 720;
    }
    QWidget#segmentedViewSwitcher QPushButton:hover {
        background: rgba(255,255,255,0.085);
        color: #FFFFFF;
        border: 1px solid rgba(255,255,255,0.115);
    }
    QWidget#segmentedViewSwitcher QPushButton:checked {
        background: rgba(255,255,255,0.145);
        color: #FFFFFF;
        border: 1px solid rgba(255,255,255,0.185);
    }
    QWidget#segmentedViewSwitcher QPushButton:pressed {
        background: rgba(255,255,255,0.175);
        color: #FFFFFF;
        border: 1px solid rgba(255,255,255,0.220);
    }
    QWidget#segmentedViewSwitcher QPushButton:disabled {
        background: transparent;
        color: rgba(255,255,255,0.25);
        border: 1px solid transparent;
    }
"""


class SegmentedViewSwitcher(QWidget):
    view_changed = Signal(str)

    def __init__(self, get_icon_func, parent=None):
        super().__init__(parent)
        self.setObjectName("segmentedViewSwitcher")
        self.setFixedHeight(40)
        self._available_modes: set[str] = set()
        self._display_mode = "normal"
        self._context = None

        self._group = QButtonGroup(self)
        self._group.setExclusive(True)

        self._buttons: dict[str, QPushButton] = {}
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(0)

        for mode, defs in VIEW_MODE_DEFS.items():
            btn = QPushButton(QIcon(get_icon_func(defs["icon"])), "")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFocusPolicy(Qt.NoFocus)
            btn.setFlat(True)
            btn.setFixedSize(VIEW_BUTTON_W, VIEW_BUTTON_H)
            btn.setMinimumSize(VIEW_BUTTON_W, VIEW_BUTTON_H)
            btn.setMaximumSize(VIEW_BUTTON_W, VIEW_BUTTON_H)
            btn.setIconSize(QSize(VIEW_ICON_W, VIEW_ICON_H))
            btn.setAccessibleName(defs["label"])
            btn.setAccessibleDescription(defs["description"])
            btn.clicked.connect(lambda checked=False, m=mode: self.set_view(m))
            btn.setVisible(False)
            self._group.addButton(btn)
            self._buttons[mode] = btn
            layout.addWidget(btn)

        self._current = "list"
        self._active_anim = None
        self._active_effect_button = None
        self.setStyleSheet(_QSS)
        self.setFixedWidth(0)
        self.hide()
        self._update_tooltips()

    def set_view(self, mode: str, emit: bool = True):
        if mode not in self._buttons:
            return
        if mode not in self._available_modes:
            return
        if self._current == mode:
            return

        self._current = mode

        for m, btn in self._buttons.items():
            btn.setChecked(m == mode)

        self._update_tooltips()

        if emit:
            self.view_changed.emit(mode)
            self._pulse_active_button(self._buttons[mode])

    def _clear_active_effect(self):
        if self._active_anim is not None:
            self._active_anim.stop()
            self._active_anim = None
        if self._active_effect_button is not None:
            self._active_effect_button.setGraphicsEffect(None)
            self._active_effect_button = None

    def _pulse_active_button(self, btn: QPushButton):
        self._clear_active_effect()
        effect = QGraphicsOpacityEffect(btn)
        effect.setOpacity(0.72)
        btn.setGraphicsEffect(effect)
        anim = QPropertyAnimation(effect, b"opacity", self)
        anim.setDuration(120)
        anim.setStartValue(0.72)
        anim.setEndValue(1.0)
        self._active_anim = anim
        self._active_effect_button = btn
        anim.finished.connect(self._clear_active_effect)
        anim.start()

    @property
    def current_view(self) -> str:
        return self._current

    def set_available_modes(self, modes: list[str], default: str | None = None,
                            context: str | None = None):
        self._context = context
        self._available_modes = set(modes or [])

        visible_count = 0
        for mode_name, btn in self._buttons.items():
            vis = mode_name in self._available_modes
            btn.setVisible(vis)
            btn.setEnabled(vis)
            if vis:
                visible_count += 1

        if visible_count <= 1:
            if visible_count == 1:
                only = next((m for m in modes if m in self._available_modes), None)
                if only:
                    self.set_view(only, emit=False)
            self.setFixedWidth(0)
            self.hide()
            return

        self.show()

        if self._current not in self._available_modes:
            target = default if default and default in self._available_modes else modes[0]
            self.set_view(target, emit=False)

        self._update_tooltips()
        self._apply_display_mode()

    def update_for_width(self, window_width: int):
        if window_width < 930:
            self.set_display_mode("compact")
        elif window_width >= 1250:
            self.set_display_mode("expanded")
        else:
            self.set_display_mode("normal")

    def set_display_mode(self, mode: str):
        if mode not in ("compact", "normal", "expanded"):
            mode = "normal"
        if self._display_mode == mode:
            return
        self._display_mode = mode
        self._apply_display_mode()

    def _apply_display_mode(self):
        for mode_name, btn in self._buttons.items():
            if not btn.isVisible():
                continue
            defs = VIEW_MODE_DEFS.get(mode_name, {})

            if self._display_mode == "expanded":
                btn.setText(" " + defs.get("label", ""))
                widths = {"list": 86, "grid": 104, "coverflow": 124,
                          "tree": 88, "details": 108}
                w = widths.get(mode_name, 96)
            elif self._display_mode == "normal":
                btn.setText("")
                w = VIEW_BUTTON_W
            else:  # compact
                btn.setText("")
                w = 42

            btn.setFixedSize(w, VIEW_BUTTON_H)
            btn.setMinimumSize(w, VIEW_BUTTON_H)
            btn.setMaximumSize(w, VIEW_BUTTON_H)

        self._resize_to_content()

    def _resize_to_content(self):
        visible = [b for b in self._buttons.values() if b.isVisible()]
        if len(visible) <= 1:
            self.setFixedWidth(0)
            self.hide()
            return
        total = sum(b.width() for b in visible) + 6
        self.setFixedWidth(total)

    def _update_tooltips(self):
        for mode, btn in self._buttons.items():
            defs = VIEW_MODE_DEFS.get(mode, {})
            if mode == self._current:
                btn.setToolTip(defs.get("active_tooltip", mode))
            else:
                btn.setToolTip(defs.get("tooltip", mode))
