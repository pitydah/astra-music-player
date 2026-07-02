import QtQuick
import QtQuick.Controls
import "../../theme"
import "../../components"
import "."

Item {
    id: root

    Flickable {
        anchors.fill: parent
        anchors.margins: MichiSpacing.xl
        contentHeight: column.height + MichiSpacing.xxl
        clip: true
        boundsBehavior: Flickable.StopAtBounds

        Column {
            id: column
            width: parent.width
            spacing: MichiSpacing.lg

            Text {
                text: "Home Audio"
                color: MichiColors.textPrimary
                font.pixelSize: MichiTypography.pageTitleSize
                font.weight: MichiTypography.weightSemiBold
            }

            HomeAudioModeSelector {
                id: modeSelector
                width: parent.width
            }

            StackLayout {
                width: parent.width
                currentIndex: modeSelector.selectedMode

                HomeAssistantPanel {
                    id: haPanel
                    width: parent.width
                    state: "not_configured"
                    onConfigureClicked: {
                        if (typeof homeAudioBridge !== "undefined" && homeAudioBridge)
                            homeAudioBridge.configureHomeAssistant()
                    }
                    onOpenDiagnostics: {
                        if (typeof homeAudioBridge !== "undefined" && homeAudioBridge)
                            homeAudioBridge.openDiagnostics()
                    }
                }

                MichiMusicStreamPanel {
                    id: streamPanel
                    width: parent.width
                }
            }

            SectionHeader { text: "Dispositivos"; width: parent.width }

            ReceiverCard {
                width: parent.width
                receiverName: "Receptor principal"
                receiverRoom: "Sala de estar"
                receiverState: "disconnected"
                receiverType: "Michi Stream"
            }

            ReceiverCard {
                width: parent.width
                receiverName: "Receptor secundario"
                receiverRoom: "Dormitorio"
                receiverState: "disconnected"
                receiverType: "Michi Stream"
            }

            GlassCard {
                width: parent.width; height: 80
                title: "Diagnóstico de red"
                subtitle: "Mide latencia y calidad de conexión entre dispositivos."
                variant: "base"
            }

            StatusBadge { text: "Experimental — Sin dispositivos conectados"; kind: "experimental" }
        }
    }
}
