import QtQuick
import "../theme"
import "../materials"

Item {
    id: root

    property string serverName: ""
    property string serverHost: ""
    property string serverType: ""
    property string serverStatus: "disconnected"
    property string ctaText: "Conectar"

    signal ctaClicked()

    GlassMaterial {
        anchors.fill: parent
        variant: "base"
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
            spacing: MichiSpacing.sm

            Row {
                width: parent.width
                spacing: MichiSpacing.sm

                Text {
                    text: root.serverName
                    color: MichiColors.textPrimary
                    font.pixelSize: MichiTypography.cardTitleSize
                    font.weight: MichiTypography.weightSemiBold
                    elide: Text.ElideRight
                    width: parent.width - 100
                }

                StatusBadge {
                    text: {
                        switch (root.serverStatus) {
                            case "connected": return "Conectado"
                            case "detected": return "Detectado"
                            default: return "Desconectado"
                        }
                    }
                    kind: {
                        switch (root.serverStatus) {
                            case "connected": return "success"
                            case "detected": return "info"
                            default: return "disconnected"
                        }
                    }
                }
            }

            Text {
                text: root.serverHost
                color: MichiColors.textMuted
                font.pixelSize: MichiTypography.metaSize
                visible: root.serverHost !== ""
            }

            Text {
                text: root.serverType
                color: MichiColors.textSecondary
                font.pixelSize: MichiTypography.metaSize
                visible: root.serverType !== ""
            }

            ActionButton {
                text: root.ctaText
                variant: "secondary"
                onClicked: root.ctaClicked()
            }
        }
    }
}
