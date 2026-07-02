import QtQuick
import QtQuick.Controls
import "../../theme"
import "../../materials"
import "../../components"

Item {
    id: root

    property string deviceAlias: ""
    property string deviceType: "desktop"
    property string deviceIp: ""
    property int devicePort: 0
    property bool paired: false

    signal connectClicked()

    implicitHeight: 80

    GlassMaterial {
        anchors.fill: parent
        radius: 10
        hovered: mouseArea.containsMouse
        interactive: true

        MouseArea {
            id: mouseArea
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
        }

        Row {
            anchors.fill: parent
            anchors.margins: MichiSpacing.md
            spacing: MichiSpacing.md

            Rectangle {
                width: 40; height: 40; radius: 8; anchors.verticalCenter: parent.verticalCenter
                color: root.paired ? Qt.rgba(0.29, 0.87, 0.50, 0.12) : Qt.rgba(0.561, 0.718, 1.0, 0.08)
                Text {
                    anchors.centerIn: parent
                    text: root.deviceAlias ? root.deviceAlias.charAt(0).toUpperCase() : "?"
                    color: root.paired ? MichiColors.success : MichiColors.accentBlue
                    font.pixelSize: 18; font.weight: MichiTypography.weightBold
                }
            }

            Column {
                anchors.verticalCenter: parent.verticalCenter
                spacing: 4; width: parent.width - 120
                Text {
                    text: root.deviceAlias || "Dispositivo"
                    color: MichiColors.textPrimary; font.pixelSize: MichiTypography.bodySize
                    font.weight: MichiTypography.weightMedium; elide: Text.ElideRight; width: parent.width
                }
                Text {
                    text: root.deviceIp ? root.deviceIp + ":" + root.devicePort : root.deviceType
                    color: MichiColors.textMuted; font.pixelSize: MichiTypography.metaSize; elide: Text.ElideRight; width: parent.width
                }
            }

            StatusBadge {
                anchors.verticalCenter: parent.verticalCenter
                text: root.paired ? "Vinculado" : "Detectado"
                kind: root.paired ? "success" : "info"
            }
        }
    }
}
