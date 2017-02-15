"""This script initialize all ui files."""

from .uiSettings import uiSettings
from .uiNdPlt import uiNdPlt
from .ui1dPlt import ui1dPlt
from .uiImage import uiImage
from .uiCbar import uiCbar

__all__ = ['uiElements']


class uiElements(uiSettings, uiNdPlt, ui1dPlt, uiImage, uiCbar):
    """Inherit from the diffrent ui files and initialize them."""

    def __init__(self):
        """Init."""
        uiSettings.__init__(self)
        uiNdPlt.__init__(self)
        ui1dPlt.__init__(self)
        uiImage.__init__(self)
        uiCbar.__init__(self)
