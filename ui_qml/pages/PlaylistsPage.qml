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
                        text: "Playlists"; color: MichiColors.textPrimary
                        font.pixelSize: MichiTypography.heroTitleSize; font.weight: MichiTypography.weightBold
                    }
                    Text {
                        text: "Gestiona tus listas de reproducción."; color: MichiColors.textSecondary
                        font.pixelSize: MichiTypography.bodySize; width: parent.width * 0.70; wrapMode: Text.WordWrap
                    }
                }
            }

            SectionHeader { text: "Tus playlists"; width: parent.width }

            GlassCard {
                width: parent.width; height: 80
                title: "Listas manuales"; subtitle: "Crea y edita playlists con tus canciones favoritas."
                variant: "base"
            }

            GlassCard {
                width: parent.width; height: 80
                title: "Listas inteligentes"; subtitle: "Playlists dinámicas basadas en reglas. Próximamente."
                variant: "base"
            }

            GlassCard {
                width: parent.width; height: 80
                title: "Importar / Exportar"; subtitle: "Comparte listas en formato estándar. Próximamente."
                variant: "base"
            }

            StatusBadge { text: "Interfaz clásica disponible"; kind: "info" }
        }
    }
}
