import QtQuick
import "../theme"

Item {
    id: root

    property string text: ""
    property bool uppercase: false
    property bool showChevron: false

    implicitHeight: 28
    implicitWidth: parent ? parent.width : 200

    Row {
        anchors.left: parent.left
        anchors.verticalCenter: parent.verticalCenter
        spacing: MichiSpacing.sm

        Text {
            text: root.uppercase ? root.text.toUpperCase() : root.text
            color: MichiColors.textPrimary
            font.pixelSize: MichiTypography.sectionTitleSize
            font.weight: MichiTypography.weightSemiBold
            font.letterSpacing: root.uppercase ? 0.5 : 0.0
        }

        Text {
            text: "›"
            color: MichiColors.textMuted
            font.pixelSize: MichiTypography.sectionTitleSize
            visible: root.showChevron
            anchors.verticalCenter: parent.verticalCenter
        }
    }
}
