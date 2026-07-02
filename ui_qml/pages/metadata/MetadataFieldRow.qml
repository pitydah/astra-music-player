import QtQuick
import QtQuick.Controls
import "../../theme"

Item {
    id: root

    property string fieldLabel: ""
    property string fieldValue: ""

    implicitHeight: 32

    Row {
        anchors.fill: parent
        anchors.leftMargin: MichiSpacing.md
        anchors.rightMargin: MichiSpacing.md
        spacing: MichiSpacing.sm

        Text {
            width: parent.width * 0.30
            text: root.fieldLabel
            color: MichiColors.textMuted
            font.pixelSize: MichiTypography.metaSize
            font.weight: MichiTypography.weightMedium
            anchors.verticalCenter: parent.verticalCenter
            elide: Text.ElideRight
        }

        Text {
            width: parent.width * 0.65
            text: root.fieldValue
            color: MichiColors.textPrimary
            font.pixelSize: MichiTypography.bodySize
            anchors.verticalCenter: parent.verticalCenter
            elide: Text.ElideRight
        }
    }
}
