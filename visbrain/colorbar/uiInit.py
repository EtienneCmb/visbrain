from PyQt5 import QtWidgets
from vispy import app

from .gui import Ui_MainWindow

__all__ = ['uiInit']


class uiInit(QtWidgets.QMainWindow, Ui_MainWindow, app.Canvas):
    """Group and initialize the graphical elements and interactions."""

    def __init__(self):
        """Init."""
        # Create the main window :
        super(uiInit, self).__init__(None)
        self.setupUi(self)
