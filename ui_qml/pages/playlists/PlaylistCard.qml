import QtQuick
import QtQuick.Controls
import MichiCover 1.0
import "../../theme"
import "../../materials"
import "../../components"

Item {
    id: root

    property string playlistTitle: ""
    property int trackCount: 0
    property string duration: ""
    property string coverKey: ""

    signal clicked()

    implicitWidth: 200; implicitHeight: 240

    GlassMaterial {
        anchors.fill: parent; radius: 12
        hovered: mouseArea.containsMouse; interactive: true
        MouseArea {
            id: mouseArea; anchors.fill: parent
            hoverEnabled: true; cursorShape: Qt.PointingHandCursor
            onClicked: root.clicked()
        }

        Column {
            anchors.fill: parent; anchors.margins: MichiSpacing.md; spacing: MichiSpacing.sm

            Rectangle {
                width: parent.width; height: width; radius: 8
                color: Qt.rgba(1.0, 1.0, 1.0, 0.03); clip: true
                CoverBridge { anchors.fill: parent; coverKey: root.coverKey || root.playlistTitle || "PL" }
            }

            Text {
                text: root.playlistTitle; color: MichiColors.textPrimary
                font.pixelSize: MichiTypography.cardTitleSize; font.weight: MichiTypography.weightSemiBold
                elide: Text.ElideRight; width: parent.width
            }
            Text {
                text: root.trackCount > 0 ? root.trackCount + " canciones" : ""
                color: MichiColors.textMuted; font.pixelSize: MichiTypography.metaSize
                visible: text !== ""
            }
        }
    }
}
