import QtQuick
import "../theme"

Rectangle {
    id: root

    property string text: ""
    property string kind: "info"
    property bool pulse: false

    implicitHeight: 22
    implicitWidth: text !== "" ? txt.implicitWidth + MichiSpacing.md * 2 : 22
    radius: 11

    color: {
        switch (root.kind) {
            case "success": return Qt.rgba(0.29, 0.87, 0.50, 0.15)
            case "warning": return Qt.rgba(0.98, 0.75, 0.14, 0.15)
            case "error": return Qt.rgba(0.95, 0.25, 0.25, 0.15)
            case "experimental": return Qt.rgba(0.655, 0.545, 0.980, 0.15)
            case "disconnected": return Qt.rgba(0.42, 0.44, 0.50, 0.15)
            case "active": return Qt.rgba(0.29, 0.87, 0.50, 0.20)
            default: return Qt.rgba(0.561, 0.718, 1.0, 0.12)
        }
    }

    border.color: Qt.rgba(1.0, 1.0, 1.0, 0.05)
    border.width: 1

    Text {
        id: txt
        anchors.centerIn: parent
        text: root.text
        color: {
            switch (root.kind) {
                case "success": return MichiColors.success
                case "warning": return MichiColors.warning
                case "error": return MichiColors.error
                case "experimental": return MichiColors.experimental
                case "disconnected": return MichiColors.disconnected
                case "active": return MichiColors.success
                default: return MichiColors.accentBlue
            }
        }
        font.pixelSize: MichiTypography.badgeSize
        font.weight: MichiTypography.weightMedium
        visible: text !== ""
    }
}
