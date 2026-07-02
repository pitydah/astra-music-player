import QtQuick
import QtQuick.Controls
import "../theme"
import "../components"
import "../materials"

Item {
    id: root

    signal closeRequested()

    Flickable {
        anchors.fill: parent
        anchors.margins: MichiSpacing.xl
        contentHeight: column.height + MichiSpacing.xxl
        clip: true
        boundsBehavior: Flickable.StopAtBounds

        Column {
            id: column
            width: parent.width
            spacing: MichiSpacing.lg

            Row {
                spacing: MichiSpacing.sm

                ActionButton { text: "←"; variant: "ghost"; onClicked: root.closeRequested() }

                Text {
                    text: "Ajustes"
                    color: MichiColors.textPrimary
                    font.pixelSize: MichiTypography.pageTitleSize
                    font.weight: MichiTypography.weightSemiBold
                    anchors.verticalCenter: parent.verticalCenter
                }
            }

            GlassCard {
                width: parent.width; height: 70
                title: "Reproducción"; subtitle: "Salida de audio, volumen, crossfade. Próximamente."
                variant: "base"
            }

            GlassCard {
                width: parent.width; height: 70
                title: "Biblioteca"; subtitle: "Carpetas, escaneo, organización. Próximamente."
                variant: "base"
            }

            GlassCard {
                width: parent.width; height: 70
                title: "Apariencia"; subtitle: "Tema, idioma, experimental. Próximamente."
                variant: "base"
            }

            GlassCard {
                width: parent.width; height: 70
                title: "Red y servidores"; subtitle: "Michi Micro Server, conexiones. Próximamente."
                variant: "base"
            }

            GlassCard {
                width: parent.width; height: 70
                title: "Sync y dispositivos"; subtitle: "Android, sincronización. Próximamente."
                variant: "base"
            }

            StatusBadge { text: "Ajustes disponibles en la interfaz clásica"; kind: "info" }
        }
    }
}
