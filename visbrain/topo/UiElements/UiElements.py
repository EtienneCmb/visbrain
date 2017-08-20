"""From the topo file, import the topo module."""
from .UiSettings import UiSettings
from .UiMenu import UiMenu

__all__ = ('UiElements')


class UiElements(UiSettings, UiMenu):
    """Initialize UiElements."""

    def __init__(self):
        """Init."""
        UiSettings.__init__(self)
        UiMenu.__init__(self)
