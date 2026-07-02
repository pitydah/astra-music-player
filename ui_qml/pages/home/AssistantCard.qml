import QtQuick
import "../../theme"
import "../../materials"
import "../../components"

Item {
    id: root

    signal openAssistant()

    implicitHeight: 100

    GlassMaterial {
        anchors.fill: parent
        hovered: mouseArea.containsMouse
        interactive: true
        radius: 12

        MouseArea {
            id: mouseArea
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            onClicked: root.openAssistant()
        }

        Row {
            anchors.fill: parent
            anchors.margins: MichiSpacing.lg
            spacing: MichiSpacing.lg

            Column {
                anchors.verticalCenter: parent.verticalCenter
                width: parent.width - 140
                spacing: MichiSpacing.xs

                Text {
                    text: "Asistente Michi"
                    color: MichiColors.textPrimary
                    font.pixelSize: MichiTypography.cardTitleSize
                    font.weight: MichiTypography.weightSemiBold
                }

                Text {
                    text: "Pregunta sobre tu música, recibe sugerencias y controla tu biblioteca con IA."
                    color: MichiColors.textSecondary
                    font.pixelSize: MichiTypography.metaSize
                    width: parent.width
                    wrapMode: Text.WordWrap
                    lineHeight: 1.4
                }
            }

            ActionButton {
                anchors.verticalCenter: parent.verticalCenter
                text: "Abrir"
                variant: "ghost"
                onClicked: root.openAssistant()
            }
        }
    }
}
