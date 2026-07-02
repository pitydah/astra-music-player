import QtQuick
import "../../theme"
import "../../materials"
import "../../components"

Item {
    id: root

    property string serverName: ""
    property string serverType: ""
    property string badgeText: "Externo"
    property string badgeKind: "info"

    signal configureClicked()

    implicitHeight: 80

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
                width: parent.width - 140
                spacing: MichiSpacing.xs

                Text {
                    text: root.serverName
                    color: MichiColors.textPrimary
                    font.pixelSize: MichiTypography.cardTitleSize
                    font.weight: MichiTypography.weightSemiBold
                }

                Text {
                    text: root.serverType
                    color: MichiColors.textSecondary
                    font.pixelSize: MichiTypography.metaSize
                }
            }

            Row {
                anchors.verticalCenter: parent.verticalCenter
                spacing: MichiSpacing.sm

                StatusBadge { text: root.badgeText; kind: root.badgeKind }

                ActionButton {
                    text: "Configurar"
                    variant: "ghost"
                    onClicked: root.configureClicked()
                }
            }
        }
    }
}
