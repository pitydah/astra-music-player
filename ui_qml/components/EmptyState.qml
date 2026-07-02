import QtQuick
import "../theme"

Column {
    id: root

    property string iconText: ""
    property string title: ""
    property string subtitle: ""
    property string actionText: ""
    property bool showAction: false

    signal actionClicked()

    spacing: MichiSpacing.md
    anchors.centerIn: parent ? undefined : undefined

    Text {
        anchors.horizontalCenter: parent.horizontalCenter
        text: root.iconText
        color: MichiColors.textMuted
        font.pixelSize: 36
        visible: root.iconText !== ""
    }

    Text {
        anchors.horizontalCenter: parent.horizontalCenter
        text: root.title
        color: MichiColors.textPrimary
        font.pixelSize: MichiTypography.sectionTitleSize
        font.weight: MichiTypography.weightMedium
        horizontalAlignment: Text.AlignHCenter
        opacity: 0.80
        visible: root.title !== ""
    }

    Text {
        anchors.horizontalCenter: parent.horizontalCenter
        text: root.subtitle
        color: MichiColors.textSecondary
        font.pixelSize: MichiTypography.bodySize
        horizontalAlignment: Text.AlignHCenter
        opacity: 0.56
        width: Math.min(implicitWidth, 400)
        wrapMode: Text.WordWrap
        visible: root.subtitle !== ""
    }

    ActionButton {
        anchors.horizontalCenter: parent.horizontalCenter
        text: root.actionText
        variant: "primary"
        visible: root.showAction && root.actionText !== ""
        onClicked: root.actionClicked()
    }
}
