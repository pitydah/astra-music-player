import QtQuick
import QtQuick.Controls
import "../theme"
import "../components"
import "../materials"

Item {
    id: root

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

            HeroMaterial {
                width: parent.width; height: 140; radius: 16; showGlow: true
                Column {
                    anchors.fill: parent; anchors.margins: MichiSpacing.xl; spacing: MichiSpacing.sm
                    Text {
                        text: "Radio"; color: MichiColors.textPrimary
                        font.pixelSize: MichiTypography.heroTitleSize; font.weight: MichiTypography.weightBold
                    }
                    Text {
                        text: "Emisoras, podcasts y transmisiones en vivo."; color: MichiColors.textSecondary
                        font.pixelSize: MichiTypography.bodySize; width: parent.width * 0.70; wrapMode: Text.WordWrap
                    }
                }
            }

            GlassCard {
                width: parent.width; height: 80
                title: "Radio en vivo"; subtitle: "Escucha emisoras de todo el mundo. Próximamente."
                variant: "base"
            }

            GlassCard {
                width: parent.width; height: 80
                title: "Podcasts"; subtitle: "Suscripción y gestión de episodios. Próximamente."
                variant: "base"
            }

            GlassCard {
                width: parent.width; height: 80
                title: "Grabaciones"; subtitle: "Captura y almacena transmisiones. Próximamente."
                variant: "base"
            }

            StatusBadge { text: "Próximamente"; kind: "experimental" }
        }
    }
}
