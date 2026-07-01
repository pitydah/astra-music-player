import QtQuick
import QtQuick.Controls
import "../theme"
import "../components"

Item {
    id: root

    property string pageTitle: "Inicio"

    height: 56

    Rectangle {
        anchors.fill: parent
        color: MichiColors.bgApp

        Rectangle {
            anchors.bottom: parent.bottom
            width: parent.width
            height: 1
            color: MichiColors.borderSubtle
        }

        Row {
            anchors.fill: parent
            anchors.leftMargin: MichiSpacing.xl
            anchors.rightMargin: MichiSpacing.xl
            spacing: MichiSpacing.lg

            Text {
                text: root.pageTitle
                color: MichiColors.textPrimary
                font.pixelSize: MichiTypography.pageTitleSize
                font.weight: MichiTypography.weightSemiBold
                anchors.verticalCenter: parent.verticalCenter
            }

            Item { width: 1; height: 1; Layout.fillWidth: true }

            SearchField {
                anchors.verticalCenter: parent.verticalCenter
                placeholderText: "Buscar en Michi..."
            }
        }
    }
}
