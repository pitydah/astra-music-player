import QtQuick
import QtQuick.Controls
import "../theme"
import "../materials"

Item {
    id: root

    property string title: ""
    property string subtitle: ""
    property string variant: "base"
    property bool hovered: false
    property bool interactive: true

    default property alias content: contentArea.children

    GlassMaterial {
        id: glass
        anchors.fill: parent
        variant: root.variant
        hovered: root.hovered
        interactive: root.interactive
        radius: 12

        Column {
            id: layout
            anchors.fill: parent
            anchors.margins: MichiSpacing.lg
            spacing: MichiSpacing.sm
            visible: root.title !== "" || root.subtitle !== ""

            Text {
                text: root.title
                color: MichiColors.textPrimary
                font.pixelSize: MichiTypography.cardTitleSize
                font.weight: MichiTypography.weightSemiBold
                visible: text !== ""
            }

            Text {
                text: root.subtitle
                color: MichiColors.textSecondary
                font.pixelSize: MichiTypography.metaSize
                visible: text !== ""
            }
        }

        Item {
            id: contentArea
            anchors.fill: parent
            anchors.topMargin: (root.title !== "" || root.subtitle !== "") ? 56 : MichiSpacing.lg
            anchors.leftMargin: MichiSpacing.lg
            anchors.rightMargin: MichiSpacing.lg
            anchors.bottomMargin: MichiSpacing.lg
        }
    }
}
