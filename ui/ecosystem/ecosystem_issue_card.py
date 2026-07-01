"""EcosystemIssueCard — displays a single ecosystem issue with problem, cause, and fix."""

from __future__ import annotations

from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

from ui.ecosystem.ecosystem_styles import ecosystem_issue_card_qss


class EcosystemIssueCard(QFrame):
    def __init__(self, issue_id: str, problem: str, cause: str, fix: str, parent=None):
        super().__init__(parent)
        self._issue_id = issue_id
        self.setObjectName("ecosystemIssueCard")
        self.setStyleSheet(ecosystem_issue_card_qss())
        self._build_ui(problem, cause, fix)

    def _build_ui(self, problem: str, cause: str, fix: str):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)

        problem_label = QLabel(problem)
        problem_label.setObjectName("issueProblem")
        problem_label.setWordWrap(True)
        layout.addWidget(problem_label)

        cause_label = QLabel(f"Causa: {cause}")
        cause_label.setObjectName("issueCause")
        cause_label.setWordWrap(True)
        layout.addWidget(cause_label)

        fix_label = QLabel(f"Solucion: {fix}")
        fix_label.setObjectName("issueFix")
        fix_label.setWordWrap(True)
        layout.addWidget(fix_label)
