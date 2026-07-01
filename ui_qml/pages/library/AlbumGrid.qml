import QtQuick
import QtQuick.Controls
import "../../theme"
import "../../components"

Item {
    id: root

    property var albums: []
    property var bridge: null

    GridView {
        anchors.fill: parent
        anchors.margins: MichiSpacing.md
        model: root.albums
        cellWidth: 200
        cellHeight: 260
        clip: true
        boundsBehavior: Flickable.StopAtBounds

        delegate: AlbumCard {
            width: 180
            height: 240
            albumTitle: modelData.album || modelData.album_key || ""
            albumArtist: modelData.artist || ""
            trackCount: modelData.track_count || 0
            coverId: modelData.album_key || modelData.filepath || ""
        }
    }
}
