import QtQuick
import QtQuick.Controls
import "../theme"
import "../materials"

Rectangle {
    id: root

    property string text: ""
    property string variant: "primary"
    property bool pressed: false
    property bool hoveredBtn: false

    signal clicked()

    width: text !== "" ? implicitWidth + MichiSpacing.xl * 2 : 40
    height: 36
    radius: 10
    color: {
        if (!enabled) return Qt.rgba(0.3, 0.3, 0.35, 0.15)
        switch (root.variant) {
            case "primary":
                return root.pressed ? Qt.rgba(0.5, 0.65, 1.0, 1.0)
                    : root.hoveredBtn ? Qt.rgba(0.65, 0.78, 1.0, 1.0)
                    : MichiColors.accentBlue
            case "secondary":
                return root.pressed ? Qt.rgba(1.0, 1.0, 1.0, 0.15)
                    : root.hoveredBtn ? Qt.rgba(1.0, 1.0, 1.0, 0.10)
                    : Qt.rgba(1.0, 1.0, 1.0, 0.06)
            case "ghost":
                return "transparent"
            case "accent":
                return root.pressed ? Qt.rgba(0.561, 0.718, 1.0, 0.18)
                    : root.hoveredBtn ? Qt.rgba(0.561, 0.718, 1.0, 0.12)
                    : Qt.rgba(0.561, 0.718, 1.0, 0.08)
            case "danger":
                return root.pressed ? Qt.rgba(0.95, 0.25, 0.25, 0.20)
                    : root.hoveredBtn ? Qt.rgba(0.95, 0.25, 0.25, 0.12)
                    : Qt.rgba(0.95, 0.25, 0.25, 0.08)
            default:
                return MichiColors.accentBlue
        }
    }

    border.color: root.variant === "ghost" ? (root.hoveredBtn ? Qt.rgba(1.0, 1.0, 1.0, 0.12) : "transparent") : "transparent"
    border.width: 1

    Text {
        anchors.centerIn: parent
        text: root.text
        color: {
            if (!enabled) return MichiColors.textMuted
            switch (root.variant) {
                case "primary": return "#070A10"
                default: return MichiColors.textPrimary
            }
        }
        font.pixelSize: MichiTypography.bodySize
        font.weight: MichiTypography.weightMedium
        visible: text !== ""
    }

    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onEntered: root.hoveredBtn = true
        onExited: root.hoveredBtn = false
        onPressed: root.pressed = true
        onReleased: root.pressed = false
        onClicked: root.clicked()
    }
}
