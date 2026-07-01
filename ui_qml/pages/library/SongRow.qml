import QtQuick
import QtQuick.Controls
import "../../theme"
import "../../components"
import "../../materials"

Item {
    id: root

    property string trackTitle: ""
    property string trackArtist: ""
    property string trackAlbum: ""
    property string trackDuration: ""
    property string trackFilepath: ""
    property bool hovered: false

    signal clicked()
    signal doubleClicked()

    implicitHeight: 36

    Rectangle {
        anchors.fill: parent
        color: root.hovered ? Qt.rgba(1.0, 1.0, 1.0, 0.03) : "transparent"
        Behavior on color { ColorAnimation { duration: MichiMotion.fast } }

        Row {
            anchors.fill: parent
            anchors.leftMargin: MichiSpacing.md
            anchors.rightMargin: MichiSpacing.md
            spacing: MichiSpacing.sm

            Text {
                width: parent.width * 0.30
                anchors.verticalCenter: parent.verticalCenter
                text: root.trackTitle
                color: root.hovered ? MichiColors.textPrimary : MichiColors.textNormal
                font.pixelSize: MichiTypography.bodySize
                elide: Text.ElideRight
            }

            Text {
                width: parent.width * 0.25
                anchors.verticalCenter: parent.verticalCenter
                text: root.trackArtist
                color: MichiColors.textSecondary
                font.pixelSize: MichiTypography.bodySize
                elide: Text.ElideRight
            }

            Text {
                width: parent.width * 0.25
                anchors.verticalCenter: parent.verticalCenter
                text: root.trackAlbum
                color: MichiColors.textSecondary
                font.pixelSize: MichiTypography.bodySize
                elide: Text.ElideRight
            }

            Text {
                width: parent.width * 0.12
                anchors.verticalCenter: parent.verticalCenter
                text: root.trackDuration
                color: MichiColors.textMuted
                font.pixelSize: MichiTypography.metaSize
                horizontalAlignment: Text.AlignRight
            }
        }

        MouseArea {
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            onEntered: root.hovered = true
            onExited: root.hovered = false
            onClicked: root.clicked()
            onDoubleClicked: root.doubleClicked()
        }
    }
}
