"""Top level Brain class.

UiInit: initialize the graphical interface
UiElements: interactions between graphical elements and deep functions
base: initialize all Brain objects (MNI, sources, connectivity...)
and associated transformations
BrainUserMethods: initialize functions for user interaction.
"""
import logging

import vispy.scene.cameras as viscam

from .interface import UiInit, UiElements, BrainShortcuts
from .base import BaseVisual, BrainCbar
from .user import BrainUserMethods
from ..pyqt_module import PyQtModule


logger = logging.getLogger('visbrain')


class Brain(PyQtModule, UiInit, UiElements, BaseVisual, BrainCbar,
            BrainUserMethods):
    """Visualization of neuroscientic data on a standard MNI brain.

    Parameters
    ----------
    bgcolor : string/tuple | 'black'
        Background color of the GUI.
    brain_template : string | 'B1'
        The MNI brain template to use. Switch between 'B1', 'B2' or 'B3'
    brain_translucent : bool | True
        Use translucent or opaque brain.
    brain_hemisphere : {'left', 'both', 'right'}
        Specify which brain hemisphere to use. Default is 'both'.
    source_obj : SourceObj | None
        An object (or list of objects) of type source (SourceObj).
    connect_obj : ConnectObj | None
        An object (or list of objects) of type connectivity (ConnectObj).
    time_series_obj : TimeSeriesObj | None
        An object (or list of objects) of type time-series (TimeSeriesObj).
    picture_obj : PictureObj | None
        An object (or list of objects) of type pictures (PictureObj).
    project_radius : float | 10.
        The projection radius to use.
    project_type : {'activity', 'repartition'}
        Define the projection type. Use 'activity' to project the source's
        activity or 'repartition' to get the number of contributing sources per
        vertex.
    project_contribute : bool | False
        Specify if source's can contribute to both hemisphere during projection
        (True) or if it can only be projected on the hemisphere the source
        belong.
    project_mask_color : string/tuple/array_like | 'orange'
        The color to assign to vertex for masked sources.
    project_cmap : string | 'viridis'
        The colormap to use for the source projection.
    project_clim : tuple | (0., 1.)
        Colorbar limits of the projection.
    project_vmin : float | None
        Minimum threshold for the projection colorbar.
    project_under : string/tuple/array_like | 'gray'
        Color to use for values under project_vmin.
    project_vmax : float | None
        Maximum threshold for the projection colorbar.
    project_over : string/tuple/array_like | 'red'
        Color to use for values over project_vmax.
    """

    def __init__(self, bgcolor='black', verbose=None, **kwargs):
        """Init."""
        # ====================== Verbose ======================
        PyQtModule.__init__(self, verbose=verbose, to_describe='_vbNode',
                            icon='brain_icon.svg')
        self._userobj = {}

        # ====================== App creation ======================
        UiInit.__init__(self, bgcolor)  # GUI creation + canvas
        BaseVisual.__init__(self, self.view.wc, self._csGrid, **kwargs)
        UiElements.__init__(self)  # GUI interactions
        self._shpopup.set_shortcuts(self.sh)  # shortcuts dict

        # ====================== Cameras ======================
        # Main camera :
        self.view.wc.camera = self.atlas.camera
        self._vbNode.parent = self.view.wc.scene
        self.atlas.rotate('top')

        # ====================== Colorbar ======================
        # Cbar creation + camera:
        camera = viscam.PanZoomCamera(rect=(-.2, -2.5, 1, 5))
        BrainCbar.__init__(self, camera)
        # Add shortcuts on it :
        BrainShortcuts.__init__(self, self.cbqt.cbviz._canvas)

        self._fcn_on_load()

    def _fcn_on_load(self):
        """Function that need to be executed on load."""
        # Setting panel :
        self._objsPage.setCurrentIndex(0)
        self.menuDispQuickSettings.setChecked(True)
        self._source_tab.setCurrentIndex(0)
        # Progress bar and rotation panel :
        self.progressBar.hide()
        self.userRotationPanel.setVisible(False)
        # Display menu :
        self.menuDispBrain.setChecked(self.atlas.mesh.visible)
        # Objects :
        self._fcn_3dobj_type()
        self._all_object_are_none()
        self._fcn_obj_type()
        # Colorbar :
        self._fcn_menu_disp_cbar()
