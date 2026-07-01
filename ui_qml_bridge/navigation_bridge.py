from PySide6.QtCore import QObject, Signal, Property


class NavigationBridge(QObject):
    routeChanged = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_route = "home"

    @Property(str, notify=routeChanged)
    def currentRoute(self):
        return self._current_route

    @currentRoute.setter
    def currentRoute(self, route: str):
        if route != self._current_route:
            self._current_route = route
            self.routeChanged.emit(route)

    def navigate(self, route: str):
        self.currentRoute = route
