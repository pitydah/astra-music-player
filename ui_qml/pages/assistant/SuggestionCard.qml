import QtQuick
import QtQuick.Controls
import "../../theme"
import "../../materials"
import "../../components"

Item {
    id: root

    property string suggestionTitle: ""
    property string suggestionDescription: ""
    property string actionRoute: ""

    signal actionTriggered()

    implicitHeight: 80
    width: parent ? parent.width : 400

    GlassMaterial {
        anchors.fill: parent
        radius: 10
        hovered: mouseArea.containsMouse
        interactive: true

        MouseArea {
            id: mouseArea
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            onClicked: root.actionTriggered()
        }

        Row {
            anchors.fill: parent
            anchors.margins: MichiSpacing.md
            spacing: MichiSpacing.md

            Column {
                anchors.verticalCenter: parent.verticalCenter
                width: parent.width - 80
                spacing: MichiSpacing.xs

                Text {
                    text: root.suggestionTitle
                    color: MichiColors.textPrimary
                    font.pixelSize: MichiTypography.cardTitleSize
                    font.weight: MichiTypography.weightSemiBold
                    elide: Text.ElideRight
                    width: parent.width
                }

                Text {
                    text: root.suggestionDescription
                    color: MichiColors.textSecondary
                    font.pixelSize: MichiTypography.metaSize
                    wrapMode: Text.WordWrap
                    width: parent.width
                    lineHeight: 1.3
                }
            }

            ActionButton {
                anchors.verticalCenter: parent.verticalCenter
                text: "Abrir"
                variant: "ghost"
                onClicked: root.actionTriggered()
            }
        }
    }
}
