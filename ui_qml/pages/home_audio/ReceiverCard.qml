import QtQuick
import "../../theme"
import "../../materials"
import "../../components"

Item {
    id: root

    property string receiverName: ""
    property string receiverRoom: ""
    property string receiverState: "disconnected"
    property string receiverType: ""

    signal configureClicked()

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
                    text: root.receiverName
                    color: MichiColors.textPrimary
                    font.pixelSize: MichiTypography.cardTitleSize
                    font.weight: MichiTypography.weightSemiBold
                }

                Text {
                    text: (root.receiverRoom !== "" ? root.receiverRoom + " · " : "") + root.receiverType
                    color: MichiColors.textSecondary
                    font.pixelSize: MichiTypography.metaSize
                    elide: Text.ElideRight
                }
            }

            Row {
                anchors.verticalCenter: parent.verticalCenter
                spacing: MichiSpacing.sm

                StatusBadge {
                    text: root.receiverState === "connected" ? "Activo" : "Inactivo"
                    kind: root.receiverState === "connected" ? "active" : "disconnected"
                }

                ActionButton {
                    text: "Configurar"
                    variant: "ghost"
                    onClicked: root.configureClicked()
                }
            }
        }
    }
}
