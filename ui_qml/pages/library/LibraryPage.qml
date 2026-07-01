import QtQuick
import QtQuick.Controls
import "../../theme"
import "../../components"

Item {
    id: root

    Column {
        anchors.centerIn: parent
        spacing: MichiSpacing.lg
        width: 360

        Rectangle {
            anchors.horizontalCenter: parent.horizontalCenter
            width: 48
            height: 48
            radius: 12
            color: Qt.rgba(0.561, 0.718, 1.0, 0.08)

            Text {
                anchors.centerIn: parent
                text: "BL"
                color: MichiColors.accentBlue
                font.pixelSize: 18
                font.weight: MichiTypography.weightBold
                font.letterSpacing: 1.5
                opacity: 0.70
            }
        }

        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: "Biblioteca"
            color: MichiColors.textPrimary
            font.pixelSize: MichiTypography.sectionTitleSize
            font.weight: MichiTypography.weightMedium
        }

        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: "Esta sección aún usa la interfaz clásica de Michi Music Player. La migración a QML está en progreso."
            color: MichiColors.textSecondary
            font.pixelSize: MichiTypography.bodySize
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
            lineHeight: 1.5
        }

        StatusBadge {
            anchors.horizontalCenter: parent.horizontalCenter
            text: "Interfaz clásica"
            kind: "info"
        }
    }
}
