import QtQuick
import QtQuick.Controls
import "../../theme"
import "../../materials"
import "../../components"

Item {
    id: root

    property bool serverActive: false
    property int serverPort: 53318
    property int peerCount: 0

    signal startServer()
    signal stopServer()

    implicitHeight: 120

    GlassMaterial {
        anchors.fill: parent
        radius: 12
        variant: root.serverActive ? "accent" : "base"

        Column {
            anchors.fill: parent
            anchors.margins: MichiSpacing.lg
            spacing: MichiSpacing.sm

            Row {
                width: parent.width; spacing: MichiSpacing.sm
                Text {
                    text: "Servidor Sync"
                    color: MichiColors.textPrimary; font.pixelSize: MichiTypography.cardTitleSize
                    font.weight: MichiTypography.weightSemiBold
                }
                StatusBadge {
                    text: root.serverActive ? "Activo" : "Inactivo"
                    kind: root.serverActive ? "active" : "disconnected"
                }
            }

            Text {
                text: root.serverActive
                    ? "Puerto " + root.serverPort + " · " + root.peerCount + " peer(s) detectados"
                    : "Servidor de sincronización detenido"
                color: MichiColors.textSecondary; font.pixelSize: MichiTypography.metaSize
            }

            ActionButton {
                text: root.serverActive ? "Detener servidor" : "Iniciar servidor"
                variant: root.serverActive ? "secondary" : "primary"
                onClicked: root.serverActive ? root.stopServer() : root.startServer()
            }
        }
    }
}
