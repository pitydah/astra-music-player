import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../theme"
import "../../components"
import "../../materials"

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
                width: parent.width
                height: 140
                radius: 16
                showGlow: true

                Column {
                    anchors.fill: parent
                    anchors.margins: MichiSpacing.xl
                    spacing: MichiSpacing.sm

                    Text {
                        text: "Audio Lab"
                        color: MichiColors.textPrimary
                        font.pixelSize: MichiTypography.heroTitleSize
                        font.weight: MichiTypography.weightBold
                    }

                    Text {
                        text: "Herramientas de análisis, conversión y diagnóstico para tu biblioteca musical."
                        color: MichiColors.textSecondary
                        font.pixelSize: MichiTypography.bodySize
                        width: parent.width * 0.70
                        wrapMode: Text.WordWrap
                    }
                }
            }

            SectionHeader {
                text: "Herramientas de inspección"
                width: parent.width
            }

            GlassCard {
                width: parent.width
                height: 80
                title: "Inspector de metadatos"
                subtitle: "Revisa campos, carátulas y consistencia de una pista. Solo lectura."
                variant: "accent"
                onClicked: {
                    if (typeof navigationBridge !== "undefined" && navigationBridge)
                        navigationBridge.navigate("metadata_inspector")
                }
            }

            SectionHeader {
                text: "Próximamente"
                width: parent.width
            }

            Grid {
                width: parent.width
                columns: 2
                columnSpacing: MichiSpacing.md
                rowSpacing: MichiSpacing.md

                GlassCard {
                    width: (parent.width - MichiSpacing.md) / 2
                    height: 80
                    title: "Salud de biblioteca"
                    subtitle: "Próximamente"
                    variant: "base"
                }

                GlassCard {
                    width: (parent.width - MichiSpacing.md) / 2
                    height: 80
                    title: "Auditoría de carátulas"
                    subtitle: "Próximamente"
                    variant: "base"
                }

                GlassCard {
                    width: (parent.width - MichiSpacing.md) / 2
                    height: 80
                    title: "Formatos y calidad"
                    subtitle: "Próximamente"
                    variant: "base"
                }

                GlassCard {
                    width: (parent.width - MichiSpacing.md) / 2
                    height: 80
                    title: "Acciones avanzadas"
                    subtitle: "Escritura de metadatos, conversión, ripping"
                    variant: "base"
                }
            }

            GlassMaterial {
                width: parent.width
                radius: 12
                variant: "status"

                Row {
                    anchors.fill: parent
                    anchors.margins: MichiSpacing.lg
                    spacing: MichiSpacing.md

                    StatusBadge { text: "Solo lectura"; kind: "info" }
                    StatusBadge { text: "Interfaz clásica disponible"; kind: "disconnected" }
                }
            }
        }
    }
}
