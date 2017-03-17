"""Top level Brain class.

uiInit: initialize the graphical interface
uiElements: interactions between graphical elements and deep functions
base: initialize all Brain objects (MNI, sources, connectivity...)
and associated transformations
userfcn: initialize functions for user interaction.
"""

from PyQt4 import QtGui
import sys
import os

import vispy.app as visapp
import vispy.scene.cameras as viscam

from .interface import uiInit, uiElements
from .base import base
from .user import userfcn


class Brain(uiInit, uiElements, base, userfcn):
    """Visualization of neuroscientic data on a standard MNI brain.

    Kargs:
        a_color: tuple, (def: (1,1,1))
            RGB colors of the MNI brain.

        a_opacity: int/float, (def: 1.)
            Transparency of the MNI brain. Must be between 0 and 1.

        a_proj: string, (def: 'internal')
            Turn a_proj to 'internal' for internal projection or 'external' for
            cortical rendering.

        a_template: string, (def: 'B1')
            The MNI brain template to use. Switch between 'B1', 'B2' or 'B3'

        a_vertices/a_faces: ndarray, (def: None)
            Specify an alternativ surface to use. Both parameters must be a 2D
            array, respectively of shapes (N_vertices, 3) and (N_faces, 3)

        a_shading: string, (def: 'smooth')
            Shading method to use for the brain. Switch between 'smooth',
            'flat' or None.

        s_xyz: ndarray, (def: None)
            Array of talairach or MNI coordinates to display sources
            into the brain. The shape of the array must be (N, 3) where
            '3' is for (x, y, z) coordinates and N, the number of sources.

        s_data: ndarray, (def, None)
            Add some data to sources. As a consequence, the radius of each
            source will be a function of s_data. must be an array of shape
            (N,). If s_data is None, all sources will have the same value.
            The parameter s_data can be masked using numpy.ma module.

        s_color: string/list/ndarray, (def: 'red')
            Color of each source sphere. If s_color is a single string,
            all sphere will have the same color. If it's' a list of strings,
            the length must be N. Alternatively, s_color can be a (N, 3) RGB
            or (N, 4) RGBA colors.

        s_alpha: int/float, (def: 1.0)
            Transparency of all sources. Must be between 0 and 1.

        s_radiusmin/s_radiusmax: int/float, (def: 5.0/10.0)
            Define the minimum and maximum source's possible radius. By default
            if all sources have the same value, the radius will be s_radiusmin.

        s_edgecolor: string/list/ndarray, (def: None)
            Add an edge to sources

        s_edgewidth: float, (def: 0.4)
            Edge width of sources

        s_scaling: bool, (def: True)
            If set to True, marker scales when rezooming.

        s_symbol: string, (def: 'disc')
            Symbol to use for sources. Allowed style strings are: disc, arrow,
            ring, clobber, square, diamond, vbar, hbar, cross, tailed_arrow, x,
            triangle_up, triangle_down, and star.

        s_text: list/tuple, (def: None)
            Set text to each electrode. s_text should be an iterable object,
            composed of strings, with the same length as the number of sources.

        s_textcolor: string/list/ndarray, (def: 'k')
            A single color element for all the text

        s_textsize: int, (def: 3)
            Fontsize of text elements

        s_textshift: list/tuple, (def: (0,1,0))
            Translate the text along (x, y, z) coordinates to improve text
            visibility

        s_projecton: string, optional, (def: 'surface')
            Project sources activity either on surface or, if displayed,
            on deep structures.

        s_mask: ndarray, optional, (def: None)
            Vector of boolean values, with the same length as the length of
            s_xyz. Use this parameter to mask some sources but keep it
            displayed.

        s_maskcolor: list/tuple, optional, (def: 'gray')
            Color of masked sources when projected on surface.

        c_connect: ndarray, (def: None)
            Connections between sources. Define N sources location using s_xyz
            of shape (N, 3). Then, c_connect must be a (N, N) array defining
            each value of connection between all sources. The diagonal is going
            to be systematically ignored.

        c_select: ndarray, (def: None)
            Select relevant connections do display. This array should be
            composed of 0 and 1 and must have the same shape as c_connect.
            Alternatively, set a mask to c_connect to have the same effect
            without using this parameter.

        c_dynamic: tuple, optional, (def: None)
            Control the dynamic opacity. For example, if c_dynamic=(0, 1),
            strong connections will be more opaque than weak connections.

        c_linewidth: float, optional, (def: 4.0)
            Linewidth of connectivity lines.

        cmap: string, (def: 'inferno')
            Matplotlib colormap name.

        cmap_lim: tuple/list, (def: None)
            Define the limit of the colorbar. This parameter must be a list or
            tuple containing two float (like (3, 5)...). If cmap_lim stay to
            None, the minimum and maximum of projected values are going to be
            used. Alternatively, you can use (3, None) or (None, 5) to ignore
            one value and force it to be assigned to the minimum or maximum.

        cmap_vmin/cmap_vmax: int/float, (def: None/None)
            Define a threshold to change colors that are under cmap_vmin or
            over cmap_vmax. See cmap_under/cmap_over to change those colors.

        cmap_under/cmap_over: string/tuple, (def: None/None)
            The color to use for values under cmap_vmin and values over
            cmap_vmax.

        t_radius: int/float, (def: 10)
            The projection radius to use (depending on coordinates type)

        ui_bgcolor: string/tuple, (def: (0.09, 0.09, 0.09))
            Backgroud color of the ui

        ui_savename: string, optional, (def: None)
            The save name when exporting

        ui_region: tuple, optional, (def: None)
            Crop the exportation of the main canvas to the region define by
            (x, y, width, height).

        ui_cbregion: tuple, optional, (def: None)
            Crop the exportation of the colorbar canvas to the region define by
            (x, y, width, height).

        ui_resolution: float, optional, (def: 3000)
            Define the screenshot resolution by indicating the number of times
            the definition of your screen must be multiplied.

        cb_export: bool, optional, (def: True)
            Control if the colorbor must be exported when doing a screenshot

        cb_fontsize: int, optional, (def: 15)
            Font-size of colorbar text (min / max / title)

        cb_fontcolor: string, optional, (def: 'white')
            Font-color of colorbar text (min / max / title)

        l_position: tuple, optional, (def: (100., 100., 100.))
            Position of the light

        l_intensity: tuple, optional, (def: (1., 1., 1.))
            Intensity of the light

        l_color: tuple, optional, (def: (1., 1., 1., 1.))
            Color of the light

        l_coefAmbient: float, optional, (def: 0.05)
            Coefficient for the ambient light

        l_coefSpecular: float, optional, (def: 0.5)
            Coefficient for the specular light

    Example:
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
        bgcolor = kwargs.get('ui_bgcolor', (0.098, 0.098, 0.098))
        # Savename, extension and croping region (usefull for the screenshot) :
        self._savename = kwargs.get('ui_savename', None)
        self._crop = kwargs.get('ui_region', None)
        self._cbcrop = kwargs.get('ui_cbregion', None)
        self._uirez = kwargs.get('ui_resolution', 3000.)
        self._xRange = (-70, 70)
        self._yRange = (-70, 70)
        self._zRange = (-90, 90)

        # ====================== App creation ======================
        # Create the app and initialize all graphical elements :
        self._app = QtGui.QApplication(sys.argv)
        uiInit.__init__(self, bgcolor)

        # Set icon :
        pathfile = sys.modules[__name__].__file__
        path = os.path.join(*['brain', 'interface', 'gui', 'vbicon.png'])
        self.setWindowIcon(QtGui.QIcon(os.path.join(pathfile.split(
                                                        '/vbrain')[0], path)))

        # ====================== Objects creation ======================
        camera = viscam.TurntableCamera(azimuth=0, distance=1000,
                                        name='turntable')
        base.__init__(self, self.view.wc, self.progressBar, **kwargs)

        # ====================== UI to visbrain ======================
        # Link UI and visbrain function :
        uiElements.__init__(self)

        # # ====================== Cameras ======================
        # # Main camera :
        self.view.wc.camera = camera
        self.atlas.mesh.set_camera(self.view.wc.camera)
        self._vbNode.parent = self.view.wc.scene

        # Fixed colorbar camera :
        self.view.cbwc.camera = viscam.TurntableCamera(interactive=True,
                                                       azimuth=0, elevation=90)
        self.view.cbwc.camera.set_range(x=(-24, 24), y=(-0.5, 0.5), margin=0)
        self.view.wc.scene.children[0].parent = None
        self._rotate(fixed='axial')

        # print(self.view.wc.scene.describe_tree(with_transform=True))

    def show(self):
        """Display the graphical user interface."""
        # This function has to be placed here (and not in the user.py script)
        self.showMaximized()
        # Fix brain range :
        self._set_cam_range()
        visapp.run()
