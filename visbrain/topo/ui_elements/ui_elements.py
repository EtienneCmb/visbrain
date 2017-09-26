"""From the topo file, import the topo module."""
from .ui_settings import UiSettings
from .ui_menu import UiMenu
from .ui_screenshot import UiScreenshot


class UiElements(UiSettings, UiMenu, UiScreenshot):
    """Initialize UiElements."""

    def __init__(self):
        """Init."""
        UiSettings.__init__(self)
        UiMenu.__init__(self)
        UiScreenshot.__init__(self)
