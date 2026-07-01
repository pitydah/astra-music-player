import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
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
                text: "Servidores y conexiones"
                color: MichiColors.textPrimary
                font.pixelSize: MichiTypography.pageTitleSize
                font.weight: MichiTypography.weightSemiBold
            }

            MicroServerHero {
                id: microHero
                width: parent.width
                state: "not_configured"
                onScanClicked: {
                    if (typeof connectionsBridge !== "undefined" && connectionsBridge)
                        connectionsBridge.scanForServers()
                    else
                        console.log("[Connections] Buscar Michi Micro Server")
                }
                onManualAddClicked: {
                    if (typeof connectionsBridge !== "undefined" && connectionsBridge)
                        connectionsBridge.addManualServer()
                    else
                        console.log("[Connections] Agregar servidor manual")
                }
            }

            SectionHeader {
                text: "Servidores externos"
                width: parent.width
            }

            Column {
                width: parent.width
                spacing: MichiSpacing.sm

                ExternalServerCard {
                    width: parent.width
                    serverName: "Navidrome"
                    serverType: "Subsonic API"
                }

                ExternalServerCard {
                    width: parent.width
                    serverName: "Jellyfin"
                    serverType: "Jellyfin API"
                }

                ExternalServerCard {
                    width: parent.width
                    serverName: "Subsonic"
                    serverType: "Subsonic API"
                }

                ExternalServerCard {
                    width: parent.width
                    serverName: "Servidor manual"
                    serverType: "URL personalizada"
                }
            }

            NetworkDiscoveryPanel {
                id: discoveryPanel
                width: parent.width
                discoveredServers: []
                onServerSelected: function(index) {
                    console.log("[Connections] Server selected:", index)
                }
            }

            HomeAudioAccess {
                width: parent.width
                onOpenHomeAudio: {
                    if (typeof navigationBridge !== "undefined" && navigationBridge)
                        navigationBridge.navigate("home_audio")
                    else
                        console.log("[Connections] Abrir Home Audio")
                }
            }
        }
    }
}
