import QtQuick
import QtQuick.Window

Window {
    id: mainWindow
    visible: true
    width: 1440
    height: 900
    title: "Michi Music Player (QML Experimental)"
    color: "#070A10"
    minimumWidth: 1024
    minimumHeight: 640

    MichiApp {
        anchors.fill: parent
    }
}
