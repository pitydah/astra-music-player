"""NowPlayingBar QSS — centralized styles for the bottom playback bar."""


def button_base_qss(radius: int) -> str:
    return f"""
        QPushButton {{
            background: transparent;
            border: 1px solid transparent;
            outline: none;
            padding: 0px;
            margin: 0px;
            border-radius: {radius}px;
        }}
        QPushButton:focus {{
            outline: none;
            border: none;
        }}
        QPushButton:hover {{
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.055);
        }}
        QPushButton:pressed {{
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.04);
        }}
        QPushButton[role="secondary_transport"]:hover {{
            background: rgba(255,255,255,0.075);
            border: 1px solid rgba(255,255,255,0.065);
        }}
        QPushButton[role="secondary_transport"]:pressed {{
            background: rgba(255,255,255,0.040);
            border: 1px solid rgba(255,255,255,0.040);
        }}
        QPushButton[role="tertiary_transport"]:hover {{
            background: rgba(255,255,255,0.055);
        }}
        QPushButton[role="utility"]:hover {{
            background: rgba(255,255,255,0.050);
            border: 1px solid rgba(255,255,255,0.045);
        }}
        QPushButton[active="true"] {{
            background: rgba(143,183,255,0.14);
            border: 1px solid rgba(143,183,255,0.26);
        }}
        QPushButton[active="true"]:hover {{
            background: rgba(143,183,255,0.20);
            border: 1px solid rgba(143,183,255,0.32);
        }}
        QPushButton#transmitButton[active="true"] {{
            background: rgba(52,199,89,0.130);
            border: 1px solid rgba(52,199,89,0.280);
        }}
        QPushButton#transmitButton[active="true"]:hover {{
            background: rgba(52,199,89,0.180);
            border: 1px solid rgba(52,199,89,0.340);
        }}
        QPushButton:disabled {{
            color: rgba(255,255,255,0.25);
            background: transparent;
            border: 1px solid transparent;
        }}
    """


def info_card_qss() -> str:
    return """
        QWidget#nowPlayingInfoCard {
            background: qlineargradient(
                x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(255,255,255,0.055),
                stop:1 rgba(255,255,255,0.028)
            );
            border: 1px solid rgba(255,255,255,0.055);
            border-radius: 16px;
        }
        QWidget#nowPlayingInfoCard:hover {
            background: qlineargradient(
                x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(255,255,255,0.072),
                stop:1 rgba(255,255,255,0.040)
            );
            border: 1px solid rgba(255,255,255,0.080);
        }
        QWidget#nowPlayingInfoCard[playing="true"] {
            border: 1px solid rgba(143,183,255,0.26);
        }
        QWidget#nowPlayingInfoCard[playing="true"]:hover {
            border: 1px solid rgba(143,183,255,0.34);
        }
    """


def play_button_qss() -> str:
    return """
        QPushButton#playButton {
            background: rgba(255,255,255,0.075);
            border: 1px solid rgba(255,255,255,0.090);
            border-radius: 18px;
        }
        QPushButton#playButton:hover {
            background: rgba(255,255,255,0.120);
            border: 1px solid rgba(255,255,255,0.145);
        }
        QPushButton#playButton:pressed {
            background: rgba(255,255,255,0.055);
            border: 1px solid rgba(255,255,255,0.090);
        }
    """


def title_label_qss() -> str:
    return (
        "QLabel#nowPlayingTitle {"
        "  font-size: 14px; font-weight: 700;"
        "  color: rgba(255,255,255,0.95);"
        "  background: transparent; border: none;"
        "}"
    )


def artist_label_qss() -> str:
    return (
        "QLabel#nowPlayingArtist {"
        "  font-size: 12px; font-weight: 500;"
        "  color: rgba(255,255,255,0.68);"
        "  background: transparent; border: none;"
        "}"
    )


def meta_label_qss() -> str:
    return (
        "QLabel#nowPlayingMeta {"
        "  font-size: 10.5px; font-weight: 500;"
        "  color: rgba(255,255,255,0.54);"
        "  background: transparent; border: none;"
        "}"
    )


def time_label_qss() -> str:
    return (
        "color: rgba(255,255,255,0.86); font-size: 10px; font-weight: 600;"
    )


def bar_qss() -> str:
    return """
        QWidget#nowplayingBar {
            background: rgba(5,6,8,0.92);
            border-radius: 18px;
            border: 1px solid rgba(255,255,255,0.07);
            border-top: 1px solid rgba(255,255,255,0.07);
        }
    """
