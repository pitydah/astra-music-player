import QtQuick
import QtQuick.Controls
import "../theme"
import "../components"
import "../materials"

Item {
    id: root

    property var settingsBridge: typeof settingsBridge !== "undefined" ? settingsBridge : null

    signal closeRequested()

    Flickable {
        anchors.fill: parent; anchors.margins: MichiSpacing.xl
        contentHeight: column.height + MichiSpacing.xxl
        clip: true; boundsBehavior: Flickable.StopAtBounds

        Column {
            id: column; width: parent.width; spacing: MichiSpacing.lg

            Row {
                spacing: MichiSpacing.sm
                ActionButton { text: "←"; variant: "ghost"; onClicked: root.closeRequested() }
                Text {
                    text: "Ajustes"; color: MichiColors.textPrimary
                    font.pixelSize: MichiTypography.pageTitleSize; font.weight: MichiTypography.weightSemiBold
                    anchors.verticalCenter: parent.verticalCenter
                }
            }

            Repeater {
                model: root.settingsBridge ? root.settingsBridge.sections : []

                GlassCard {
                    width: parent.width; height: 70
                    title: modelData.title || ""
                    subtitle: modelData.desc || ""
                    variant: "base"
                }
            }
        }
    }
}
