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
                }
                onManualAddClicked: {
                    if (typeof connectionsBridge !== "undefined" && connectionsBridge)
                        connectionsBridge.addManualServer()
                }
            }

            SectionHeader {
                text: "Servidores externos"
                width: parent.width
            }

            Grid {
                width: parent.width
                columns: 2
                columnSpacing: MichiSpacing.md
                rowSpacing: MichiSpacing.md

                ExternalServerCard {
                    width: (parent.width - MichiSpacing.md) / 2
                    height: 80
                    serverName: "Navidrome"
                    serverType: "Subsonic API"
                }
                ExternalServerCard {
                    width: (parent.width - MichiSpacing.md) / 2
                    height: 80
                    serverName: "Jellyfin"
                    serverType: "Jellyfin API"
                }
                ExternalServerCard {
                    width: (parent.width - MichiSpacing.md) / 2
                    height: 80
                    serverName: "Subsonic"
                    serverType: "Subsonic API"
                }
                ExternalServerCard {
                    width: (parent.width - MichiSpacing.md) / 2
                    height: 80
                    serverName: "Servidor manual"
                    serverType: "URL personalizada"
                }
            }

            NetworkDiscoveryPanel {
                id: discoveryPanel
                width: parent.width
                discoveredServers: []
            }

            HomeAudioAccess {
                width: parent.width
                onOpenHomeAudio: {
                    if (typeof navigationBridge !== "undefined" && navigationBridge)
                        navigationBridge.navigate("home_audio")
                }
            }
        }
    }
}
