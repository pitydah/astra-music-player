import QtQuick
import QtQuick.Controls
import "../../theme"
import "../../components"
import "../../materials"

Item {
    id: root

    property var playlistsBridge: typeof playlistsBridge !== "undefined" ? playlistsBridge : null

    Component.onCompleted: {
        if (root.playlistsBridge && typeof root.playlistsBridge.refresh !== "undefined")
            root.playlistsBridge.refresh()
    }

    Flickable {
        anchors.fill: parent; anchors.margins: MichiSpacing.xl
        contentHeight: column.height + MichiSpacing.xxl
        clip: true; boundsBehavior: Flickable.StopAtBounds

        Column {
            id: column; width: parent.width; spacing: MichiSpacing.lg

            HeroMaterial {
                width: parent.width; height: 140; radius: 16; showGlow: true
                Column {
                    anchors.fill: parent; anchors.margins: MichiSpacing.xl; spacing: MichiSpacing.sm
                    Text {
                        text: "Playlists"; color: MichiColors.textPrimary
                        font.pixelSize: MichiTypography.heroTitleSize; font.weight: MichiTypography.weightBold
                    }
                    Text {
                        text: "Gestiona tus listas de reproducción."; color: MichiColors.textSecondary
                        font.pixelSize: MichiTypography.bodySize; width: parent.width * 0.70; wrapMode: Text.WordWrap
                    }
                }
            }

            Row {
                spacing: MichiSpacing.sm
                ActionButton { text: "+ Nueva playlist"; variant: "primary" }
                ActionButton { text: "Importar M3U"; variant: "secondary" }
            }

            SectionHeader { text: "Tus playlists"; width: parent.width }

            Flow {
                width: parent.width; spacing: MichiSpacing.md

                Repeater {
                    model: root.playlistsBridge ? root.playlistsBridge.playlists : []

                    PlaylistCard {
                        playlistTitle: modelData.title || ""
                        trackCount: modelData.track_count || 0
                        duration: modelData.duration || ""
                        coverKey: modelData.cover_key || ""
                        onClicked: {
                            if (typeof navigationBridge !== "undefined" && navigationBridge)
                                navigationBridge.navigate("playlist_detail")
                        }
                    }
                }
            }

            StatusBadge { text: "Interfaz clásica disponible"; kind: "info" }
        }
    }
}
