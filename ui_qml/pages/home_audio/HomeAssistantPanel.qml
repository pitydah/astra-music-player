import QtQuick
import QtQuick.Controls
import "../../theme"
import "../../components"

Item {
    id: root

    property string state: "not_configured"

    signal configureClicked()
    signal openDiagnostics()

    implicitHeight: 240

    Column {
        anchors.fill: parent
        spacing: MichiSpacing.lg

        GlassMaterial {
            width: parent.width
            height: 200
            variant: "base"
            radius: 12

            Column {
                anchors.fill: parent
                anchors.margins: MichiSpacing.lg
                spacing: MichiSpacing.md

                Text {
                    text: "Home Assistant"
                    color: MichiColors.textPrimary
                    font.pixelSize: MichiTypography.sectionTitleSize
                    font.weight: MichiTypography.weightSemiBold
                }

                Text {
                    text: root.state === "not_configured"
                        ? "Home Assistant no está configurado. Conéctalo para controlar la reproducción en tu hogar."
                        : "Home Assistant conectado y operativo."
                    color: MichiColors.textSecondary
                    font.pixelSize: MichiTypography.bodySize
                    width: parent.width
                    wrapMode: Text.WordWrap
                }

                Row {
                    spacing: MichiSpacing.sm
                    ActionButton {
                        text: root.state === "not_configured" ? "Configurar Home Assistant" : "Abrir Home Assistant"
                        variant: "primary"
                        onClicked: root.configureClicked()
                    }
                    ActionButton {
                        text: "Diagnóstico"
                        variant: "ghost"
                        onClicked: root.openDiagnostics()
                    }
                }

                StatusBadge {
                    text: root.state === "not_configured" ? "No configurado" : "Conectado"
                    kind: root.state === "not_configured" ? "disconnected" : "success"
                }
            }
        }
    }
}
