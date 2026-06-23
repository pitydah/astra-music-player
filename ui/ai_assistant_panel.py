"""AI Assistant chat panel — glass dark themed, with Fase 2 action confirmations."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QLineEdit, QPushButton, QLabel, QFrame, QSizePolicy,
)


_PRIVACY_NOTICE = (
    "El asistente usa IA local (Ollama). "
    "No se envian rutas ni biblioteca completa al modelo."
)

_PLACEHOLDER = "Pregunta algo sobre tu biblioteca musical..."


class AiAssistantPanel(QWidget):
    send_requested = Signal(str)
    action_confirmed = Signal(str)
    action_cancelled = Signal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("aiAssistantPanel")
        self._messages: list[dict[str, str]] = []
        self._build_ui()
        self._apply_qss()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll.setObjectName("assistantChatScroll")

        self._chat_container = QWidget()
        self._chat_container.setObjectName("assistantChatContainer")
        self._chat_layout = QVBoxLayout(self._chat_container)
        self._chat_layout.setContentsMargins(16, 12, 16, 12)
        self._chat_layout.setSpacing(10)
        self._chat_layout.addStretch()

        self._scroll.setWidget(self._chat_container)
        layout.addWidget(self._scroll, 1)

        self._privacy_badge = QLabel(_PRIVACY_NOTICE)
        self._privacy_badge.setObjectName("assistantPrivacyBadge")
        self._privacy_badge.setWordWrap(True)
        self._privacy_badge.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._privacy_badge)

        input_row = QHBoxLayout()
        input_row.setContentsMargins(12, 8, 12, 12)
        input_row.setSpacing(8)

        self._input = QLineEdit()
        self._input.setObjectName("assistantInput")
        self._input.setPlaceholderText(_PLACEHOLDER)
        self._input.returnPressed.connect(self._on_send)
        input_row.addWidget(self._input, 1)

        self._send_btn = QPushButton("Enviar")
        self._send_btn.setObjectName("assistantSendBtn")
        self._send_btn.setCursor(Qt.PointingHandCursor)
        self._send_btn.clicked.connect(self._on_send)
        input_row.addWidget(self._send_btn)

        layout.addLayout(input_row)

    @staticmethod
    def _build_panel_qss() -> str:
        return (
            "QWidget#aiAssistantPanel {"
            "  background: #090B11;"
            "}"
            "QScrollArea#assistantChatScroll {"
            "  background: transparent;"
            "  border: none;"
            "}"
            "QWidget#assistantChatContainer {"
            "  background: transparent;"
            "}"
            "QLabel#assistantPrivacyBadge {"
            "  color: rgba(255,255,255,0.42);"
            "  font-size: 10px;"
            "  padding: 6px 16px;"
            "  background: rgba(143,183,255,0.04);"
            "  border-top: 1px solid rgba(255,255,255,0.03);"
            "}"
            "QLineEdit#assistantInput {"
            "  background: rgba(255,255,255,0.035);"
            "  border: 1px solid rgba(255,255,255,0.06);"
            "  border-radius: 12px;"
            "  padding: 10px 14px;"
            "  color: rgba(255,255,255,0.92);"
            "  font-size: 13px;"
            "}"
            "QLineEdit#assistantInput:focus {"
            "  border: 1px solid rgba(143,183,255,0.18);"
            "  background: rgba(255,255,255,0.048);"
            "}"
            "QPushButton#assistantSendBtn {"
            "  background: rgba(143,183,255,0.12);"
            "  border: 1px solid rgba(143,183,255,0.14);"
            "  border-radius: 12px;"
            "  padding: 10px 20px;"
            "  color: rgba(255,255,255,0.92);"
            "  font-size: 13px;"
            "  font-weight: 600;"
            "}"
            "QPushButton#assistantSendBtn:hover {"
            "  background: rgba(143,183,255,0.20);"
            "  border: 1px solid rgba(143,183,255,0.22);"
            "}"
            "QPushButton#assistantSendBtn:pressed {"
            "  background: rgba(143,183,255,0.08);"
            "}"
        )

    def _apply_qss(self):
        self.setStyleSheet(self._build_panel_qss())

    def _on_send(self):
        text = self._input.text().strip()
        if not text:
            return
        self._input.clear()
        self.add_message("user", text)
        self.send_requested.emit(text)

    def add_message(self, role: str, content: str, pending: dict | None = None):
        bubble = _ChatBubble(role, content, self._chat_container)
        idx = self._chat_layout.count() - 1
        self._chat_layout.insertWidget(max(0, idx), bubble)
        if pending:
            card = _PendingActionCard(pending, self._chat_container)
            card.confirmed.connect(self.action_confirmed.emit)
            card.cancelled.connect(self.action_cancelled.emit)
            self._chat_layout.insertWidget(self._chat_layout.count() - 1, card)
        self._scroll_to_bottom()

    def add_message_r(self, content: str):
        """Convenience slot for response_received signal — adds as 'assistant'."""
        self.add_message("assistant", content)

    def add_response(self, response: dict):
        """Handle structured response from service: {reply, pending}."""
        reply = response.get("reply", "")
        if reply:
            self.add_message("assistant", reply)
        pending = response.get("pending")
        if pending:
            card = _PendingActionCard(pending, self._chat_container)
            card.confirmed.connect(
                lambda aid=pending.get("action_id", ""): self.action_confirmed.emit(aid)
            )
            card.cancelled.connect(
                lambda aid=pending.get("action_id", ""): self.action_cancelled.emit(aid)
            )
            self._chat_layout.insertWidget(self._chat_layout.count() - 1, card)
            self._scroll_to_bottom()

    def set_thinking(self, thinking: bool):
        if thinking:
            self._send_btn.setEnabled(False)
            self._input.setEnabled(False)
            self._send_btn.setText("Pensando...")
        else:
            self._send_btn.setEnabled(True)
            self._input.setEnabled(True)
            self._send_btn.setText("Enviar")
            self._input.setFocus()

    def set_ollama_status(self, available: bool, model: str = ""):
        if available:
            self._privacy_badge.setText(
                f"{_PRIVACY_NOTICE} — {model} conectado"
            )
        else:
            self._privacy_badge.setText(
                f"{_PRIVACY_NOTICE} — Ollama no disponible"
            )

    def clear_messages(self):
        while self._chat_layout.count() > 1:
            item = self._chat_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()
        self._messages.clear()

    def _scroll_to_bottom(self):
        sb = self._scroll.verticalScrollBar()
        sb.setValue(sb.maximum())


class _ChatBubble(QFrame):
    def __init__(self, role: str, content: str, parent: QWidget):
        super().__init__(parent)
        self.setObjectName(f"chatBubble_{role}")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel(content)
        label.setWordWrap(True)
        label.setTextFormat(Qt.PlainText)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        if role == "user":
            label.setObjectName("bubbleUser")
            label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            layout.addWidget(label)
            layout.setAlignment(Qt.AlignRight)
        else:
            label.setObjectName("bubbleAssistant")
            label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            layout.addWidget(label)
            layout.setAlignment(Qt.AlignLeft)

        label.setStyleSheet(
            "QLabel#bubbleUser {"
            "  background: rgba(143,183,255,0.10);"
            "  border: 1px solid rgba(143,183,255,0.12);"
            "  border-radius: 14px;"
            "  padding: 10px 16px;"
            "  color: rgba(255,255,255,0.90);"
            "  font-size: 13px;"
            "  max-width: 520px;"
            "}"
            "QLabel#bubbleAssistant {"
            "  background: rgba(255,255,255,0.030);"
            "  border: 1px solid rgba(255,255,255,0.04);"
            "  border-radius: 14px;"
            "  padding: 10px 16px;"
            "  color: rgba(255,255,255,0.84);"
            "  font-size: 13px;"
            "  max-width: 620px;"
            "}"
        )


class _PendingActionCard(QFrame):
    confirmed = Signal(str)
    cancelled = Signal(str)

    def __init__(self, pending: dict, parent: QWidget):
        super().__init__(parent)
        self.setObjectName("pendingActionCard")
        self._action_id = pending.get("action_id", "")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        title = QLabel(pending.get("title", "Accion pendiente"))
        title.setObjectName("pendingTitle")
        title.setStyleSheet(
            "QLabel#pendingTitle {"
            "  color: rgba(255,255,255,0.92);"
            "  font-size: 14px;"
            "  font-weight: 600;"
            "}"
        )
        layout.addWidget(title)

        desc = pending.get("description", "")
        if desc:
            desc_label = QLabel(desc)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet(
                "QLabel {"
                "  color: rgba(255,255,255,0.62);"
                "  font-size: 12px;"
                "}"
            )
            layout.addWidget(desc_label)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        confirm_btn = QPushButton("Confirmar")
        confirm_btn.setObjectName("pendingConfirmBtn")
        confirm_btn.setCursor(Qt.PointingHandCursor)
        confirm_btn.clicked.connect(lambda: self.confirmed.emit(self._action_id))
        btn_row.addWidget(confirm_btn)

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setObjectName("pendingCancelBtn")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(lambda: self.cancelled.emit(self._action_id))
        btn_row.addWidget(cancel_btn)

        layout.addLayout(btn_row)

        self.setStyleSheet(
            "QFrame#pendingActionCard {"
            "  background: rgba(143,183,255,0.04);"
            "  border: 1px solid rgba(143,183,255,0.10);"
            "  border-radius: 14px;"
            "}"
            "QPushButton#pendingConfirmBtn {"
            "  background: rgba(143,183,255,0.14);"
            "  border: 1px solid rgba(143,183,255,0.16);"
            "  border-radius: 10px;"
            "  padding: 8px 18px;"
            "  color: rgba(255,255,255,0.94);"
            "  font-size: 12px;"
            "  font-weight: 600;"
            "}"
            "QPushButton#pendingConfirmBtn:hover {"
            "  background: rgba(143,183,255,0.22);"
            "}"
            "QPushButton#pendingCancelBtn {"
            "  background: rgba(255,255,255,0.03);"
            "  border: 1px solid rgba(255,255,255,0.05);"
            "  border-radius: 10px;"
            "  padding: 8px 18px;"
            "  color: rgba(255,255,255,0.58);"
            "  font-size: 12px;"
            "  font-weight: 500;"
            "}"
            "QPushButton#pendingCancelBtn:hover {"
            "  background: rgba(255,255,255,0.06);"
            "  color: rgba(255,255,255,0.78);"
            "}"
        )
