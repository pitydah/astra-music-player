import QtQuick
import QtQuick.Controls
import "../theme"

Item {
    id: root

    property string variant: "base"
    property bool hovered: false
    property bool interactive: false
    property int radius: 12
    property alias backgroundColor: bgRect.color
    property alias borderColor: bgRect.border.color
    property alias borderWidth: bgRect.border.width

    Item {
        anchors.fill: parent

        Rectangle {
            id: bgRect
            anchors.fill: parent
            radius: root.radius
            color: {
                switch (root.variant) {
                    case "compact": return Qt.rgba(0.05, 0.06, 0.09, 0.85)
                    case "elevated": return MichiColors.surfaceCardElevated
                    case "accent": return Qt.rgba(0.561, 0.718, 1.0, 0.06)
                    case "floating": return Qt.rgba(0.05, 0.06, 0.09, 0.92)
                    case "status": return Qt.rgba(0.05, 0.06, 0.09, 0.75)
                    case "danger": return Qt.rgba(0.95, 0.25, 0.25, 0.08)
                    default: return MichiColors.surfaceCard
                }
            }
            border.color: {
                if (root.hovered && root.interactive) return MichiColors.borderFocus
                switch (root.variant) {
                    case "accent": return Qt.rgba(0.561, 0.718, 1.0, 0.20)
                    case "danger": return Qt.rgba(0.95, 0.25, 0.25, 0.20)
                    case "floating": return Qt.rgba(1.0, 1.0, 1.0, 0.08)
                    default: return MichiColors.borderCard
                }
            }
            border.width: 1

            Rectangle {
                anchors.fill: parent
                radius: parent.radius
                gradient: Gradient {
                    GradientStop { position: 0.0; color: Qt.rgba(1.0, 1.0, 1.0, 0.02) }
                    GradientStop { position: 1.0; color: "transparent" }
                }
            }
        }
    }
}
