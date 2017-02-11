"""This script initialize all ui files."""

from .uiSettings import uiSettings
from .uiNdPlt import uiNdPlt
from .ui1dPlt import ui1dPlt

__all__ = ['uiElements']


class uiElements(uiSettings, uiNdPlt, ui1dPlt):
    """Inherit from the diffrent ui files and initialize them."""

    def __init__(self):
        """Init."""
        uiSettings.__init__(self)
        uiNdPlt.__init__(self)
        ui1dPlt.__init__(self)
