import QtQuick
import QtQuick.Controls
import "../theme"
import "../components"
import "../materials"

Item {
    id: root

    property var mixBridge: typeof mixBridge !== "undefined" ? mixBridge : null

    signal backRequested()

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

            Row {
                spacing: MichiSpacing.sm

                ActionButton {
                    text: "←"
                    variant: "ghost"
                    onClicked: root.backRequested()
                }

                Text {
                    text: root.mixBridge ? root.mixBridge.currentMixTitle : "Mix"
                    color: MichiColors.textPrimary
                    font.pixelSize: MichiTypography.pageTitleSize
                    font.weight: MichiTypography.weightSemiBold
                    anchors.verticalCenter: parent.verticalCenter
                }
            }

            SongTable {
                width: parent.width
                height: parent.height - 60
                songs: root.mixBridge ? root.mixBridge.currentSongs : []
                bridge: null
            }
        }
    }
}
