pragma Singleton
import QtQuick

QtObject {
    readonly property QtObject colors: MichiColors
    readonly property QtObject typography: MichiTypography
    readonly property QtObject spacing: MichiSpacing
    readonly property QtObject motion: MichiMotion
}
