from PyQt4 import QtGui
import sys

from vispy import io, app
import vispy.app as visapp
import vispy.scene.cameras as viscam

from .interface import uiInit, uiElements
from .elements import elements


 
class vbrain(uiInit, uiElements, elements):

    """
    All possible colors can be a matplotlib color name ('olive', 'slateblue'...),
    an hexadecimal type ('#9b59b6', '#3498db', '#95a5a6'...) or an array of RGB or
    RGBA colors.
    's_': sources options
    'a_': atlas options
    'c_': connectivity options
    't_': transformations options
    'cmap_': colormap options
    'cb_': colorbar
    'ui_': graphical interface options

    Kargs:
        a_color: tuple, (def: (1,1,1))
            RGB colors of the MNI brain.

        a_opacity: int/float, (def: 0.1)
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

        c_connect: ndarray, (def: None)
            Connections between sources. Define N sources location using s_xyz of
            shape (N, 3). Then, c_connect must be a (N, N) array defining each value of
            connection between all sources. The diagonal is going to be systematically ignored.

        c_select: ndarray, (def: None)
            Select relevant connections do display. This array should be composed of 0 and 1
            and must have the same shape as c_connect. Alternatively, set a mask to c_connect
            to have the same effect without using this parameter.

        cmap: string, (def: 'inferno')
            Matplotlib colormap name.

        cmap_vmin/cmap_vmax: int/float, (def: None/None)
            Minimum/maximum values for the colormap.

        cmap_under/cmap_over: string/tuple, (def: None/None)
            The color to use for values under cmap_vmin and values over cmap_vmax.

        t_radius: int/float, (def: 10)
            The projection radius to use (depending on coordinates type)

        t_transform: vispy transformation, (def: None)
            Define and set a transformation to all displayed elements. This can be
            usefull to adapt a user template to visbrain.

        ui_bgcolor: string/tuple, (def: (0.09, 0.09, 0.09))
            Backgroud color of the ui

    Example:
        >>> # Load lirairies :
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

        # ------ App creation ------
        # Create the app and initialize all graphical elements :
        self._app = QtGui.QApplication(sys.argv)
        uiInit.__init__(self, kwargs.get('ui_bgcolor', (0.09, 0.09, 0.09)))

        # # ------ Objects creation ------
        elements.__init__(self, self.view.wc, self.progressBar, **kwargs)

        # ------ UI to visbrain ------
        # Link UI and visbrain function :
        uiElements.__init__(self)

        # # ------ Cameras ------
        # # Main camera :
        self.view.wc.camera = viscam.TurntableCamera(azimuth=90, elevation=90)
        self._vbNode.parent = self.view.wc.scene

        # # Fixed colorbar camera :
        self.view.cbwc.camera = viscam.TurntableCamera(interactive=True, azimuth=0, elevation=90)
        self.view.cbwc.camera.set_range(x=(-24,24), y=(-0.5,0.5), margin=0)
        self.view.wc.scene.children[0].parent = None
        
        # print(self.view.wc.scene.describe_tree(with_transform=True))

    def show(self):
        self.showMaximized()
        self.rotate_fixed()
        visapp.run()