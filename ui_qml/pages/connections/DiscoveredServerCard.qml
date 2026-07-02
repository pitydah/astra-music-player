import QtQuick
import "../../theme"
import "../../materials"
import "../../components"

Item {
    id: root

    property string serverName: ""
    property string serverHost: ""
    property string serverType: ""
    property string serverStatus: "disconnected"

    signal connectClicked()

    implicitHeight: 100

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

        Row {
            anchors.fill: parent
            anchors.margins: MichiSpacing.lg
            spacing: MichiSpacing.lg

            Column {
                anchors.verticalCenter: parent.verticalCenter
                width: parent.width - 160
                spacing: MichiSpacing.xs

                Text {
                    text: root.serverName
                    color: MichiColors.textPrimary
                    font.pixelSize: MichiTypography.cardTitleSize
                    font.weight: MichiTypography.weightSemiBold
                }

                Text {
                    text: root.serverHost + " · " + root.serverType
                    color: MichiColors.textSecondary
                    font.pixelSize: MichiTypography.metaSize
                    elide: Text.ElideRight
                }
            }

            Row {
                anchors.verticalCenter: parent.verticalCenter
                spacing: MichiSpacing.sm

                StatusBadge {
                    text: root.serverStatus === "connected" ? "Conectado"
                        : root.serverStatus === "detected" ? "Detectado"
                        : "Desconectado"
                    kind: root.serverStatus === "connected" ? "success"
                        : root.serverStatus === "detected" ? "info"
                        : "disconnected"
                }

                ActionButton {
                    text: "Conectar"
                    variant: "accent"
                    onClicked: root.connectClicked()
                }
            }
        }
    }
}
