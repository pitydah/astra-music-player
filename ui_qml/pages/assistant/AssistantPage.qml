import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../../theme"
import "../../components"
import "../../materials"

Item {
    id: root

    property var michiAiBridge: typeof michiAiBridge !== "undefined" ? michiAiBridge : null
    property var chatItems: []

    Component.onCompleted: {
        if (root.michiAiBridge && typeof root.michiAiBridge.refresh !== "undefined") {
            root.michiAiBridge.refresh()
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
                        text: "Michi AI"
                        color: MichiColors.textPrimary
                        font.pixelSize: MichiTypography.heroTitleSize
                        font.weight: MichiTypography.weightBold
                    }

                    Text {
                        text: "Asistente inteligente para tu ecosistema musical. Pregunta, explora y descubre."
                        color: MichiColors.textSecondary
                        font.pixelSize: MichiTypography.bodySize
                        width: parent.width * 0.70
                        wrapMode: Text.WordWrap
                    }

                    StatusBadge {
                        text: "Experimental"
                        kind: "experimental"
                    }
                }
            }

            SectionHeader {
                text: "Sugerencias"
                width: parent.width
            }

            Repeater {
                id: suggestionsRepeater
                model: ListModel {}

                SuggestionCard {
                    width: parent.width
                    suggestionTitle: model.title || ""
                    suggestionDescription: model.description || ""
                    actionRoute: model.route || ""
                    onActionTriggered: {
                        if (typeof navigationBridge !== "undefined" && navigationBridge) {
                            navigationBridge.navigate(model.route)
                        }
                    }
                }
            }

            SectionHeader {
                text: "Chat"
                width: parent.width
            }

            Column {
                id: chatColumn
                width: parent.width
                spacing: MichiSpacing.md
            }

            Row {
                width: parent.width
                spacing: MichiSpacing.sm

                Rectangle {
                    width: parent.width - 50
                    height: 38
                    radius: 10
                    color: MichiColors.surfaceInput
                    border.color: chatInput.activeFocus ? MichiColors.borderFocus : MichiColors.borderSubtle
                    border.width: chatInput.activeFocus ? 2 : 1

                    TextInput {
                        id: chatInput
                        anchors.fill: parent
                        anchors.leftMargin: MichiSpacing.md
                        anchors.rightMargin: MichiSpacing.md
                        anchors.topMargin: MichiSpacing.xs
                        anchors.bottomMargin: MichiSpacing.xs
                        color: MichiColors.textPrimary
                        font.pixelSize: MichiTypography.bodySize
                        placeholderText: "Pregunta a Michi AI..."
                        verticalAlignment: TextInput.AlignVCenter

                        Text {
                            anchors.verticalCenter: parent.verticalCenter
                            text: "Pregunta a Michi AI..."
                            color: MichiColors.textMuted
                            font.pixelSize: MichiTypography.bodySize
                            visible: parent.text === "" && !parent.activeFocus
                        }

                        onAccepted: sendMessage()
                    }
                }

                ActionButton {
                    width: 40
                    height: 38
                    text: "→"
                    variant: "accent"
                    onClicked: sendMessage()
                }
            }

            StatusBadge {
                text: "Interfaz clásica disponible"
                kind: "info"
            }
        }
    }

    function sendMessage() {
        var text = chatInput.text.trim()
        if (text === "") return
        chatInput.text = ""

        if (root.michiAiBridge && typeof root.michiAiBridge.sendMessage !== "undefined") {
            root.michiAiBridge.sendMessage(text)
        }

        var bubble = Qt.createQmlObject(
            'import QtQuick; import "../assistant"; ChatBubble { width: chatColumn.width; messageText: "' + escapeText(text) + '"; role: "user" }',
            chatColumn
        )

        if (root.michiAiBridge) {
            root.michiAiBridge.responseReceived.connect(function(response) {
                var respBubble = Qt.createQmlObject(
                    'import QtQuick; import "../assistant"; ChatBubble { width: chatColumn.width; messageText: "' + escapeText(response) + '"; role: "assistant" }',
                    chatColumn
                )
            })
        }
    }

    function escapeText(t) {
        return t.replace(/"/g, '\\"').replace(/\n/g, ' ').replace(/\r/g, '')
    }

    Connections {
        target: root.michiAiBridge
        function onContextChanged() {
            if (!root.michiAiBridge) return
            var items = root.michiAiBridge.suggestions || []
            suggestionsRepeater.model.clear()
            for (var i = 0; i < items.length; i++) {
                suggestionsRepeater.model.append(items[i])
            }
        }
    }
}
