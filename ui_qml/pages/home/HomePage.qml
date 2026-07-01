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

            HomeHero {}

            ContinueCard {
                id: continueCard
                width: parent.width
            }

            Row {
                width: parent.width
                spacing: MichiSpacing.lg

                LibraryStatusCard {
                    id: libraryCard
                    width: parent.width * 0.48
                    albums: 0
                    artists: 0
                    tracks: 0
                    onOpenLibrary: console.log("[Home] Abrir biblioteca")
                }

                EcosystemCard {
                    id: ecosystemCard
                    width: parent.width * 0.48
                    microServerState: "not_configured"
                    onOpenConnections: console.log("[Home] Abrir conexiones")
                    onOpenHomeAudio: console.log("[Home] Abrir Home Audio")
                }
            }

            AssistantCard {
                width: parent.width
                onOpenAssistant: console.log("[Home] Abrir asistente")
            }
        }
    }
}
