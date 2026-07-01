import QtQuick
import "../../theme"
import "../../materials"
import "../../components"

Item {
    id: root

    property string microServerState: "not_configured"
    property bool localServer: false

    signal openConnections()
    signal openHomeAudio()

    implicitHeight: 180

    GlassMaterial {
        anchors.fill: parent
        hovered: mouseArea.containsMouse
        interactive: true
        radius: 12

        MouseArea {
            id: mouseArea
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
        }

        Column {
            anchors.fill: parent
            anchors.margins: MichiSpacing.lg
            spacing: MichiSpacing.md

            Text {
                text: "Ecosistema Michi"
                color: MichiColors.textPrimary
                font.pixelSize: MichiTypography.sectionTitleSize
                font.weight: MichiTypography.weightSemiBold
            }

            Row {
                spacing: MichiSpacing.sm
                StatusBadge {
                    text: {
                        switch (root.microServerState) {
                            case "connected": return "Conectado"
                            case "detected": return "Detectado"
                            default: return "No configurado"
                        }
                    }
                    kind: {
                        switch (root.microServerState) {
                            case "connected": return "success"
                            case "detected": return "info"
                            default: return "disconnected"
                        }
                    }
                }
                StatusBadge { text: "Experimental"; kind: "experimental" }
            }

            Text {
                text: "Michi Micro Server — Servidor musical doméstico del ecosistema Michi"
                color: MichiColors.textSecondary
                font.pixelSize: MichiTypography.bodySize
                width: parent.width
                wrapMode: Text.WordWrap
            }

            Row {
                spacing: MichiSpacing.sm
                ActionButton {
                    text: "Ver servidores"
                    variant: "primary"
                    onClicked: root.openConnections()
                }
                ActionButton {
                    text: "Home Audio"
                    variant: "secondary"
                    onClicked: root.openHomeAudio()
                }
            }
        }
    }
}
