import QtQuick
import QtQuick.Controls
import "../theme"
import "../components"
import "../materials"

Item {
    id: root

    property var radioBridge: typeof radioBridge !== "undefined" ? radioBridge : null

    Component.onCompleted: {
        if (root.radioBridge && typeof root.radioBridge.refresh !== "undefined")
            root.radioBridge.refresh()
    }

    Flickable {
        anchors.fill: parent; anchors.margins: MichiSpacing.xl
        contentHeight: column.height + MichiSpacing.xxl
        clip: true; boundsBehavior: Flickable.StopAtBounds

        Column {
            id: column; width: parent.width; spacing: MichiSpacing.lg

            HeroMaterial {
                width: parent.width; height: 140; radius: 16; showGlow: true
                Column {
                    anchors.fill: parent; anchors.margins: MichiSpacing.xl; spacing: MichiSpacing.sm
                    Text {
                        text: "Radio"; color: MichiColors.textPrimary
                        font.pixelSize: MichiTypography.heroTitleSize; font.weight: MichiTypography.weightBold
                    }
                    Text {
                        text: "Emisoras de todo el mundo."; color: MichiColors.textSecondary
                        font.pixelSize: MichiTypography.bodySize; width: parent.width * 0.70; wrapMode: Text.WordWrap
                    }
                }
            }

            SectionHeader { text: "Favoritas"; width: parent.width }

            Repeater {
                model: root.radioBridge ? root.radioBridge.favorites : []

                GlassCard {
                    width: parent.width; height: 60
                    title: modelData.name || ""
                    subtitle: modelData.codec ? modelData.codec + (modelData.country ? " · " + modelData.country : "") : ""
                    variant: "base"
                }
            }

            Text {
                text: "No hay emisoras favoritas."
                color: MichiColors.textMuted; font.pixelSize: MichiTypography.bodySize
                width: parent.width; wrapMode: Text.WordWrap
                visible: root.radioBridge && root.radioBridge.favorites.length === 0
            }

            SectionHeader { text: "Todas las emisoras"; width: parent.width }

            Repeater {
                model: root.radioBridge ? root.radioBridge.stations : []

                GlassCard {
                    width: parent.width; height: 60
                    title: modelData.name || ""
                    subtitle: modelData.url || ""
                    variant: "base"
                }
            }

            Text {
                text: "No hay emisoras configuradas. Agrega una URL para comenzar."
                color: MichiColors.textMuted; font.pixelSize: MichiTypography.bodySize
                width: parent.width; wrapMode: Text.WordWrap
                visible: root.radioBridge && root.radioBridge.stations.length === 0
            }

            StatusBadge { text: "Interfaz clásica disponible"; kind: "info" }
        }
    }
}
