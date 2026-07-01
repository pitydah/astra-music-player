import QtQuick
import "../theme"

Item {
    id: root

    property int radius: 0

    Rectangle {
        anchors.fill: parent
        color: "#080A10"

        Rectangle {
            anchors.right: parent.right
            width: 1
            height: parent.height
            color: Qt.rgba(0.561, 0.718, 1.0, 0.03)
        }
    }
}
