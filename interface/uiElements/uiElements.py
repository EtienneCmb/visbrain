from .uiSettings import uiSettings
from .uiAtlas import uiAtlas
from .uiSources import uiSources
from .uiConnectivity import uiConnectivity
from .uiCmap import uiCmap
from .uiOpacity import uiOpacity

__all__ = ['uiElements']

class uiElements(uiSettings, uiAtlas, uiSources, uiCmap, uiConnectivity, uiOpacity):

    """Group all ui elements
    """

    def __init__(self):
        uiSettings.__init__(self)
        uiAtlas.__init__(self)
        uiSources.__init__(self)
        uiConnectivity.__init__(self)
        uiCmap.__init__(self)
        uiOpacity.__init__(self)

