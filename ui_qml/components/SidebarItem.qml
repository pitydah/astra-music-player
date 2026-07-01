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

            Text {
                text: root.iconText
                color: root.active ? MichiColors.accentBlue : MichiColors.textSecondary
                font.pixelSize: 16
                anchors.verticalCenter: parent.verticalCenter
                visible: root.iconText !== ""
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
