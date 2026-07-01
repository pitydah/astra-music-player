import QtQuick
import "../../theme"
import "../../materials"
import "../../components"

Item {
    id: root

    property string serverName: ""
    property string serverHost: ""
    property string serverType: ""
    property string statusText: "Conectado"
    property string statusKind: "success"

    signal disconnectClicked()
    signal configureClicked()

    implicitHeight: 100

    GlassMaterial {
        anchors.fill: parent
        variant: "elevated"
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
                width: parent.width - 200
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

                StatusBadge { text: root.statusText; kind: root.statusKind }

                ActionButton {
                    text: "Configurar"
                    variant: "secondary"
                    onClicked: root.configureClicked()
                }

                ActionButton {
                    text: "Desconectar"
                    variant: "ghost"
                    onClicked: root.disconnectClicked()
                }
            }
        }
    }
}
