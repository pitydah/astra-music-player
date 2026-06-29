"""SidebarPanel — dark glass sidebar panel using AcrylicGlassFrame."""
from ui.effects.michi_glass import AcrylicGlassFrame, apply_sidebar_shadow


class SidebarPanel(AcrylicGlassFrame):
    """Dark glass sidebar panel with noise, specular, shadow, and double border."""

    def __init__(self, parent=None):
        super().__init__(
            "sidebarGlass", parent,
            tint_opacity=0.08,
            specular_opacity=14,
            clip_radius=24,
        )
        apply_sidebar_shadow(self)
