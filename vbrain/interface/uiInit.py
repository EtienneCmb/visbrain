from PyQt4 import QtGui
from vispy import app
import sys

from .gui import Ui_MainWindow
from .ViewBase import ViewBase, vbShortcuts
from ..utils import color2vb

__all__ = ['uiInit']


class uiInit(QtGui.QMainWindow, Ui_MainWindow, app.Canvas, vbShortcuts):

    """Load all ui elements from pyqt
    """

    def __init__(self, bgcolor=(0.1,0.1,0.1)):
        # Create the main window :
        super(uiInit, self).__init__(None)
        self.setupUi(self)
        if self._savename is not None:
            self.setWindowTitle('vbrain - '+self._savename)

    	# Initlialize view :
        self.view = ViewBase(bgcolor)

        # Add the canvas to the UI (vBrain widget) and colorbar:
        self.vBrain.addWidget(self.view.canvas.native)
        self.cbpanel.addWidget(self.view.cbwc.canvas.native)

        # By default, hide quick settings panel :
        self.bgcolor = tuple(color2vb(color=bgcolor, length=1)[0, 0:3])
        self.q_widget.hide()

        # Set background elements :
        self.bgd_red.setValue(self.bgcolor[0])
        self.bgd_green.setValue(self.bgcolor[1])
        self.bgd_blue.setValue(self.bgcolor[2])

        # Initialize shortcuts :
        vbShortcuts.__init__(self, self.view.canvas)
        