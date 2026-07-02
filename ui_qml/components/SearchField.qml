import QtQuick
import QtQuick.Controls
import "../theme"
import "../materials"

Item {
    id: root

    property string placeholderText: "Buscar..."
    property string text: ""
    property bool fieldFocused: false

    signal searchTextChanged(string newText)
    signal searchSubmitted(string text)

    implicitHeight: 38
    implicitWidth: 280

    InputMaterial {
        anchors.fill: parent
        focused: root.fieldFocused
        hoveredInput: searchInput.hovered
        radius: 10
    }

    TextInput {
        id: searchInput
        anchors.fill: parent
        anchors.leftMargin: MichiSpacing.md
        anchors.rightMargin: MichiSpacing.md
        anchors.topMargin: MichiSpacing.xs
        anchors.bottomMargin: MichiSpacing.xs
        color: MichiColors.textPrimary
        font.pixelSize: MichiTypography.bodySize
        selectionColor: MichiColors.accentSelection
        clip: true
        verticalAlignment: TextInput.AlignVCenter

        property bool hovered: false

        Text {
            anchors.verticalCenter: parent.verticalCenter
            text: root.placeholderText
            color: MichiColors.textMuted
            font.pixelSize: MichiTypography.bodySize
            visible: parent.text === "" && !parent.activeFocus
        }

        onTextChanged: root.searchTextChanged(text)
        onAccepted: root.searchSubmitted(text)
        onActiveFocusChanged: root.fieldFocused = activeFocus

        MouseArea {
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.IBeamCursor
            onEntered: searchInput.hovered = true
            onExited: searchInput.hovered = false
            onClicked: searchInput.forceActiveFocus()
        }
    }
}
