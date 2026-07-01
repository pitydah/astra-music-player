import QtQuick
import QtQuick.Controls
import "../../theme"
import "../../materials"
import "../../components"

Item {
    id: root

    implicitHeight: 200

    HeroMaterial {
        anchors.fill: parent
        radius: 16
        showGlow: true

        Row {
            anchors.fill: parent
            anchors.margins: MichiSpacing.xl
            spacing: MichiSpacing.xl

            Column {
                width: parent.width * 0.60
                anchors.verticalCenter: parent.verticalCenter
                spacing: MichiSpacing.md

                Text {
                    text: "Centro Michi"
                    color: MichiColors.textPrimary
                    font.pixelSize: MichiTypography.heroTitleSize
                    font.weight: MichiTypography.weightBold
                }

                Text {
                    text: "Tu ecosistema musical. Biblioteca, servidores, Home Audio y asistente en un solo lugar."
                    color: MichiColors.textSecondary
                    font.pixelSize: MichiTypography.bodySize
                    width: parent.width
                    wrapMode: Text.WordWrap
                    lineHeight: 1.5
                }

                Row {
                    spacing: MichiSpacing.sm

                    ActionButton {
                        text: "Continuar escuchando"
                        variant: "primary"
                    }

                    ActionButton {
                        text: "Explorar"
                        variant: "ghost"
                    }
                }
            }

            Item {
                width: parent.width * 0.35
                height: parent.height
                anchors.verticalCenter: parent.verticalCenter

                Rectangle {
                    anchors.centerIn: parent
                    width: 120
                    height: 120
                    radius: 60
                    color: Qt.rgba(0.561, 0.718, 1.0, 0.06)
                    border.color: Qt.rgba(0.561, 0.718, 1.0, 0.12)
                    border.width: 1

                    Text {
                        anchors.centerIn: parent
                        text: "♫"
                        color: MichiColors.accentBlue
                        font.pixelSize: 42
                        opacity: 0.60
                    }
                }
            }
        }
    }
}
