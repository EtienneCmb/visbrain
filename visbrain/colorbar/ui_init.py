"""GUI initialization."""
from PyQt5 import QtWidgets
from vispy import app

from .gui import Ui_MainWindow
from .ui_menu import UiMenu, UiScreenshot


class UiInit(QtWidgets.QMainWindow, Ui_MainWindow, app.Canvas, UiMenu,
             UiScreenshot):
    """Group and initialize the graphical elements and interactions."""

    def __init__(self):
        """Init."""
        # Create the main window :
        super(UiInit, self).__init__(None)
        self.setupUi(self)
        UiMenu.__init__(self)
        UiScreenshot.__init__(self)
