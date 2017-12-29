"""This script group the diffrent graphical components.

Grouped components :
    * PyQt elements (window, Pyqt functions...)
    * Vispy canvas functions
    * User shortcuts
"""
from PyQt5 import QtWidgets
from vispy import app, scene

from .gui import Ui_MainWindow
from ..config import CONFIG


class TopoCanvas(object):
    """Canvas creation."""

    def __init__(self, title='', bgcolor=(0, 0, 0)):
        """Init."""
        # Initialize main canvas:
        self.canvas = scene.SceneCanvas(keys='interactive', show=False,
                                        dpi=600, bgcolor=bgcolor,
                                        fullscreen=True, resizable=True,
                                        title=title, app=CONFIG['VISPY_APP'])


class UiInit(QtWidgets.QMainWindow, Ui_MainWindow, app.Canvas):
    """Group and initialize the graphical elements and interactions."""

    def __init__(self):
        """Init."""
        # Create the main window :
        super(UiInit, self).__init__(None)
        self.setupUi(self)
        self._view = TopoCanvas('MainCanvas', 'white')
        self._grid = self._view.canvas.central_widget.add_grid()
        self._TopoLayout.addWidget(self._view.canvas.native)
