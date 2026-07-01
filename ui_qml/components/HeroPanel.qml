import QtQuick
import QtQuick.Controls
import "../theme"
import "../materials"

Item {
    id: root

    property string heroTitle: ""
    property string heroSubtitle: ""
    property var actions: []
    property Item visualSlot: null

    HeroMaterial {
        anchors.fill: parent
        radius: 16
        showGlow: true

        Row {
            anchors.fill: parent
            anchors.margins: MichiSpacing.xl
            spacing: MichiSpacing.xl

            Column {
                width: visualSlot ? parent.width * 0.55 : parent.width
                anchors.verticalCenter: parent.verticalCenter
                spacing: MichiSpacing.md

                Text {
                    text: root.heroTitle
                    color: MichiColors.textPrimary
                    font.pixelSize: MichiTypography.heroTitleSize
                    font.weight: MichiTypography.weightBold
                    width: parent.width
                    wrapMode: Text.WordWrap
                }

                Text {
                    text: root.heroSubtitle
                    color: MichiColors.textSecondary
                    font.pixelSize: MichiTypography.bodySize
                    width: parent.width
                    wrapMode: Text.WordWrap
                    lineHeight: 1.5
                }

                Row {
                    spacing: MichiSpacing.sm
                    visible: root.actions.length > 0
                }
            }

            Item {
                width: visualSlot ? parent.width * 0.40 : 0
                height: parent.height
                visible: visualSlot !== null
                anchors.verticalCenter: parent.verticalCenter

                Loader {
                    anchors.fill: parent
                    sourceComponent: root.visualSlot
                }
            }
        }
    }
}
