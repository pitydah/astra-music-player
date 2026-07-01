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
                onModeSelected: function(index) {
                    console.log("[HomeAudio] Mode selected:", index)
                }
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
                        else
                            console.log("[HomeAudio] Configurar HA")
                    }
                    onOpenDiagnostics: {
                        if (typeof homeAudioBridge !== "undefined" && homeAudioBridge)
                            homeAudioBridge.openDiagnostics()
                        else
                            console.log("[HomeAudio] Diagnóstico HA")
                    }
                }

                MichiMusicStreamPanel {
                    id: streamPanel
                    width: parent.width
                }
            }
        }
    }
}
