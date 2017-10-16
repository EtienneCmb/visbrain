"""This script initialize Brain objects and manage if they are empty.

The following elements are initialized :
    * Atlas : create the main standard MNI brain.
    * Sources : deep points inside / over the brain. They can materialized
    intracranial electrodes, MEG / EEG sensors...
    * Connectivity : straight lines which connect the deep sources.
    * Roi : deep structures can be added (like brodmann areas or gyrus...).
    This can be for processing (like projecting sources activity on it),
    educational or simply for visualiation purpose.
    * Colorbar : initialize the colorbar elements.
    * Projections : set of projections that can be applied on several
    Brain objects (like cortical_projection(), cortical_repartition(...))
    Those transformations are added here, at the top level, so that they
    can have access to the previously defined elements.
"""

from vispy import scene

from ...objects import (CombineSources, CombineConnect, CombineTimeSeries,
                        CombinePictures)

from .AtlasBase import AtlasBase
from .VolumeBase import VolumeBase
from .projection import Projections


class BaseVisual(Projections):
    """Initialize Brain objects.

    Initialize sources / connectivity / areas / colorbar / projections.
    Organize them at diffrent levels and make the link with the graphical
    user interface (if no object is detected, the corresponding panel in the
    GUI has to be deactivate).
    """

    def __init__(self, canvas, parent_sp, progressbar, **kwargs):
        """Init."""
        # ---------- Initialize base ----------
        # Get progress bar :
        self.progressbar = progressbar

        # Initialize visbrain objects :
        self.atlas = AtlasBase(**kwargs)
        self.volume = VolumeBase(parent_sp=parent_sp)
        self.sources = CombineSources(kwargs.get('source_obj', None))
        self.connect = CombineConnect(kwargs.get('connect_obj', None))
        self.tseries = CombineTimeSeries(kwargs.get('time_series_obj', None))
        self.pic = CombinePictures(kwargs.get('picture_obj', None))

        # Add projections :
        Projections.__init__(self, **kwargs)
        self._tobj['brain'] = self.atlas

        # ---------- Panel management ----------
        # Some GUI panels are systematically deactivate if there's no
        # corresponding object.

        # Sources panel:
        if self.sources.name is None:
            self._obj_type_lst.model().item(0).setEnabled(False)
            # Disable menu :
            self.menuDispSources.setChecked(False)
            self.menuDispSources.setEnabled(False)
            self.menuTransform.setEnabled(False)

        # Connectivity panel:
        if self.connect.name is None:
            self._obj_type_lst.model().item(1).setEnabled(False)
            # Disable menu :
            self.menuDispConnect.setEnabled(False)
            self.menuDispConnect.setChecked(False)

        # Time-series panel :
        if self.tseries.name is None:
            self._obj_type_lst.model().item(2).setEnabled(False)

        # Pictures panel :
        if self.pic.name is None:
            self._obj_type_lst.model().item(3).setEnabled(False)

        # ---------- Put everything in a root node ----------
        # Here, each object is put in a root node so that each transformation
        # can be applied to all elements.

        # Create a root node :
        self._vbNode = scene.Node(name='visbrain')

        # Make this root node the parent of others Brain objects :
        self.volume.parent = self._vbNode
        self.sources.parent = self._vbNode
        self.connect.parent = self._vbNode
        self.tseries.parent = self._vbNode
        self.pic.parent = self._vbNode
        self.atlas.mesh.parent = self._vbNode

        # Add XYZ axis (debugging : x=red, y=green, z=blue)
        # scene.visuals.XYZAxis(parent=self._vbNode)

        # Add a rescale / translate transformation to the Node :
        self._vbNode.transform = self.atlas.mesh._btransform
