"""This script initialize all ui files."""

from .ui_settings import UiSettings
from .ui_atlas import UiAtlas
from .ui_sources import UiSources
from .ui_connectivity import UiConnectivity
from .ui_opacity import UiOpacity
from .ui_menu import UiMenu
from .ui_config import UiConfig
from .ui_screenshot import UiScreenshot


class UiElements(UiSettings, UiAtlas, UiSources, UiConnectivity, UiOpacity,
                 UiConfig, UiMenu, UiScreenshot):
    """Inherit from the diffrent ui files and initialize them."""

    def __init__(self):
        """Init."""
        UiSettings.__init__(self)
        UiAtlas.__init__(self)
        UiSources.__init__(self)
        UiConnectivity.__init__(self)
        UiOpacity.__init__(self)
        UiConfig.__init__(self)
        UiMenu.__init__(self)
        UiScreenshot.__init__(self)
