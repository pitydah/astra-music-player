import QtQuick
import QtQuick.Controls
import "../../theme"
import "../../components"

Item {
    id: root

    property var libraryBridge: typeof libraryBridge !== "undefined" ? libraryBridge : null

    function refreshData() {
        if (root.libraryBridge && typeof root.libraryBridge.refresh !== "undefined") {
            root.libraryBridge.refresh()
        }
    }

    Component.onCompleted: refreshData()

    Column {
        anchors.fill: parent
        spacing: 0

        Rectangle {
            width: parent.width
            height: 48
            color: Qt.rgba(1.0, 1.0, 1.0, 0.02)

            Row {
                anchors.fill: parent
                anchors.leftMargin: MichiSpacing.xl
                spacing: MichiSpacing.md

                Text {
                    text: "Canciones"
                    color: tabBar.currentIndex === 0 ? MichiColors.accentBlue : MichiColors.textSecondary
                    font.pixelSize: MichiTypography.bodySize
                    font.weight: tabBar.currentIndex === 0 ? MichiTypography.weightSemiBold : MichiTypography.weightNormal
                    anchors.verticalCenter: parent.verticalCenter

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: tabBar.currentIndex = 0
                    }
                }

                Text {
                    text: "Álbumes"
                    color: tabBar.currentIndex === 1 ? MichiColors.accentBlue : MichiColors.textSecondary
                    font.pixelSize: MichiTypography.bodySize
                    font.weight: tabBar.currentIndex === 1 ? MichiTypography.weightSemiBold : MichiTypography.weightNormal
                    anchors.verticalCenter: parent.verticalCenter

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: tabBar.currentIndex = 1
                    }
                }
            }
        }

        SearchField {
            width: parent.width
            anchors.margins: MichiSpacing.md
            placeholderText: "Buscar canciones..."
            onSearchTextChanged: {
                if (root.libraryBridge && typeof root.libraryBridge.search !== "undefined") {
                    root.libraryBridge.search(text)
                }
            }
        }

        StackLayout {
            id: tabBar
            width: parent.width
            height: parent.height - 48 - 38
            currentIndex: 0

            SongTable {
                id: songsView
                songs: root.libraryBridge ? root.libraryBridge.songs : []
                bridge: root.libraryBridge
            }

            AlbumGrid {
                id: albumView
                albums: root.libraryBridge ? root.libraryBridge.albums : []
                bridge: root.libraryBridge
            }
        }
    }
}
