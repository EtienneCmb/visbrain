"""This script initialize all ui files."""

from .ui_atlas import UiAtlas
from .ui_menu import UiMenu
from .ui_config import UiConfig
from .ui_screenshot import UiScreenshot
# Objects :
from .ui_connectivity import UiConnectivity
from .ui_sources import UiSources
from .ui_timeseries import UiTimeSeries
from .ui_pictures import UiPictures
from .ui_vectors import UiVectors
from .ui_objects import UiObjects


class UiElements(UiAtlas, UiSources, UiConnectivity, UiTimeSeries,
                 UiPictures, UiVectors, UiConfig, UiMenu, UiScreenshot,
                 UiObjects):
    """Inherit from the diffrent ui files and initialize them."""

    def __init__(self):
        """Init."""
        UiAtlas.__init__(self)
        UiSources.__init__(self)
        UiConnectivity.__init__(self)
        UiTimeSeries.__init__(self)
        UiPictures.__init__(self)
        UiVectors.__init__(self)
        UiConfig.__init__(self)
        UiMenu.__init__(self)
        UiScreenshot.__init__(self)
        UiObjects.__init__(self)
