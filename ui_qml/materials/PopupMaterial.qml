import QtQuick
import "../theme"

Item {
    id: root

    property int radius: 16

    Rectangle {
        anchors.fill: parent
        radius: root.radius
        color: MichiColors.surfacePopup
        border.color: Qt.rgba(0.561, 0.718, 1.0, 0.15)
        border.width: 1
    }
}
