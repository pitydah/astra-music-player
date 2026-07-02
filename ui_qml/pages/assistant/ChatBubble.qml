import QtQuick
import QtQuick.Controls
import "../../theme"
import "../../materials"

Item {
    id: root

    property string messageText: ""
    property string role: "assistant"
    property bool hovered: false

    implicitHeight: bubbleColumn.height + MichiSpacing.md * 2
    width: parent ? parent.width : 400

    GlassMaterial {
        radius: 12
        variant: root.role === "user" ? "accent" : "base"
        hovered: root.hovered

        Column {
            id: bubbleColumn
            anchors.fill: parent
            anchors.margins: MichiSpacing.md
            spacing: MichiSpacing.xs

            Text {
                text: root.role === "user" ? "Tú" : "Michi AI"
                color: root.role === "user" ? MichiColors.accentBlue : MichiColors.experimental
                font.pixelSize: MichiTypography.metaSize
                font.weight: MichiTypography.weightSemiBold
            }

            Text {
                text: root.messageText
                color: MichiColors.textPrimary
                font.pixelSize: MichiTypography.bodySize
                wrapMode: Text.WordWrap
                width: parent.width
                lineHeight: 1.4
            }
        }

        MouseArea {
            anchors.fill: parent
            hoverEnabled: true
            onEntered: root.hovered = true
            onExited: root.hovered = false
        }
    }
}
