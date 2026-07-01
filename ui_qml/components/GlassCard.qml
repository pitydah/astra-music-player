import QtQuick
import QtQuick.Controls
import "../theme"
import "../materials"

Item {
    id: root

    property string title: ""
    property string subtitle: ""
    property string iconName: ""
    property string variant: "base"
    property bool hovered: false
    property alias cardRadius: glass.radius

    signal clicked()

    GlassMaterial {
        id: glass
        anchors.fill: parent
        variant: root.variant
        hovered: root.hovered
        interactive: true
        radius: 12

        MouseArea {
            anchors.fill: parent
            hoverEnabled: true
            onEntered: root.hovered = true
            onExited: root.hovered = false
            onClicked: root.clicked()
        }

        Column {
            anchors.fill: parent
            anchors.margins: MichiSpacing.lg
            spacing: MichiSpacing.xs

            Text {
                text: root.title
                color: MichiColors.textPrimary
                font.pixelSize: MichiTypography.cardTitleSize
                font.weight: MichiTypography.weightSemiBold
                elide: Text.ElideRight
                width: parent.width
                visible: text !== ""
            }

            Text {
                text: root.subtitle
                color: MichiColors.textSecondary
                font.pixelSize: MichiTypography.bodySize
                elide: Text.ElideRight
                width: parent.width
                visible: text !== ""
            }
        }
    }
}
