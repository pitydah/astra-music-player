import QtQuick
import "../theme"
import "../materials"

Item {
    id: root

    property string panelTitle: "Inspector"
    property bool ready: false

    GlassMaterial {
        anchors.fill: parent
        variant: "base"
        radius: 12

        Column {
            anchors.fill: parent
            anchors.margins: MichiSpacing.lg
            spacing: MichiSpacing.sm

            Text {
                text: root.panelTitle
                color: MichiColors.textPrimary
                font.pixelSize: MichiTypography.sectionTitleSize
                font.weight: MichiTypography.weightSemiBold
            }

            Text {
                text: root.ready ? "Inspector activo" : "Inspector no disponible en modo experimental"
                color: MichiColors.textSecondary
                font.pixelSize: MichiTypography.bodySize
                visible: true
            }
        }
    }
}
