import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../theme"
import "../../components"
import "../../materials"

Item {
    id: root

    property var audioLabBridge: typeof audioLabBridge !== "undefined" ? audioLabBridge : null

    Component.onCompleted: {
        if (root.audioLabBridge && typeof root.audioLabBridge.refresh !== "undefined")
            root.audioLabBridge.refresh()
    }

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
                        text: "Audio Lab"
                        color: MichiColors.textPrimary
                        font.pixelSize: MichiTypography.heroTitleSize; font.weight: MichiTypography.weightBold
                    }
                    Text {
                        text: "Herramientas de análisis, conversión y diagnóstico para tu biblioteca musical."
                        color: MichiColors.textSecondary
                        font.pixelSize: MichiTypography.bodySize; width: parent.width * 0.70; wrapMode: Text.WordWrap
                    }
                }
            }

            GlassCard {
                width: parent.width; height: 80
                title: "Inspector de metadatos"
                subtitle: "Revisa campos, carátulas y consistencia de una pista."
                variant: "accent"
                onClicked: {
                    if (typeof navigationBridge !== "undefined" && navigationBridge)
                        navigationBridge.navigate("metadata_inspector")
                }
            }

            SectionHeader { text: "Estado de la biblioteca"; width: parent.width }

            GlassMaterial {
                width: parent.width; radius: 12; variant: "base"
                Row {
                    anchors.fill: parent; anchors.margins: MichiSpacing.lg; spacing: MichiSpacing.xl
                    Column { spacing: 4
                        Text { text: root.audioLabBridge ? root.audioLabBridge.totalTracks : "—"; color: MichiColors.accentBlue; font.pixelSize: MichiTypography.heroTitleSize; font.weight: MichiTypography.weightBold }
                        Text { text: "Canciones"; color: MichiColors.textMuted; font.pixelSize: MichiTypography.metaSize }
                    }
                    Column { spacing: 4
                        Text { text: root.audioLabBridge ? root.audioLabBridge.missingMetadata : "—"; color: root.audioLabBridge && root.audioLabBridge.missingMetadata > 0 ? MichiColors.warning : MichiColors.textPrimary; font.pixelSize: MichiTypography.heroTitleSize; font.weight: MichiTypography.weightBold }
                        Text { text: "Sin metadata"; color: MichiColors.textMuted; font.pixelSize: MichiTypography.metaSize }
                    }
                    Column { spacing: 4
                        Text { text: root.audioLabBridge ? root.audioLabBridge.missingCovers : "—"; color: root.audioLabBridge && root.audioLabBridge.missingCovers > 0 ? MichiColors.warning : MichiColors.textPrimary; font.pixelSize: MichiTypography.heroTitleSize; font.weight: MichiTypography.weightBold }
                        Text { text: "Sin carátula"; color: MichiColors.textMuted; font.pixelSize: MichiTypography.metaSize }
                    }
                }
            }

            SectionHeader { text: "Herramientas"; width: parent.width }

            Grid {
                width: parent.width; columns: 2; columnSpacing: MichiSpacing.md; rowSpacing: MichiSpacing.md

                Repeater {
                    model: root.audioLabBridge ? root.audioLabBridge.modules : []

                    GlassCard {
                        width: (parent.width - MichiSpacing.md) / 2; height: 90
                        title: modelData.title || ""
                        subtitle: modelData.desc || ""
                        variant: modelData.status === "available" ? "base" : "status"
                        onClicked: {
                            if (modelData.id === "diagnostics" && typeof navigationBridge !== "undefined")
                                navigationBridge.navigate("audio_lab")
                        }
                    }
                }
            }

            GlassMaterial {
                width: parent.width; radius: 12; variant: "status"
                Column {
                    anchors.fill: parent; anchors.margins: MichiSpacing.lg; spacing: MichiSpacing.sm
                    StatusBadge { text: "Solo lectura"; kind: "info" }
                    StatusBadge { text: "Interfaz clásica disponible"; kind: "disconnected" }
                }
            }
        }
    }
}
