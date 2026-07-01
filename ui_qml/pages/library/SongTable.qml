import QtQuick
import QtQuick.Controls
import "../../theme"
import "../../components"

Item {
    id: root

    property var songs: []
    property var bridge: null

    signal songSelected(string filepath)
    signal songPlayRequested(string filepath)

    Column {
        anchors.fill: parent
        spacing: 0

        Row {
            width: parent.width
            height: 32
            spacing: MichiSpacing.sm
            Rectangle {
                width: parent.width
                height: parent.height
                color: Qt.rgba(1.0, 1.0, 1.0, 0.02)

                Row {
                    anchors.fill: parent
                    anchors.leftMargin: MichiSpacing.md
                    anchors.rightMargin: MichiSpacing.md
                    spacing: MichiSpacing.sm

                    Text { width: parent.width * 0.30; text: "Título"; color: MichiColors.textMuted; font.pixelSize: MichiTypography.metaSize; font.weight: MichiTypography.weightMedium; anchors.verticalCenter: parent.verticalCenter }
                    Text { width: parent.width * 0.25; text: "Artista"; color: MichiColors.textMuted; font.pixelSize: MichiTypography.metaSize; font.weight: MichiTypography.weightMedium; anchors.verticalCenter: parent.verticalCenter }
                    Text { width: parent.width * 0.25; text: "Álbum"; color: MichiColors.textMuted; font.pixelSize: MichiTypography.metaSize; font.weight: MichiTypography.weightMedium; anchors.verticalCenter: parent.verticalCenter }
                    Text { width: parent.width * 0.12; text: "Duración"; color: MichiColors.textMuted; font.pixelSize: MichiTypography.metaSize; font.weight: MichiTypography.weightMedium; horizontalAlignment: Text.AlignRight; anchors.verticalCenter: parent.verticalCenter }
                }
            }
        }

        ListView {
            width: parent.width
            height: parent.height - 32
            model: root.songs
            clip: true
            boundsBehavior: Flickable.StopAtBounds

            delegate: SongRow {
                width: parent.width
                trackTitle: modelData.title || modelData.filepath || ""
                trackArtist: modelData.artist || ""
                trackAlbum: modelData.album || ""
                trackDuration: modelData.duration ? formatDuration(modelData.duration) : ""
                trackFilepath: modelData.filepath || ""

                onDoubleClicked: {
                    if (modelData.filepath) {
                        root.songPlayRequested(modelData.filepath)
                        if (root.bridge && typeof root.bridge.play_song !== "undefined") {
                            root.bridge.play_song(modelData.filepath)
                        }
                    }
                }
            }

            function formatDuration(secs) {
                var m = Math.floor(secs / 60)
                var s = Math.floor(secs % 60)
                return m + ":" + (s < 10 ? "0" : "") + s
            }
        }
    }
}
