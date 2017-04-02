"""This script initialize Brain objects and manage if they are empty.

The following elements are initialized :
    * Atlas : create the main standard MNI brain.
    * Sources : deep points inside / over the brain. They can materialized
    intracranial electrodes, MEG / EEG sensors...
    * Connectivity : straight lines which connect the deep sources.
    * Areas : deep structures can be added (like brodmann areas or gyrus...).
    This can be for processing (like projecting sources activity on it),
    educational or simply for visualiation purpose.
    * Colorbar : initialize the colorbar elements.
    * Projections : set of projections that can be applied on several
    Brain objects (like cortical_projection(), cortical_repartition(...))
    Those transformations are added here, at the top level, so that they
    can have access to the previously defined elements.
"""

from vispy.scene import Node

from .AtlasBase import AtlasBase
from .SourcesBase import SourcesBase
from .ConnectBase import ConnectBase
from .CbarBase import CbarBase
from .AreaBase import AreaBase
from .projection import Projections


class base(CbarBase, Projections):
    """Initialize Brain objects.

    Initialize sources / connectivity / areas / colorbar / projections.
    Organize them at diffrent levels and make the link with the graphical
    user interface (if no object is detected, the corresponding panel in the
    GUI has to be deactivate).
    """

    def __init__(self, canvas, progressbar, **kwargs):
        """Init."""
        # ---------- Initialize base ----------
        # Get progress bar :
        self.progressbar = progressbar

        # Initialize brain, sources and connectivity objects and put them in
        # the relevant attribute :
        self.atlas = AtlasBase(**kwargs)
        self.sources = SourcesBase(**kwargs)
        self.connect = ConnectBase(_xyz=self.sources.xyz,
                                   c_xyz=self.sources.xyz, **kwargs)
        self.area = AreaBase(scale_factor=self.atlas._scaleMax,
                             name='NoneArea', select=None, color='#ab4642')

        # Initialize colorbar base  (by default, with sources base):
        self.cb = CbarBase(self.view.cbwc, cb_fontcolor=self._cbfontcolor,
                           cb_fontsize=self._cbfontsize,
                           cb_label=self._cblabel, **self.sources._cb)

        # Add projections :
        Projections.__init__(self, **kwargs)

        # ---------- Panel management ----------
        # Some GUI panels are systematically deactivate if there's no
        # corresponding object.

        # Sources panel:
        if self.sources.mesh.name is 'NoneSources':
            self.QuickSettings.setTabEnabled(2, False)
            self.QuickSettings.setTabEnabled(3, False)
            self.QuickSettings.setTabEnabled(5, False)
            self.menuTransform.setEnabled(False)
            self.o_Sources.setEnabled(False)
            self.o_Sources.setChecked(False)

        # Text panel:
        if self.sources.stextmesh.name == 'NoneText':
            self.o_Text.setEnabled(False)
            self.o_Text.setChecked(False)
            self.grpText.setEnabled(False)

        # Connectivity panel:
        if self.connect.mesh.name == 'NoneConnect':
            self.QuickSettings.setTabEnabled(3, False)
            self.cmapConnect.setEnabled(False)
            self.o_Connect.setEnabled(False)
            self.o_Connect.setChecked(False)
        elif self.connect.colval is not None:
            self.cmapConnect.setEnabled(False)
            self.o_Connect.setEnabled(False)
        self._lw = kwargs.get('c_linewidth', 4.)

        # ---------- Put everything in a root node ----------
        # Here, each object is put in a root node so that each transformation
        # can be applied to all elements.

        # Create a root node :
        self._vbNode = Node(name='visbrain')

        # Make this root node the parent of others Brain objects :
        self.atlas.mesh.parent = self._vbNode
        self.sources.mesh.parent = self._vbNode
        self.connect.mesh.parent = self._vbNode
        self.sources.stextmesh.parent = self._vbNode

        # Add a rescale / translate transformation to the Node :
        self._vbNode.transform = self.atlas.transform
