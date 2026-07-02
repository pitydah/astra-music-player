import QtQuick
import QtQuick.Controls
import MichiCover 1.0
import "../../theme"
import "../../components"
import "../../materials"

Item {
    id: root

    property string playlistTitle: ""
    property var bridge: null

    signal backRequested()

    Flickable {
        anchors.fill: parent; anchors.margins: MichiSpacing.xl
        contentHeight: column.height + MichiSpacing.xxl
        clip: true; boundsBehavior: Flickable.StopAtBounds

        Column {
            id: column; width: parent.width; spacing: MichiSpacing.lg

            Row {
                spacing: MichiSpacing.sm
                ActionButton { text: "←"; variant: "ghost"; onClicked: root.backRequested() }
                Text {
                    text: root.playlistTitle; color: MichiColors.textPrimary
                    font.pixelSize: MichiTypography.pageTitleSize; font.weight: MichiTypography.weightSemiBold
                    anchors.verticalCenter: parent.verticalCenter
                }
            }

            Row {
                spacing: MichiSpacing.sm
                ActionButton { text: "Reproducir"; variant: "primary" }
                ActionButton { text: "Editar"; variant: "secondary" }
            }

            Text {
                text: "Contenido de la playlist"
                color: MichiColors.textSecondary; font.pixelSize: MichiTypography.bodySize
            }
        }
    }
}
