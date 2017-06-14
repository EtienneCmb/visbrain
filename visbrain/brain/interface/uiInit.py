"""This script group the diffrent graphical components.

Grouped components :
    * PyQt elements (window, Pyqt functions...)
    * Vispy canvas functions
    * User shortcuts
"""

from PyQt5 import QtWidgets
from vispy import app

from .gui import Ui_MainWindow
from .ViewBase import vbCanvas, vbShortcuts
from ...utils import color2vb

__all__ = ['uiInit']


class uiInit(QtWidgets.QMainWindow, Ui_MainWindow, app.Canvas, vbShortcuts):
    """Group and initialize the graphical elements and interactions.

    Kargs:
        bgcolor: tuple, optional, (def: (0.1, 0.1, 0.1))
            Background color of the main window. The same background
            will be used for the colorbar panel so that future figures
            can be uniform.
    """

    def __init__(self, bgcolor=(0.1, 0.1, 0.1)):
        """Init."""
        # Create the main window :
        super(uiInit, self).__init__(None)
        self.setupUi(self)
        if self._savename is not None:
            self.setWindowTitle('Brain - '+self._savename)

        # Initlialize view :
        self.view = vbCanvas(bgcolor)

        # Add the canvas to the UI (vBrain widget) and colorbar:
        self.vBrain.addWidget(self.view.canvas.native)
        self.cbpanel.addWidget(self.view.cbwc.canvas.native)

        # Set background color and hide quick settings panel :
        self.bgcolor = tuple(color2vb(color=bgcolor, length=1)[0, 0:3])
        self.q_widget.hide()

        # Set background elements :
        self.bgd_red.setValue(self.bgcolor[0])
        self.bgd_green.setValue(self.bgcolor[1])
        self.bgd_blue.setValue(self.bgcolor[2])

        # Initialize shortcuts :
        vbShortcuts.__init__(self, self.view.canvas)
