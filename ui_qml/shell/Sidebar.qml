import QtQuick
import QtQuick.Controls
import "../theme"
import "../materials"
import "../components"

Item {
    id: root

    property string currentRoute: "home"
    signal routeRequested(string route)

    width: 220

    SidebarMaterial {
        anchors.fill: parent

        Column {
            anchors.fill: parent
            anchors.topMargin: MichiSpacing.xl
            spacing: MichiSpacing.xs

            Text {
                anchors.left: parent.left
                anchors.leftMargin: 20
                text: "Michi"
                color: MichiColors.textPrimary
                font.pixelSize: 20
                font.weight: MichiTypography.weightBold
                height: 40
            }

            Text {
                anchors.left: parent.left
                anchors.leftMargin: 20
                text: "Music Player"
                color: MichiColors.textMuted
                font.pixelSize: MichiTypography.metaSize
                height: 20
            }

            Item { height: MichiSpacing.xl; width: 1 }

            Column {
                anchors.left: parent.left
                anchors.right: parent.right
                spacing: 2

                Repeater {
                    model: ListModel {
                        ListElement { route: "home"; icon: "⌂"; label: "Inicio" }
                        ListElement { route: "library"; icon: "♫"; label: "Biblioteca" }
                        ListElement { route: "connections"; icon: "⇌"; label: "Conexiones" }
                        ListElement { route: "home_audio"; icon: "♬"; label: "Home Audio" }
                        ListElement { route: "assistant"; icon: "⚡"; label: "Asistente" }
                        ListElement { route: "audio_lab"; icon: "⚙"; label: "Audio Lab" }
                        ListElement { route: "settings"; icon: "☰"; label: "Ajustes" }
                    }

                    SidebarItem {
                        iconText: model.icon
                        label: model.label
                        active: root.currentRoute === model.route
                        onClicked: root.routeRequested(model.route)
                    }
                }
            }

            Item { height: MichiSpacing.xl; width: 1 }

            StatusBadge {
                anchors.left: parent.left
                anchors.leftMargin: 20
                text: "Experimental"
                kind: "experimental"
            }
        }
    }
}
