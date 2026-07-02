import QtQuick
import "../../theme"
import "../../materials"
import "../../components"

Item {
    id: root

    implicitHeight: 420

    Column {
        anchors.fill: parent
        spacing: MichiSpacing.lg

        GlassMaterial {
            width: parent.width
            height: 80
            variant: "base"
            radius: 12

            Row {
                anchors.fill: parent
                anchors.margins: MichiSpacing.lg
                spacing: MichiSpacing.lg

                Column {
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: MichiSpacing.xs

                    Text {
                        text: "Michi Music Stream"
                        color: MichiColors.textPrimary
                        font.pixelSize: MichiTypography.sectionTitleSize
                        font.weight: MichiTypography.weightSemiBold
                    }

                    Text {
                        text: "Sistema propio del ecosistema Michi para transmitir música a receptores y equipos de audio dentro de la red local."
                        color: MichiColors.textSecondary
                        font.pixelSize: MichiTypography.bodySize
                        width: parent.width - 100
                        wrapMode: Text.WordWrap
                    }
                }

                StatusBadge { text: "Concepto"; kind: "experimental" }
            }
        }

        Text {
            text: "Componentes del sistema"
            color: MichiColors.textPrimary
            font.pixelSize: MichiTypography.sectionTitleSize
            font.weight: MichiTypography.weightSemiBold
        }

        Grid {
            width: parent.width
            columns: 2
            columnSpacing: MichiSpacing.md
            rowSpacing: MichiSpacing.md

            Repeater {
                model: [
                    { title: "Receptores Michi", desc: "Dispositivos de audio en red" },
                    { title: "Salas y zonas", desc: "Agrupación de receptores" },
                    { title: "Transmisión local", desc: "Streaming sin servidor externo" },
                    { title: "Sincronización multiroom", desc: "Audio sincronizado en todas las salas" },
                    { title: "Diagnóstico de latencia", desc: "Medición de delay en la red" },
                    { title: "Protocolo Michi Stream", desc: "Capa de transporte del ecosistema" }
                ]

                GlassCard {
                    width: (parent.width - MichiSpacing.md) / 2
                    height: 80
                    title: modelData.title
                    subtitle: modelData.desc
                    variant: "base"
                }
            }
        }
    }
}
