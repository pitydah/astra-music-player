import QtQuick
import QtQuick.Controls
import "../../theme"
import "../../materials"
import "../../components"

Item {
    id: root

    property var discoveredServers: []

    signal serverSelected(int index)

    implicitHeight: 300

    GlassMaterial {
        anchors.fill: parent
        variant: "base"
        radius: 12

        Column {
            anchors.fill: parent
            anchors.margins: MichiSpacing.lg
            spacing: MichiSpacing.md

            Text {
                text: "Descubrimiento en red"
                color: MichiColors.textPrimary
                font.pixelSize: MichiTypography.sectionTitleSize
                font.weight: MichiTypography.weightSemiBold
            }

            Text {
                text: "Servidores Michi detectados en la red local"
                color: MichiColors.textSecondary
                font.pixelSize: MichiTypography.bodySize
                visible: root.discoveredServers.length > 0
            }

            Repeater {
                model: root.discoveredServers

                DiscoveryResultCard {
                    width: parent.width
                    height: 120
                    serverName: modelData.name || ""
                    serverHost: modelData.host || ""
                    serverType: modelData.type || ""
                    serverStatus: modelData.status || "disconnected"
                    ctaText: "Conectar"
                    onCtaClicked: root.serverSelected(index)
                }
            }

            Text {
                text: "No se encontraron servidores en la red. Asegúrate de que Michi Micro Server esté ejecutándose."
                color: MichiColors.textMuted
                font.pixelSize: MichiTypography.bodySize
                visible: root.discoveredServers.length === 0
                wrapMode: Text.WordWrap
                width: parent.width
            }
        }
    }
}
