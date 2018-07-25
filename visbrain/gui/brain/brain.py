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
from .visuals import Visuals
from .cbar import BrainCbar
from .user import BrainUserMethods
from visbrain._pyqt_module import _PyQtModule
from visbrain.config import PROFILER

logger = logging.getLogger('visbrain')


class Brain(_PyQtModule, UiInit, UiElements, Visuals, BrainCbar,
            BrainUserMethods):
    """Visualization of brain-data on a standard MNI brain.

    By default the Brain module display a standard MNI brain. Then, this brain
    can interact with several objects :

        * Brain (:class:`visbrain.objects.BrainObj`)
        * Sources (:class:`visbrain.objects.SourceObj`)
        * Connectivity (:class:`visbrain.objects.ConnectObj`)
        * Time-series (:class:`visbrain.objects.TimeSeries3DObj`)
        * Pictures (:class:`visbrain.objects.Picture3DObj`)
        * Vectors (:class:`visbrain.objects.VectorObj`)
        * Volume (:class:`visbrain.objects.VolumeObj`)
        * Cross-sections (:class:`visbrain.objects.CrossSecObj`)
        * Region Of Interest (:class:`visbrain.objects.RoiObj`)

    Alternatively, if an other brain template is needed, a brain object
    (BrainObj) can also be used (see brain_obj).

    Parameters
    ----------
    brain_obj : :class:`visbrain.objects.BrainObj` | None
        A brain object.
    vol_obj : :class:`visbrain.objects.VolumeObj` | None
        A volume object.
    cross_sec_obj : :class:`visbrain.objects.CrossSecObj` | None
        A cross-sections object.
    roi_obj : :class:`visbrain.objects.RoiObj` | None
        A Region Of Interest (ROI) object.
    source_obj : :class:`visbrain.objects.SourceObj` | None
        An object (or list of objects) of type source.
    connect_obj : :class:`visbrain.objects.ConnectObj` | None
        An object (or list of objects) of type connectivity.
    time_series_obj : :class:`visbrain.objects.TimeSeries3DObj` | None
        An object (or list of objects) of type time-series.
    picture_obj : :class:`visbrain.objects.Picture3DObj` | None
        An object (or list of objects) of type pictures.
    vector_obj : :class:`visbrain.objects.VectorObj` | None
        An object (or list of objects) of type vector.
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
    bgcolor : string/tuple | 'black'
        Background color of the GUI.
    """

    def __init__(self, bgcolor='black', verbose=None, **kwargs):
        """Init."""
        # ====================== PyQt creation ======================
        _PyQtModule.__init__(self, verbose=verbose, to_describe='view.wc',
                             icon='brain_icon.svg')
        self._userobj = {}
        self._gl_scale = 100.  # fix appearance for small meshes
        self._camera = viscam.TurntableCamera(name='MainBrainCamera')

        # ====================== Canvas creation ======================
        UiInit.__init__(self, bgcolor)  # GUI creation + canvas
        PROFILER("Canvas creation")

        # ====================== App creation ======================
        PROFILER("Visual elements", as_type='title')
        Visuals.__init__(self, self.view.wc, **kwargs)

        # ====================== Ui interactions ======================
        UiElements.__init__(self)  # GUI interactions
        PROFILER("Ui interactions")
        self._shpopup.set_shortcuts(self.sh)  # shortcuts dict

        # ====================== Cameras ======================
        # Main camera :
        self.view.wc.camera = self._camera
        self._vbNode.parent = self.view.wc.scene
        self.atlas.camera = self._camera
        self.roi.camera = self._camera
        self.atlas._csize = self.view.canvas.size
        self.atlas.rotate('top')
        self.atlas.camera.set_default_state()
        PROFILER("Cameras creation")

        # ====================== Colorbar ======================
        camera = viscam.PanZoomCamera(rect=(-.2, -2.5, 1, 5))
        BrainCbar.__init__(self, camera)
        PROFILER("Colorbar and panzoom creation")
        self.background_color(bgcolor)

        # ====================== Shortcuts ======================
        BrainShortcuts.__init__(self, self.cbqt.cbviz._canvas)
        PROFILER("Set brain shortcuts")

        self._fcn_on_load()
        PROFILER("Functions on load")

    def _fcn_on_load(self):
        """Function that need to be executed on load."""
        # Setting panel :
        self._objsPage.setCurrentIndex(0)
        self.menuDispQuickSettings.setChecked(True)
        self._source_tab.setCurrentIndex(0)
        self._obj_type_lst.setCurrentIndex(0)
        # Progress bar and rotation panel :
        self.progressBar.hide()
        self.userRotationPanel.setVisible(False)
        # Display menu :
        self.menuDispBrain.setChecked(self.atlas.mesh.visible)
        # Objects :
        self._fcn_obj_type()
        # Colorbar :
        self._fcn_menu_disp_cbar()
