"""Top level vbrain class.
uiInit: initialize the graphical interface
uiElements: interactions between graphical elements and deep functions
vbobj: initialize all vbrain objects (MNI, sources, connectivity...)
and associated transformations
"""

from PyQt4 import QtGui
import sys
import os

from vispy import io, app
import vispy.app as visapp
import vispy.scene.cameras as viscam

from .interface import uiInit, uiElements
from .vbobj import vbobj

import visbrain



class vbrain(uiInit, uiElements, vbobj):

    """
    All possible colors can be a matplotlib color name (*'olive', 'slateblue'...*),
    an hexadecimal type (*'#9b59b6', '#3498db', '#95a5a6'...*) or an array of RGB or
    RGBA colors. 

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
            Specify an alternativ surface to use. Both parameters must be a 2D array,
            respectively of shapes (N_vertices, 3) and (N_faces, 3)

        a_shading: string, (def: 'smooth')
            Shading method to use for the brain. Switch between 'smooth', 'flat' or None

        s_xyz: ndarray, (def: None)
            Array of talairach or MNI coordinates to display sources
            into the brain. The shape of the array must be (N, 3) where
            '3' is for (x, y, z) coordinates and N, the number of sources.

        s_data: ndarray, (def, None)
            Add some data to sources. As a consequence, the radius of each
            source will be a function of s_data. must be an array of shape
            (N,). If s_data is None, all sources will have the same value. The parameter
            s_data can be masked using numpy.ma module.

        s_color: string/list/ndarray, (def: 'red')
            Color of each source sphere. If s_color is a single string,
            all sphere will have the same color. If it's' a list of strings,
            the length must be N. Alternatively, s_color can be a (N, 3) RGB
            or (N, 4) RGBA colors.

        s_alpha: int/float, (def: 1.0)
            Transparency of all sources. Must be between 0 and 1.

        s_radiusmin/s_radiusmax: int/float, (def: 5.0/10.0)
            Define the minimum and maximum source's possible radius. By default,
            if all sources have the same value, the radius will be s_radiusmin.

        s_edgecolor: string/list/ndarray, (def: None)
            Add an edge to sources

        s_edgewidth: float, (def: 0.4)
            Edge width of sources

        s_scaling: bool, (def: True)
            If s_render is 'marker', control if sources have to be scaled when zooming
            or not.

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
            Vector of boolean values, with the same length as the length of s_xyz.
            Use this parameter to mask some sources but keep it displayed.

        s_maskcolor: list/tuple, optional, (def: 'gray')
            Color of masked sources when projected on surface.

        c_connect: ndarray, (def: None)
            Connections between sources. Define N sources location using s_xyz of
            shape (N, 3). Then, c_connect must be a (N, N) array defining each value of
            connection between all sources. The diagonal is going to be systematically ignored.

        c_select: ndarray, (def: None)
            Select relevant connections do display. This array should be composed of 0 and 1
            and must have the same shape as c_connect. Alternatively, set a mask to c_connect
            to have the same effect without using this parameter.

        c_dynamic: tuple, optional, (def: None)
            Control the dynamic opacity. For example, if c_dynamic=(0, 1),
            strong connections will be more opaque than weak connections.

        c_linewidth: float, optional, (def: 4.0)
            Linewidth of connectivity lines.

        cmap: string, (def: 'inferno')
            Matplotlib colormap name.

        cmap_lim: tuple/list, (def: None)
            Define the limit of the colorbar. This parameter must be a list or tuple
            containing two float (like (3, 5)...). If cmap_lim stay to None, the minimum
            and maximum of projected values are going to be used. Alternatively, you can
            use (3, None) or (None, 5) to ignore one value and force it to be assigned to
            the minimum or maximum.

        cmap_vmin/cmap_vmax: int/float, (def: None/None)
            Define a threshold to change colors that are under cmap_vmin or over
            cmap_vmax. See cmap_under/cmap_over to change those colors.

        cmap_under/cmap_over: string/tuple, (def: None/None)
            The color to use for values under cmap_vmin and values over cmap_vmax.

        t_radius: int/float, (def: 10)
            The projection radius to use (depending on coordinates type)

        ui_bgcolor: string/tuple, (def: (0.09, 0.09, 0.09))
            Backgroud color of the ui

        ui_savename: string, optional, (def: None)
            The save name when exporting

        ui_extension: string, optional, (def: '.png')
            The picture extension when exporting. Choose between 'png'
            and 'tiff'

        ui_crop: tuple, optional, (def: None)
            crop the exportation. Must be  (x, y, width, height)

        cb_export: bool, optional, (def: True)
            Control if the colorbor must be exported when doing a screenshot

        cb_fontsize: int, optional, (def: 15)
            The fontsize of colorbar indications

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
        >>> from visbrain import vbrain 
        >>> # Define some coordinates and colors for three deep sources :
        >>> s_xyz = np.array([[-12, -13, 58], [40, 7, 57], [10, 5, 36]])
        >>> s_color = ["#3498db", "#e74c3c", "#2ecc71"]
        >>> # Add data to sources :
        >>> s_data = [100, 0.2, 27]
        >>> # Define a visbrain instance with previous parameters :
        >>> vb = vbrain(s_xyz=s_xyz, s_data=s_data, s_color=s_color)
        >>> # Finally, display the interface :
        >>> vb.show()
    """
    def __init__(self, *args, **kwargs):

        # ------ ui Arguments ------
        bgcolor = kwargs.get('ui_bgcolor', (0.09, 0.09, 0.09))
        self._savename = kwargs.get('ui_savename', None)
        self._extension = kwargs.get('ui_extension', '.png')
        self._crop = kwargs.get('ui_crop', None)
        if self._extension not in ['png', 'tiff']:
            self._extension = 'png'

        # ------ App creation ------
        # Create the app and initialize all graphical elements :
        self._app = QtGui.QApplication(sys.argv)
        uiInit.__init__(self, bgcolor)

        # Set icon :
        iconpath = os.path.join(os.path.dirname(visbrain.__file__), 'vbrain/interface/gui/vbicon.png')
        self.setWindowIcon(QtGui.QIcon(iconpath))

        # ------ Objects creation ------
        camera = viscam.TurntableCamera(azimuth=0, distance=1000)
        vbobj.__init__(self, self.view.wc, self.progressBar, **kwargs)

        # ------ UI to visbrain ------
        # Link UI and visbrain function :
        uiElements.__init__(self)

        # # ------ Cameras ------
        # # Main camera :
        self.view.wc.camera = camera
        self.atlas.mesh.set_camera(self.view.wc.camera)
        self._vbNode.parent = self.view.wc.scene

        # # Fixed colorbar camera :
        self.view.cbwc.camera = viscam.TurntableCamera(interactive=True, azimuth=0, elevation=90)
        self.view.cbwc.camera.set_range(x=(-24,24), y=(-0.5,0.5), margin=0)
        self.view.wc.scene.children[0].parent = None
        
        
        # print(self.view.wc.scene.describe_tree(with_transform=True))

    def show(self):
        """Display the graphical user interface
        """
        self.showMaximized()
        self.rotate()
        visapp.run()
