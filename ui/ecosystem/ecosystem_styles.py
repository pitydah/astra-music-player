"""QSS styles for ecosystem UI widgets."""

from __future__ import annotations


def ecosystem_page_qss() -> str:
    return """
    #ecosystemPage {
        background: transparent;
    }
    #ecosystemPage QLabel#pageTitle {
        font-size: 20px;
        font-weight: bold;
        color: rgba(255,255,255,0.92);
    }
    #ecosystemPage QLabel#pageSubtitle {
        font-size: 13px;
        color: rgba(255,255,255,0.55);
    }
    #ecosystemPage QPushButton#actionBtn {
        background: rgba(143,183,255,0.15);
        border: 1px solid rgba(143,183,255,0.28);
        border-radius: 6px;
        color: #8FB7FF;
        padding: 6px 16px;
        font-size: 13px;
    }
    #ecosystemPage QPushButton#actionBtn:hover {
        background: rgba(143,183,255,0.25);
    }
    #ecosystemPage QPushButton#actionBtn:pressed {
        background: rgba(143,183,255,0.35);
    }
    #ecosystemPage QFrame#sectionCard {
        background: rgba(255,255,255,0.045);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px;
    }
    #ecosystemPage QLabel#sectionTitle {
        font-size: 14px;
        font-weight: bold;
        color: rgba(255,255,255,0.88);
    }
    """


def ecosystem_health_panel_qss() -> str:
    return """
    #ecosystemHealthPanel {
        background: rgba(255,255,255,0.035);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px;
    }
    #ecosystemHealthPanel QLabel#healthStatus {
        font-size: 16px;
        font-weight: bold;
    }
    #ecosystemHealthPanel QLabel#healthLabel {
        font-size: 12px;
        color: rgba(255,255,255,0.55);
    }
    #ecosystemHealthPanel QLabel#healthValue {
        font-size: 22px;
        font-weight: bold;
        color: rgba(255,255,255,0.85);
    }
    """


def ecosystem_device_card_qss() -> str:
    return """
    #ecosystemDeviceCard {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px;
        padding: 8px;
    }
    #ecosystemDeviceCard:hover {
        background: rgba(255,255,255,0.075);
        border: 1px solid rgba(143,183,255,0.28);
    }
    #ecosystemDeviceCard QLabel#deviceName {
        font-size: 14px;
        font-weight: bold;
        color: rgba(255,255,255,0.85);
    }
    #ecosystemDeviceCard QLabel#deviceType {
        font-size: 11px;
        color: rgba(255,255,255,0.52);
    }
    #ecosystemDeviceCard QLabel#deviceStatus {
        font-size: 11px;
    }
    """


def ecosystem_issue_card_qss() -> str:
    return """
    #ecosystemIssueCard {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,100,100,0.25);
        border-radius: 8px;
        padding: 8px;
    }
    #ecosystemIssueCard QLabel#issueProblem {
        font-size: 13px;
        font-weight: bold;
        color: rgba(255,140,140,0.9);
    }
    #ecosystemIssueCard QLabel#issueCause {
        font-size: 11px;
        color: rgba(255,255,255,0.55);
    }
    #ecosystemIssueCard QLabel#issueFix {
        font-size: 12px;
        color: rgba(255,255,255,0.75);
    }
    """


def ecosystem_plan_card_qss() -> str:
    return """
    #ecosystemPlanCard {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px;
        padding: 8px;
    }
    #ecosystemPlanCard:hover {
        background: rgba(255,255,255,0.075);
        border: 1px solid rgba(143,183,255,0.28);
    }
    #ecosystemPlanCard QLabel#planTitle {
        font-size: 14px;
        font-weight: bold;
        color: rgba(255,255,255,0.85);
    }
    #ecosystemPlanCard QLabel#planDescription {
        font-size: 12px;
        color: rgba(255,255,255,0.62);
    }
    #ecosystemPlanCard QLabel#planChanges {
        font-size: 11px;
        color: rgba(255,255,255,0.52);
    }
    """
