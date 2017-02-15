"""Top level vbrain class.

uiInit: initialize the graphical interface
uiElements: interactions between graphical elements and deep functions
base: initialize all vbrain objects (MNI, sources, connectivity...)
and associated transformations
userfcn: initialize functions for user interaction.
"""
import numpy as np

from PyQt4 import QtGui
import sys

import vispy.app as visapp
import vispy.scene.cameras as viscam

from .interface import uiInit, uiElements
from .visuals import visuals
from ..utils import id
from warnings import warn
# from .user import userfcn


class Ndviz(uiInit, visuals, uiElements):
    """Visualization of nd-signals.

    Args:
        data: array
            The array to plot. It can have any dimension.

        sf: float
            The sampling frequency

    Kargs:
        nd_title: string, optional, (def: 'Nd-plot')
            Title of the Nd plot.

        nd_xlabel: string, optional, (def: 'X axis')
            Label of the x axis for the Nd plot.

        nd_ylabel: string, optional, (def: 'Y axis')
            Label of the y axis for the Nd plot.

        on_title: string, optional, (def: '1d-plot')
            Title of the 1d plot.

        od_xlabel: string, optional, (def: 'X axis')
            Label of the x axis for the 1d plot.

        od_ylabel: string, optional, (def: 'Y axis')
            Label of the y axis for the 1d plot.

        ui_bgcolor: string/tuple, optional, (def: (.09, .09, .09))
            Background color of the main canvas.

        lw: float, optional, (def: 1.)
            Line width of each signal.
    """

    def __init__(self, data, sf, *args, **kwargs):
        """Init."""
        # Be sure to have float arguments :
        if data.dtype != np.float32:
            data = data.astype(np.float32, copy=False)
            warn("Data should be an array of float number. Use "
                 "data.astype(np.float32) before opening the interface.")
        # ====================== ui Arguments ======================
        # Background color (for all of the canvas) :
        bgcolor = kwargs.get('ui_bgcolor', (0.09, 0.09, 0.09))
        nd_title = kwargs.get('nd_title', 'Nd-plot')
        nd_xlabel = kwargs.get('nd_xlabel', 'X axis')
        nd_ylabel = kwargs.get('nd_ylabel', 'Y axis')
        od_title = kwargs.get('od_title', '1d-plot')
        od_xlabel = kwargs.get('od_xlabel', 'X axis')
        od_ylabel = kwargs.get('od_ylabel', 'Y axis')
        # Default linewidth :
        self._lw = kwargs.get('lw', 1.)
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
        self._app = QtGui.QApplication(sys.argv)
        uiInit.__init__(self, bgcolor, nd_title, nd_xlabel, nd_ylabel,
                        od_title, od_xlabel, od_ylabel)

        # ====================== Objects creation ======================
        visuals.__init__(self, data, sf, **kwargs)

        # ====================== user & GUI interaction  ======================
        # User <-> GUI :
        uiElements.__init__(self)

        # ====================== Cameras ======================
        # Nd-plot camera :
        ndcam = viscam.PanZoomCamera(rect=(-1, -1, 2, 2))
        self._ndplt.mesh.set_camera(ndcam)
        self._ndCanvas.set_camera(ndcam)
        self._ndCanvas.visible_axis(False)

        # 1d-plot camera :
        odcam = viscam.PanZoomCamera(rect=self._1dplt.mesh.rect)
        self._1dCanvas.set_camera(odcam)

        # Image-plot camera :
        # imcam = viscam.PanZoomCamera(rect=self._1dplt.rect)
        # self._imCanvas.set_camera(imcam)

        # Fixed colorbar camera :
        turntable = viscam.TurntableCamera(interactive=True, azimuth=0,
                                           elevation=90)
        self._cbCanvas.set_camera(turntable)
        self._cbCanvas.wc.camera.set_range(x=(-24, 24), y=(-0.5, 0.5),
                                           margin=0)
        # self._cbCanvas.wc.scene.children[0].parent = None

        ################################################################
        self._NdVizPanel.setVisible(True)
        self._1dVizPanel.setVisible(False)
        self._1dCanvas.visible_axis(False)
        self.q_widget.setVisible(True)
        ################################################################

        # Finally, update each canvas and tab selection :
        self._ndCanvas.canvas.update()
        self._1dCanvas.canvas.update()
        self._fcn_tabSelection()

    def show(self):
        """Display the graphical user interface."""
        # This function has to be placed here (and not in the user.py script)
        self.showMaximized()
        visapp.run()
