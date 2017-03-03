"""This script initialize all ui files."""

from .uiSettings import uiSettings
from .uiPanels import uiPanels
from .uiSignal import uiSignal

__all__ = ['uiElements']


class uiElements(uiSettings, uiPanels, uiSignal):
    """Inherit from the diffrent ui files and initialize them."""

    def __init__(self):
        """Init."""
        uiSettings.__init__(self)
        uiPanels.__init__(self)
        uiSignal.__init__(self)
