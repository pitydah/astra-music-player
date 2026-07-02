import QtQuick
import "../../theme"
import "../../materials"
import "../../components"

Item {
    id: root

    signal openHomeAudio()

    implicitHeight: 80

    GlassMaterial {
        anchors.fill: parent
        variant: "accent"
        hovered: mouseArea.containsMouse
        interactive: true
        radius: 12

        MouseArea {
            id: mouseArea
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            onClicked: root.openHomeAudio()
        }

        Row {
            anchors.fill: parent
            anchors.margins: MichiSpacing.lg
            spacing: MichiSpacing.lg

            Column {
                anchors.verticalCenter: parent.verticalCenter
                width: parent.width - 120
                spacing: MichiSpacing.xs

                Text {
                    text: "Home Audio"
                    color: MichiColors.textPrimary
                    font.pixelSize: MichiTypography.cardTitleSize
                    font.weight: MichiTypography.weightSemiBold
                }

                Text {
                    text: "Home Assistant y Michi Music Stream en tu hogar"
                    color: MichiColors.textSecondary
                    font.pixelSize: MichiTypography.metaSize
                }
            }

            ActionButton {
                anchors.verticalCenter: parent.verticalCenter
                text: "Abrir"
                variant: "accent"
                onClicked: root.openHomeAudio()
            }
        }
    }
}
