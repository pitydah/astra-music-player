import QtQuick
import "../../theme"
import "../../materials"
import "../../components"

Item {
    id: root

    property int albums: 0
    property int artists: 0
    property int tracks: 0
    property bool hasData: false

    signal openLibrary()

    implicitHeight: 160

    GlassMaterial {
        anchors.fill: parent
        hovered: mouseArea.containsMouse
        interactive: true
        radius: 12

        MouseArea {
            id: mouseArea
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            onClicked: root.openLibrary()
        }

        Column {
            anchors.fill: parent
            anchors.margins: MichiSpacing.lg
            spacing: MichiSpacing.md

            Text {
                text: "Biblioteca"
                color: MichiColors.textPrimary
                font.pixelSize: MichiTypography.sectionTitleSize
                font.weight: MichiTypography.weightSemiBold
            }

            Loader {
                sourceComponent: root.hasData ? statsComponent : emptyComponent
                width: parent.width
            }

            ActionButton {
                text: "Explorar biblioteca"
                variant: "secondary"
                onClicked: root.openLibrary()
            }
        }
    }

    Component {
        id: statsComponent
        Row {
            spacing: MichiSpacing.xl
            Column {
                spacing: MichiSpacing.xs
                Text {
                    text: root.albums
                    color: MichiColors.accentBlue
                    font.pixelSize: MichiTypography.heroTitleSize
                    font.weight: MichiTypography.weightBold
                }
                Text {
                    text: "Álbumes"
                    color: MichiColors.textMuted
                    font.pixelSize: MichiTypography.metaSize
                }
            }
            Column {
                spacing: MichiSpacing.xs
                Text {
                    text: root.artists
                    color: MichiColors.textPrimary
                    font.pixelSize: MichiTypography.heroTitleSize
                    font.weight: MichiTypography.weightBold
                }
                Text {
                    text: "Artistas"
                    color: MichiColors.textMuted
                    font.pixelSize: MichiTypography.metaSize
                }
            }
            Column {
                spacing: MichiSpacing.xs
                Text {
                    text: root.tracks
                    color: MichiColors.textPrimary
                    font.pixelSize: MichiTypography.heroTitleSize
                    font.weight: MichiTypography.weightBold
                }
                Text {
                    text: "Canciones"
                    color: MichiColors.textMuted
                    font.pixelSize: MichiTypography.metaSize
                }
            }
        }
    }

    Component {
        id: emptyComponent
        Text {
            text: "Biblioteca no indexada. Agrega carpetas con música para comenzar."
            color: MichiColors.textMuted
            font.pixelSize: MichiTypography.bodySize
            width: parent.width
            wrapMode: Text.WordWrap
        }
    }
}
