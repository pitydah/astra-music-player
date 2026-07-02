import QtQuick
import QtQuick.Controls
import "../../theme"
import "../../components"
import "../../materials"

Item {
    id: root

    property var metadataBridge: typeof metadataBridge !== "undefined" ? metadataBridge : null

    function inspect(filepath) {
        if (root.metadataBridge && typeof root.metadataBridge.inspectTrack !== "undefined") {
            root.metadataBridge.inspectTrack(filepath)
        }
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

            Text {
                text: "Inspector de metadatos"
                color: MichiColors.textPrimary
                font.pixelSize: MichiTypography.pageTitleSize
                font.weight: MichiTypography.weightSemiBold
            }

            Loader {
                width: parent.width
                sourceComponent: root.metadataBridge && root.metadataBridge.hasSelection ? inspectorContent : emptyComponent
            }
        }
    }

    Component {
        id: emptyComponent
        Column {
            width: parent.width
            spacing: MichiSpacing.lg
            anchors.centerIn: parent
            width: 360

            Rectangle {
                anchors.horizontalCenter: parent.horizontalCenter
                width: 48; height: 48; radius: 12
                color: Qt.rgba(0.561, 0.718, 1.0, 0.08)
                Text {
                    anchors.centerIn: parent
                    text: "MI"
                    color: MichiColors.accentBlue
                    font.pixelSize: 18; font.weight: MichiTypography.weightBold
                    font.letterSpacing: 1.5; opacity: 0.70
                }
            }

            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: "Selecciona una canción"
                color: MichiColors.textPrimary
                font.pixelSize: MichiTypography.sectionTitleSize
                font.weight: MichiTypography.weightMedium
            }

            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: "Selecciona una canción en la Biblioteca para inspeccionar sus metadatos."
                color: MichiColors.textSecondary
                font.pixelSize: MichiTypography.bodySize
                wrapMode: Text.WordWrap
                horizontalAlignment: Text.AlignHCenter
            }
        }
    }

    Component {
        id: inspectorContent
        Column {
            width: parent.width
            spacing: MichiSpacing.lg

            GlassMaterial {
                width: parent.width
                height: 120
                radius: 12
                variant: "base"

                Column {
                    anchors.fill: parent
                    anchors.margins: MichiSpacing.lg
                    spacing: MichiSpacing.sm

                    Text {
                        text: root.metadataBridge ? root.metadataBridge.trackTitle : "—"
                        color: MichiColors.textPrimary
                        font.pixelSize: MichiTypography.sectionTitleSize
                        font.weight: MichiTypography.weightSemiBold
                    }

                    Text {
                        text: root.metadataBridge ? root.metadataBridge.trackArtist : ""
                        color: MichiColors.textSecondary
                        font.pixelSize: MichiTypography.bodySize
                        visible: text !== ""
                    }

                    Text {
                        text: root.metadataBridge ? root.metadataBridge.trackAlbum : ""
                        color: MichiColors.textMuted
                        font.pixelSize: MichiTypography.metaSize
                        visible: text !== ""
                    }
                }
            }

            GlassMaterial {
                width: parent.width
                radius: 12
                variant: "base"

                Column {
                    anchors.fill: parent
                    anchors.margins: MichiSpacing.lg
                    spacing: MichiSpacing.xs

                    Text {
                        text: "Metadatos"
                        color: MichiColors.textPrimary
                        font.pixelSize: MichiTypography.cardTitleSize
                        font.weight: MichiTypography.weightSemiBold
                        bottomPadding: MichiSpacing.sm
                    }

                    Repeater {
                        model: root.metadataBridge ? root.metadataBridge.fields : []

                        MetadataFieldRow {
                            width: parent.width
                            fieldLabel: modelData.label || ""
                            fieldValue: modelData.value || ""
                        }
                    }
                }
            }

            MetadataArtworkPreview {
                width: parent.width
                artworkStatus: root.metadataBridge ? root.metadataBridge.artworkStatus : ""
                coverKey: root.metadataBridge && root.metadataBridge.hasSelection ? "inspector" : ""
            }

            GlassMaterial {
                width: parent.width
                radius: 12
                variant: "base"

                Column {
                    anchors.fill: parent
                    anchors.margins: MichiSpacing.lg
                    spacing: MichiSpacing.md

                    Text {
                        text: "Acciones"
                        color: MichiColors.textPrimary
                        font.pixelSize: MichiTypography.cardTitleSize
                        font.weight: MichiTypography.weightSemiBold
                    }

                    ActionButton {
                        text: "Previsualizar sugerencias"
                        variant: "secondary"
                        onClicked: {
                            if (root.metadataBridge && typeof root.metadataBridge.previewSuggestedFixes !== "undefined") {
                                root.metadataBridge.previewSuggestedFixes()
                            }
                        }
                    }

                    ActionButton {
                        text: "Aplicar cambios"
                        variant: "ghost"
                        enabled: root.metadataBridge ? root.metadataBridge.canApply : false
                        tooltip: "La escritura de metadatos se habilitará en una fase posterior."
                    }
                }
            }
        }
    }
}
