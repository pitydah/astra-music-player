import QtQuick
import "../theme"

Item {
    id: root

    property bool focused: false
    property bool hoveredInput: false
    property int radius: 10

    Rectangle {
        anchors.fill: parent
        radius: root.radius
        color: MichiColors.surfaceInput
        border.color: {
            if (root.focused) return MichiColors.borderFocus
            if (root.hoveredInput) return Qt.rgba(1.0, 1.0, 1.0, 0.12)
            return MichiColors.borderSubtle
        }
        border.width: root.focused ? 2 : 1
    }
}
