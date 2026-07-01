import QtQuick
import QtQuick.Controls
import "../../theme"
import "../../components"

Item {
    id: root

    EmptyState {
        anchors.centerIn: parent
        iconText: "⚡"
        title: "Asistente Michi"
        subtitle: "Esta sección aún usa la interfaz clásica. Migración QML en progreso."
    }
}
