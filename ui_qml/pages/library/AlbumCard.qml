import QtQuick
import QtQuick.Controls
import "../../theme"
import "../../materials"
import "../../components"

Item {
    id: root

    property string albumTitle: ""
    property string albumArtist: ""
    property int trackCount: 0
    property string coverId: ""

    signal clicked()

    implicitWidth: 180
    implicitHeight: 240

    GlassMaterial {
        anchors.fill: parent
        radius: 12
        hovered: mouseArea.containsMouse
        interactive: true

        MouseArea {
            id: mouseArea
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            onClicked: root.clicked()
        }

        Column {
            anchors.fill: parent
            anchors.margins: MichiSpacing.md
            spacing: MichiSpacing.sm

            Rectangle {
                width: parent.width
                height: width
                radius: 8
                color: Qt.rgba(1.0, 1.0, 1.0, 0.03)

                Image {
                    anchors.fill: parent
                    source: root.coverId ? "image://michi-cover/album/" + root.coverId : "image://michi-cover/fallback/" + (root.albumTitle || "COVER")
                    fillMode: Image.PreserveAspectCrop
                    asynchronous: true
                    sourceSize.width: 512
                    sourceSize.height: 512
                }

                Text {
                    anchors.centerIn: parent
                    text: root.albumTitle ? root.albumTitle.charAt(0).toUpperCase() : "?"
                    color: MichiColors.textMuted
                    font.pixelSize: 36
                    font.weight: MichiTypography.weightBold
                    visible: parent.source === "" || parent.status === Image.Error
                }
            }

            Text {
                text: root.albumTitle
                color: MichiColors.textPrimary
                font.pixelSize: MichiTypography.cardTitleSize
                font.weight: MichiTypography.weightSemiBold
                elide: Text.ElideRight
                width: parent.width
            }

            Text {
                text: root.albumArtist
                color: MichiColors.textSecondary
                font.pixelSize: MichiTypography.metaSize
                elide: Text.ElideRight
                width: parent.width
                visible: root.albumArtist !== ""
            }

            Text {
                text: root.trackCount > 0 ? root.trackCount + " canciones" : ""
                color: MichiColors.textMuted
                font.pixelSize: MichiTypography.metaSize
            }
        }
    }
}
