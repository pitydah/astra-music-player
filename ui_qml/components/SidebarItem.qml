import QtQuick
import QtQuick.Controls
import "../theme"

Item {
    id: root

    property string iconText: ""
    property string label: ""
    property bool active: false
    property bool sidebarHovered: false

    signal clicked()

    implicitHeight: 40
    implicitWidth: 200

    Rectangle {
        anchors.fill: parent
        anchors.leftMargin: MichiSpacing.sm
        anchors.rightMargin: MichiSpacing.sm
        radius: 8
        color: {
            if (root.active) return Qt.rgba(0.561, 0.718, 1.0, 0.12)
            if (root.sidebarHovered) return Qt.rgba(1.0, 1.0, 1.0, 0.04)
            return "transparent"
        }

        Behavior on color {
            ColorAnimation { duration: MichiMotion.fast; easing.type: MichiMotion.easing.standard }
        }

        Rectangle {
            visible: root.active
            width: 3
            height: 20
            anchors.left: parent.left
            anchors.verticalCenter: parent.verticalCenter
            radius: 2
            color: MichiColors.accentBlue
        }

        Row {
            anchors.left: parent.left
            anchors.leftMargin: 16
            anchors.verticalCenter: parent.verticalCenter
            spacing: 12

            Rectangle {
                width: 28
                height: 28
                radius: 6
                color: root.active ? Qt.rgba(0.561, 0.718, 1.0, 0.10) : "transparent"
                anchors.verticalCenter: parent.verticalCenter
                visible: root.iconText !== ""

                Text {
                    anchors.centerIn: parent
                    text: root.iconText
                    color: root.active ? MichiColors.accentBlue : MichiColors.textMuted
                    font.pixelSize: 12
                    font.weight: MichiTypography.weightSemiBold
                    font.letterSpacing: 1.2
                }
            }

            Text {
                text: root.label
                color: root.active ? MichiColors.textPrimary : MichiColors.textSecondary
                font.pixelSize: MichiTypography.bodySize
                font.weight: root.active ? MichiTypography.weightMedium : MichiTypography.weightNormal
                anchors.verticalCenter: parent.verticalCenter
            }
        }

        MouseArea {
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            onEntered: root.sidebarHovered = true
            onExited: root.sidebarHovered = false
            onClicked: root.clicked()
        }
    }
}
