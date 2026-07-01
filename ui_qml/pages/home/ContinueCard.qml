import QtQuick
import QtQuick.Controls
import "../../theme"
import "../../materials"
import "../../components"

Item {
    id: root

    property string trackTitle: "—"
    property string trackArtist: "—"
    property bool hasPlayback: false

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
            onClicked: console.log("[ContinueCard] Continuar reproducción")
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
                    text: "Continuar escuchando"
                    color: MichiColors.textPrimary
                    font.pixelSize: MichiTypography.cardTitleSize
                    font.weight: MichiTypography.weightSemiBold
                }

                Text {
                    text: root.hasPlayback
                        ? (root.trackTitle + " · " + root.trackArtist)
                        : "No hay reproducción activa"
                    color: MichiColors.textSecondary
                    font.pixelSize: MichiTypography.metaSize
                    elide: Text.ElideRight
                    width: parent.width
                }
            }

            ActionButton {
                anchors.verticalCenter: parent.verticalCenter
                text: "Reproducir"
                variant: root.hasPlayback ? "accent" : "secondary"
                enabled: root.hasPlayback
                onClicked: console.log("[ContinueCard] Play")
            }
        }
    }
}
