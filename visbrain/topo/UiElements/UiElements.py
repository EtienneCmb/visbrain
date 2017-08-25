"""From the topo file, import the topo module."""
from .UiSettings import UiSettings
from .UiMenu import UiMenu
from .UiScreenshot import UiScreenshot

__all__ = ('UiElements')


class UiElements(UiSettings, UiMenu, UiScreenshot):
    """Initialize UiElements."""

    def __init__(self):
        """Init."""
        UiSettings.__init__(self)
        UiMenu.__init__(self)
        UiScreenshot.__init__(self)
