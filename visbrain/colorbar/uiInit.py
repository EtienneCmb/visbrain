from PyQt5 import QtWidgets
from vispy import app

from .gui import Ui_MainWindow
from .uiMenu import uiMenu, UiScreenshot

__all__ = ['uiInit']


class uiInit(QtWidgets.QMainWindow, Ui_MainWindow, app.Canvas, uiMenu,
             UiScreenshot):
    """Group and initialize the graphical elements and interactions."""

    def __init__(self):
        """Init."""
        # Create the main window :
        super(uiInit, self).__init__(None)
        self.setupUi(self)
        uiMenu.__init__(self)
        UiScreenshot.__init__(self)
