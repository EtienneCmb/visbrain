"""Top level Ndviz class."""
import numpy as np

from PyQt5 import QtWidgets
import sys

import vispy.app as visapp
import vispy.scene.cameras as viscam

from .interface import uiInit, uiElements
from .visuals import visuals
from warnings import warn
# from ..utils import id
import sip
sip.setdestroyonexit(False)


class Ndviz(uiInit, visuals, uiElements):
    """Signal visualization tool.

    This class to visualize multi-dimentional array or to inspect single
    signal in several forms (line / markers / histogram / spectrogram / image).

    Parameters
    ----------
    data : array
        The array to plot. It can have any dimension.
    sf : float | 1.
        The sampling frequency
    nd_lw : float | 1.
        Line width of each signal for the Nd-plot.
    nd_title : string | 'Nd-plot'
        Title of the Nd plot.
    nd_xlabel : string | 'X axis'
        Label of the x axis for the Nd plot.
    nd_ylabel : string | 'Y axis'
        Label of the y axis for the Nd plot.
    od_lw : float | 1.
        Line width of each signal for the 1d-plot line.
    on_title : string | '1d-plot'
        Title of the 1d plot.
    od_xlabel : string | 'X axis'
        Label of the x axis for the 1d plot.
    od_ylabel : string | 'Y axis'
        Label of the y axis for the 1d plot.
    ui_bgcolor : string/tuple | (.09, .09, .09)
        Background color of the main canvas.

    Examples
    --------
    >>> import numpy as np
    >>> from visbrain import Ndviz
    >>> y = np.random.rand(1000, 10, 20)
    >>> Ndviz(y).show()
    """

    def __init__(self, data, sf=1, **kwargs):
        """Init."""
        # Be sure to have float arguments :
        if data.dtype != np.float32:
            data = data.astype(np.float32, copy=False)
            warn("Data should be an array of float number. Use "
                 "data.astype(np.float32) before opening the interface.")
        # ====================== ui Arguments ======================
        # Background color (for all of the canvas) :
        bgcolor = kwargs.get('ui_bgcolor', (.09, .09, .09))
        nd_title = kwargs.get('nd_title', 'Nd-plot')
        nd_xlabel = kwargs.get('nd_xlabel', 'X axis')
        nd_ylabel = kwargs.get('nd_ylabel', 'Y axis')
        nd_grid = kwargs.get('nd_grid', False)
        nd_visible = kwargs.get('nd_visible', True)
        od_grid = kwargs.get('od_grid', True)
        od_visible = kwargs.get('od_visible', False)
        od_title = kwargs.get('od_title', '1d-plot')
        od_xlabel = kwargs.get('od_xlabel', 'X axis')
        od_ylabel = kwargs.get('od_ylabel', 'Y axis')
        # Default linewidth :
        self._ndlw = kwargs.get('nd_lw', 2.)
        self._1dlw = kwargs.get('od_lw', 2.)
        self._oridata = np.ascontiguousarray(data)
        self._sf = np.float32(sf)
        # print('ID 0: ', id(self._oridata))
        # Savename, extension and croping region (usefull for the screenshot) :
        self._savename = kwargs.get('ui_savename', None)
        self._extension = kwargs.get('ui_extension', '.png')
        self._crop = kwargs.get('ui_region', None)
        if self._extension not in ['png', 'tiff']:
            self._extension = 'png'

        # ====================== App creation ======================
        # Create the app and initialize all graphical elements :
        self._app = QtWidgets.QApplication(sys.argv)
        uiInit.__init__(self, bgcolor, nd_title, nd_xlabel, nd_ylabel,
                        od_title, od_xlabel, od_ylabel)

        # ====================== Objects creation ======================
        visuals.__init__(self, data, self._sf, **kwargs)

        # ====================== user & GUI interaction  ======================
        # User <-> GUI :
        uiElements.__init__(self)

        # ====================== Cameras ======================
        # Nd-plot camera :
        ndcam = viscam.PanZoomCamera(rect=(-1, -1, 2, 2))
        self._ndplt.mesh.set_camera(ndcam)
        self._ndCanvas.set_camera(ndcam)

        # 1d-plot camera :
        odcam = viscam.PanZoomCamera(rect=self._1dplt.mesh.rect)
        self._1dCanvas.set_camera(odcam)

        # Fixed colorbar camera :
        turntable = viscam.TurntableCamera(interactive=True, azimuth=0,
                                           elevation=90)
        self._cbCanvas.set_camera(turntable)
        self._cbCanvas.wc.camera.set_range(x=(-24, 24), y=(-0.5, 0.5),
                                           margin=0)
        # self._cbCanvas.wc.scene.children[0].parent = None

        # ====================== Visibility ======================
        # Nd-panel :
        self._CanVisNd.setChecked(nd_visible)
        self._NdVizPanel.setVisible(nd_visible)
        self._ndGridTog.setChecked(nd_grid)
        self._ndCanvas.visible_axis(nd_grid)
        # 1d-panel :
        self._CanVis1d.setChecked(od_visible)
        self._1dVizPanel.setVisible(od_visible)
        self._1dGridTog.setChecked(od_grid)
        self._1dCanvas.visible_axis(od_grid)

        # Finally, update each canvas and tab selection :
        self._ndCanvas.canvas.update()
        self._1dCanvas.canvas.update()
        self._fcn_QuickTabSelec()

    def show(self):
        """Display the graphical user interface."""
        # This function has to be placed here (and not in the user.py script)
        self.showMaximized()
        visapp.run()
