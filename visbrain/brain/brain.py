"""Top level Brain class.

uiInit: initialize the graphical interface
uiElements: interactions between graphical elements and deep functions
base: initialize all Brain objects (MNI, sources, connectivity...)
and associated transformations
BrainUserMethods: initialize functions for user interaction.
"""

from PyQt5 import QtWidgets
import sys

import vispy.app as visapp
import vispy.scene.cameras as viscam

from .interface import uiInit, uiElements
from .interface.uiInit import BrainShortcuts
from .base import base, BrainCbar
from .user import BrainUserMethods
from ..utils import set_widget_size
import sip
sip.setdestroyonexit(False)


class Brain(uiInit, uiElements, base, BrainCbar, BrainUserMethods):
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

    s_xyz : array_like | None
        Array of talairach or MNI coordinates to display sources
        into the brain. The shape of the array must be (N, 3) where
        '3' is for (x, y, z) coordinates and N, the number of sources.

    s_data : array_like | None
        Add some data to sources. As a consequence, the radius of each
        source will be a function of s_data. must be an array of shape
        (N,). If s_data is None, all sources will have the same value.
        The parameter s_data can be masked using numpy.ma module.

    s_system : string | 'mni'
        Specify the coordinate system. Use either 'mni' (MNI) or 'tal'
        (Talairach).

    s_color : string/list/array_like | 'red'
        Color of each source sphere. If s_color is a single string,
        all sphere will have the same color. If it's' a list of strings,
        the length must be N. Alternatively, s_color can be a (N, 3) RGB
        or (N, 4) RGBA colors.

    s_alpha : int/float | 1.0
        Transparency of all sources. Must be between 0 and 1.

    s_radiusmin / s_radiusmax : float | 5.0/10.0
        Define the minimum and maximum source's possible radius. By default
        if all sources have the same value, the radius will be s_radiusmin.

    s_edgecolor : string/list/array_like | None
        Add an edge to sources

    s_edgewidth : float | 0.4
        Edge width of sources

    s_scaling : bool | True
        If set to True, marker scales when zooming.

    s_symbol : string | 'disc'
        Symbol to use for sources. Allowed style strings are: disc, arrow,
        ring, clobber, square, diamond, vbar, hbar, cross, tailed_arrow, x,
        triangle_up, triangle_down, and star.

    s_text : list/tuple | None
        Set text to each electrode. s_text should be an iterable object,
        composed of strings, with the same length as the number of sources.

    s_textcolor : string/list/array_like | 'k'
        A single color element for all the text

    s_textsize : int | 3
        Font size of text elements

    s_textshift : list/tuple | (0,1,0)
        Translate the text along (x, y, z) coordinates to improve text
        visibility

    s_projecton : string | 'surface'
        Project sources activity either on surface or, if displayed,
        on deep structures.

    s_mask : array_like | None
        Vector of boolean values, with the same length as the length of
        s_xyz. Use this parameter to mask some sources but keep it
        displayed.

    s_maskcolor : list/tuple | 'gray'
        Color of masked sources when projected on surface.

    ts_data : array_like | None
        Array of data for the time-series. This array must have a shape of
        (n_sources, n_time_points).

    ts_select : array_like | None
        Array of boolean values to specify which time-series to hide or to
        display.

    ts_color : string/list/tuple/array_like | 'white'
        Color of the time-series.

    ts_amp : float | 6.
        Graphical amplitude of the time-series.

    ts_width : float | 20.
        Graphical width of th time-series.

    ts_lw : float | 1.5
        Line width of the time-series.

    ts_dxyz : tuple | (0., 0., 1.)
        Offset along the (x, y, z) axis for the time-series.

    pic_data : array_like | None
        Array of picture data. Must have a shape of (n_sources, n_rows, n_cols)

    pic_width : float | 7.
        Width of each picture.

    pic_height : float | 7.
        Height of each picture.

    pic_dxyz : float | (0., 0., 1.)
        Offset along the (x, y, z) axis for the pictures.

    c_connect : array_like | None
        Connections between sources. Define N sources location using s_xyz
        of shape (N, 3). Then, c_connect must be a (N, N) array defining
        each value of connection between all sources. The diagonal is going
        to be systematically ignored.

    c_select : array_like | None
        Select relevant connections do display. This array should be
        composed of 0 and 1 and must have the same shape as c_connect.
        Alternatively, set a mask to c_connect to have the same effect
        without using this parameter.

    c_colorby : string | 'strength'
        Define how to color connexions. Use 'strength' if the color has to
        be modulate by the connectivity strength. Use 'count' if the
        color depends on the number of connexions per node. Use 'density'
        to define colors according to the number of line in a sphere of
        radius c_dradius.

    c_dynamic : tuple | None
        Control the dynamic opacity. For example, if c_dynamic=(0, 1),
        strong connections will be more opaque than weak connections.

    c_dradius : float | 30.
        Radius for the density color line method.

    c_colval : dict | None
        Define colors for a specifics values. For example, c_colval=
        {1.5: 'red', 2.1: 'blue'} every connexions equal to 1.5 are going
        to be red and blue for 2.1. Use np.nan: 'gray' in order to define
        the color of all connexions that are not in the dictionary
        otherwise they are going to be ignored.

    c_linewidth : float | 3.0
        Line width of connectivity lines.

    t_radius : float | 10.
        The projection radius to use (depending on coordinates type)

    t_contribute : bool | False
        Specify if source's can contribute to both hemisphere during projection
        (True) or if it can only be projected on the hemisphere the source
        belong.

    ui_bgcolor : string/tuple | (0.09, 0.09, 0.09)
        Background color of the ui

    ui_savename : string | None
        The save name when exporting

    ui_region : tuple | None
        Crop the exportation of the main canvas to the region define by
        (x, y, width, height).

    ui_autocrop : bool | True
        Automatically crop figures when saving.

    ui_resolution : float | 3000
        Define the screenshot resolution by indicating the number of times
        the definition of your screen must be multiplied.

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

    Methods
    -------
    show()
        Display the graphical user interface.
    quit()
        Quit the interface.
    rotate()
        Rotate the scene elements using a predefined or a custom rotation.
    background_color()
        Set the background color of the main canvas and the colorbar.
    screenshot()
        Take a screenshot of the current scene and save it as a picture.
    load_config()
        Load a configuration file.
    save_config()
        Save a configuration file.
    brain_control()
        Control the type of brain to use.
    brain_list()
        Get the list of available mesh brain templates.
    add_mesh()
        Add a mesh to the scene.
    add_volume()
        Add a new volume to the interface.
    volume_list()
        Get the list of volumes available.
    cross_sections_control()
        Set the cross-section position.
    sources_control()
        Set data to sources and control source's properties.
    sources_opacity()
        Set the level of transparency of sources.
    sources_display()
        Select sources to display.
    cortical_projection()
        Project sources activity.
    cortical_repartition()
        Get the number of contributing sources per vertex.
    sources_colormap()
        Change the colormap of cortical projection / repartition.
    sources_fit()
        Force sources coordinates to fit to a selected object.
    sources_to_convex_hull()
        Convert a set of sources into a convex hull.
    add_sources()
        Add a supplementar source's object.
    time_series_control()
        Control time-series settings.
    add_time_series()
        Add time-series (TS) object.
    pictures_control()
        Control pictures settings.
    add_pictures()
        Add pictures object.
    connect_control()
        Update connectivity object.
    add_connect()
        Add a supplementar connectivity object.
    roi_control()
        Select Region Of Interest (ROI) to plot.
    roi_light_reflection()
        Change how light is reflecting onto roi.
    roi_opacity()
        Set the level of transparency of the deep structures.
    roi_list()
        Get the list of supported ROI.
    cbar_control()
        Control the colorbar of a specific object.
    cbar_select()
        Select and disply a colorbar.
    cbar_list()
        Get the list of objects for which the colorbar can be controlled.
    cbar_autoscale()
        Autoscale the colorbar to the best limits.
    cbar_export()
        Export colorbars in a text file or in a dictionary.
    """

    def __init__(self, *args, **kwargs):
        """Init."""
        # ====================== ui Arguments ======================
        # Background color (for the main and the colorbar canvas) :
        bgcolor = kwargs.get('ui_bgcolor', (0., 0., 0.))
        # Savename, extension and croping region (usefull for the screenshot) :
        self._savename = kwargs.get('ui_savename', None)
        self._crop = kwargs.get('ui_region', None)
        self._autocrop = kwargs.get('ui_autocrop', True)
        self._uirez = kwargs.get('ui_resolution', 3000.)
        self._xyzRange = {'turntable': {'x': None, 'y': (-1200, 1200),
                                        'z': None},
                          'fly': {'x': (-120, 120), 'y': (-100, 200),
                                  'z': (-90, 90)},
                          }
        self._cbarexport = True
        self._userobj = {}

        # ====================== App creation ======================
        # Create the app and initialize all graphical elements :
        self._app = QtWidgets.QApplication(sys.argv)
        uiInit.__init__(self, bgcolor)

        # Set icon :
        # pathfile = sys.modules[__name__].__file__
        # path = os.path.join(*['brain', 'interface', 'gui', 'vbicon.png'])
        # self.setWindowIcon(QtGui.QIcon(os.path.join(pathfile.split(
        #     '/vbrain')[0], path)))

        # ====================== Objects creation ======================
        camera = viscam.TurntableCamera(azimuth=0, distance=1000,
                                        name='turntable')
        base.__init__(self, self.view.wc, self._csGrid, self.progressBar,
                      **kwargs)

        # ====================== UI to visbrain ======================
        # Link UI and visbrain function :
        uiElements.__init__(self)
        self._shpopup.set_shortcuts(self.sh)

        # ====================== Cameras ======================
        # Main camera :
        self.view.wc.camera = camera
        self.atlas.mesh.set_camera(self.view.wc.camera)
        self.pic.set_camera(self.view.wc.camera)
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
        # Sources :
        if self.sources.mesh.visible:
            self.menuDispSources.setChecked(True)
        # Connectivity :
        if self.connect.mesh.visible:
            self.menuDispConnect.setChecked(True)
            self._fcn_menuConnect()
        # Colorbar :
        self._fcn_menuCbar()

    def show(self):
        """Display the graphical user interface."""
        # This function has to be placed here (and not in the user.py script)
        self.showMaximized()
        # Fix brain range :
        # self._set_cam_range()
        visapp.run()
