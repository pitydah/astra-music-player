import QtQuick
import "../theme"

Item {
    id: root

    property Item target

    OpacityAnimator {
        target: root.target
        from: 0.0
        to: 1.0
        duration: MichiMotion.fast
        easing.type: MichiMotion.easing.standard
    }
}
