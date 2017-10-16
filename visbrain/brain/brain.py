"""Top level Brain class.

UiInit: initialize the graphical interface
UiElements: interactions between graphical elements and deep functions
base: initialize all Brain objects (MNI, sources, connectivity...)
and associated transformations
BrainUserMethods: initialize functions for user interaction.
"""

from PyQt5 import QtWidgets
import sys

import vispy.app as visapp
import vispy.scene.cameras as viscam

from .interface import UiInit, UiElements, BrainShortcuts
from .base import BaseVisual, BrainCbar
from .user import BrainUserMethods
from ..utils import set_widget_size
import sip
sip.setdestroyonexit(False)


class Brain(UiInit, UiElements, BaseVisual, BrainCbar, BrainUserMethods):
    """Visualization of neuroscientic data on a standard MNI brain.

    The *Brain* module include several objects that can be individually
    controlled :

    * **a_** : Atlas properties
    * **s_** : Sources properties
    * **ts_** : Time-series properties
    * **pic_** : Pictures properties
    * **c_** : Connectivity properties
    * **t_** : Transformations properties
    * **ui_** : Graphical User Interface properties
    * **l_** : Light properties

    In addition, some objects provide an extended control of color properties.
    This is the case for source's projection (**s_**), connectivity (**c_**)
    and pictures (**pic_**). Here's the list of color properties for those
    objects :

    * **clim** : a tuple of two floats for the colorbar limits.
    * **cmap** : a string name of a matplotlib colormap.
    * **vmin** : a float for the lower threshold.
    * **under** : a string for color under vmin.
    * **vmax** : a float for the higher threshold.
    * **over** : a string for color over vmax.

    As an example, s_cmap, c_clim and pic_vmin respectively controlled the
    colormap of projected source's activity, the colorbar limits of the
    connectivity and the lower threshold of pictures.

    Parameters
    ----------
    a_color : tuple | (1., 1., 1.)
        RGB colors of the MNI brain (default is white).

    a_opacity : int/float | 1.
        Transparency of the MNI brain. Must be between 0 and 1.

    a_proj : string | {'internal', 'external'}
        Turn a_proj to 'internal' for internal projection or 'external' for
        cortical rendering.

    a_template : string | 'B1'
        The MNI brain template to use. Switch between 'B1', 'B2' or 'B3'

    source_obj : SourceObj | None
        An object (or list of objects) of type source (SourceObj).

    connect_obj : ConnectObj | None
        An object (or list of objects) of type connectivity (ConnectObj).

    time_series_obj : TimeSeriesObj | None
        An object (or list of objects) of type time-series (TimeSeriesObj).

    picture_obj : PictureObj | None
        An object (or list of objects) of type pictures (PictureObj).

    t_radius : float | 10.
        The projection radius to use (depending on coordinates type)

    t_contribute : bool | False
        Specify if source's can contribute to both hemisphere during projection
        (True) or if it can only be projected on the hemisphere the source
        belong.

    ui_bgcolor : string/tuple | (0.09, 0.09, 0.09)
        Background color of the ui

    l_position : tuple | (100., 100., 100.)
        Position of the light

    l_intensity : tuple | (1., 1., 1.)
        Intensity of the light

    l_color : tuple | (1., 1., 1., 1.)
        Color of the light

    l_ambient : float | 0.05
        Coefficient for the ambient light

    l_specular : float | 0.5
        Coefficient for the specular light

    Examples
    --------
    >>> # Load librairies :
    >>> import numpy as np
    >>> from visbrain import Brain
    >>> # Define some coordinates and colors for three deep sources :
    >>> s_xyz = np.array([[-12, -13, 58], [40, 7, 57], [10, 5, 36]])
    >>> s_color = ["#3498db", "#e74c3c", "#2ecc71"]
    >>> # Add data to sources :
    >>> s_data = [100, 0.2, 27]
    >>> # Define a visbrain instance with previous parameters :
    >>> vb = Brain(s_xyz=s_xyz, s_data=s_data, s_color=s_color)
    >>> # Finally, display the interface :
    >>> vb.show()
    """

    def __init__(self, *args, **kwargs):
        """Init."""
        # ====================== ui Arguments ======================
        # Background color (for the main and the colorbar canvas) :
        bgcolor = kwargs.get('ui_bgcolor', (0., 0., 0.))
        # Savename, extension and croping region (usefull for the screenshot) :
        self._savename = kwargs.get('ui_savename', None)
        self._xyzRange = {'turntable': {'x': None, 'y': (-1200, 1200),
                                        'z': None},
                          'fly': {'x': (-120, 120), 'y': (-100, 200),
                                  'z': (-90, 90)},
                          }
        self._userobj = {}

        # ====================== App creation ======================
        # Create the app and initialize all graphical elements :
        self._app = QtWidgets.QApplication(sys.argv)
        UiInit.__init__(self, bgcolor)

        # Set icon :
        # pathfile = sys.modules[__name__].__file__
        # path = os.path.join(*['brain', 'interface', 'gui', 'vbicon.png'])
        # self.setWindowIcon(QtGui.QIcon(os.path.join(pathfile.split(
        #     '/vbrain')[0], path)))

        # ====================== Objects creation ======================
        camera = viscam.TurntableCamera(azimuth=0, distance=1000,
                                        name='turntable')
        BaseVisual.__init__(self, self.view.wc, self._csGrid, self.progressBar,
                            **kwargs)

        # ====================== UI to visbrain ======================
        # Link UI and visbrain function :
        UiElements.__init__(self)
        self._shpopup.set_shortcuts(self.sh)

        # ====================== Cameras ======================
        # Main camera :
        self.view.wc.camera = camera
        self.atlas.mesh.set_camera(self.view.wc.camera)
        self._vbNode.parent = self.view.wc.scene
        self._rotate(fixed='axial')
        self.view.wc.camera.set_default_state()

        # ====================== Colorbar ======================
        # Fixed colorbar camera :
        camera = viscam.PanZoomCamera(rect=(-.2, -2.5, 1, 5))
        # Cbar creation :
        BrainCbar.__init__(self, camera)
        # Add shortcuts on it :
        BrainShortcuts.__init__(self, self.cbqt.cbviz._canvas)

        self._fcn_on_load()

    def _fcn_on_load(self):
        """Function that need to be executed on load."""
        # Setting panel :
        self.q_widget.setVisible(True)
        self.QuickSettings.setCurrentIndex(0)
        self._objsPage.setCurrentIndex(0)
        self.menuDispQuickSettings.setChecked(True)
        self.SettingTab.setCurrentIndex(0)
        set_widget_size(self._app, self.q_widget, 23)
        # Display menu :
        self.menuDispBrain.setChecked(self.atlas.mesh.visible)
        # Objects :
        self._all_object_are_none()
        self._fcn_obj_type()
        # Sources :
        # if self.sources.visible:
        #     self.menuDispSources.setChecked(True)
        # Connectivity :
        # if self.connect.mesh.visible:
        #     self.menuDispConnect.setChecked(True)
        #     self._fcn_menu_disp_connect()
        # Colorbar :
        self._fcn_menu_disp_cbar()

    def show(self):
        """Display the graphical user interface."""
        # This function has to be placed here (and not in the user.py script)
        self.showMaximized()
        # Fix brain range :
        # self._set_cam_range()
        visapp.run()
