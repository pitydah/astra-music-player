import QtQuick
import QtQuick.Controls
import MichiCover 1.0
import "../../theme"

Item {
    id: root

    property string artworkStatus: ""
    property string coverKey: ""

    implicitHeight: 120

    Rectangle {
        anchors.fill: parent
        radius: 8
        color: Qt.rgba(1.0, 1.0, 1.0, 0.02)

        Row {
            anchors.centerIn: parent
            spacing: MichiSpacing.lg

            Rectangle {
                width: 80
                height: 80
                radius: 6
                color: Qt.rgba(1.0, 1.0, 1.0, 0.03)
                clip: true

                CoverBridge {
                    anchors.fill: parent
                    coverKey: root.coverKey
                }
            }

            Column {
                anchors.verticalCenter: parent.verticalCenter
                spacing: MichiSpacing.xs

                Text {
                    text: "Carátula"
                    color: MichiColors.textPrimary
                    font.pixelSize: MichiTypography.bodySize
                    font.weight: MichiTypography.weightSemiBold
                }

                Text {
                    text: root.artworkStatus || "Sin carátula"
                    color: MichiColors.textSecondary
                    font.pixelSize: MichiTypography.metaSize
                }
            }
        }
    }
}
