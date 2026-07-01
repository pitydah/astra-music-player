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
                        onClicked: {
                            if (typeof navigationBridge !== "undefined" && navigationBridge)
                                navigationBridge.navigate("playback")
                        }
                    }

                    ActionButton {
                        text: "Explorar"
                        variant: "ghost"
                        onClicked: {
                            if (typeof navigationBridge !== "undefined" && navigationBridge)
                                navigationBridge.navigate("library")
                        }
                    }
                }
            }

            Item {
                width: parent.width * 0.35
                height: parent.height
                anchors.verticalCenter: parent.verticalCenter

                Rectangle {
                    anchors.centerIn: parent
                    width: 100
                    height: 100
                    radius: 50
                    color: Qt.rgba(0.561, 0.718, 1.0, 0.06)
                    border.color: Qt.rgba(0.561, 0.718, 1.0, 0.12)
                    border.width: 1

                    Text {
                        anchors.centerIn: parent
                        text: "MM"
                        color: MichiColors.accentBlue
                        font.pixelSize: 28
                        font.weight: MichiTypography.weightBold
                        font.letterSpacing: 2.0
                        opacity: 0.50
                    }
                }
            }
        }
    }
}
