import QtQuick
import "../../theme"
import "../../materials"
import "../../components"

Item {
    id: root

    property string zoneName: ""
    property int receiverCount: 0
    property string zoneStatus: "idle"

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
                spacing: MichiSpacing.xs

                Text {
                    text: root.zoneName
                    color: MichiColors.textPrimary
                    font.pixelSize: MichiTypography.cardTitleSize
                    font.weight: MichiTypography.weightSemiBold
                }

                Text {
                    text: root.receiverCount + " receptor(es)"
                    color: MichiColors.textSecondary
                    font.pixelSize: MichiTypography.metaSize
                }
            }

            StatusBadge {
                anchors.verticalCenter: parent.verticalCenter
                text: root.zoneStatus === "playing" ? "Reproduciendo" : "En espera"
                kind: root.zoneStatus === "playing" ? "active" : "disconnected"
            }
        }
    }
}
