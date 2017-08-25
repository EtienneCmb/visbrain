"""This script initialize all ui files."""

from .uiSettings import uiSettings
from .uiAtlas import uiAtlas
from .uiSources import uiSources
from .uiConnectivity import uiConnectivity
from .uiOpacity import uiOpacity
from .uiMenu import uiMenu
from .uiConfig import uiConfig
from .UiScreenshot import UiScreenshot

__all__ = ('uiElements')


class uiElements(uiSettings, uiAtlas, uiSources, uiConnectivity, uiOpacity,
                 uiConfig, uiMenu, UiScreenshot):
    """Inherit from the diffrent ui files and initialize them."""

    def __init__(self):
        """Init."""
        uiSettings.__init__(self)
        uiAtlas.__init__(self)
        uiSources.__init__(self)
        uiConnectivity.__init__(self)
        uiOpacity.__init__(self)
        uiConfig.__init__(self)
        uiMenu.__init__(self)
        UiScreenshot.__init__(self)
