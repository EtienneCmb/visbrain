import vispy.visuals.transforms as vist

from .AtlasBase import AtlasBase
from .SourcesBase import SourcesBase
from .ConnectivityBase import ConnectivityBase
from .CmapBase import CmapBase
from .transformations import transformations

class elements(CmapBase, transformations):

    """docstring for elements
    """

    def __init__(self, canvas, progressbar, **kwargs):
        # Initialize transformation with Null:
        self.transform = vist.ChainTransform([vist.NullTransform()])
        self.progressbar = progressbar

        # Initialize brain, sources and connectivity elements :
        self.atlas = AtlasBase(canvas, a_transform=self.transform, **kwargs)
        self.sources = SourcesBase(canvas, s_transform=self.atlas.transform, **kwargs)
        self.connect = ConnectivityBase(canvas, c_transform=self.atlas.transform, **kwargs)
        CmapBase.__init__(self, **kwargs)

        # Add transformations :
        transformations.__init__(self, **kwargs)

        # Manage visible panel :
        if self.sources.xyz is None:
            self.q_SOURCES.setEnabled(False)
            self.menuTransform.setEnabled(False)
            self.q_TRANS.setEnabled(False)
            self.q_CONNECT.setEnabled(False)
        if self.connect.connect is None:
            self.q_CONNECT.setEnabled(False)

        # Update slider with the brain opacity:
        self.OpacitySlider.setValue(self.atlas.opacity*100)
        # canvas.update()

