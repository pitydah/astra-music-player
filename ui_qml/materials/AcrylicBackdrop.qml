import QtQuick
import "../theme"

Item {
    id: root

    property string textureHint: "dark"

    Rectangle {
        anchors.fill: parent
        color: {
            switch (root.textureHint) {
                case "hero": return Qt.rgba(0.04, 0.05, 0.08, 0.95)
                default: return Qt.rgba(0.03, 0.04, 0.06, 0.98)
            }
        }

        Rectangle {
            anchors.fill: parent
            gradient: Gradient {
                GradientStop { position: 0.0; color: Qt.rgba(0.561, 0.718, 1.0, 0.02) }
                GradientStop { position: 1.0; color: "transparent" }
            }
        }
    }
}
