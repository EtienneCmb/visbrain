from PyQt4 import QtGui
import sys

from vispy import io, app
import vispy.app as visapp

from .interface import uiInit


class vbtimeseries(uiInit):

    """
    """

    def __init__(self, *args, **kwargs):

        # ------ App creation ------
        # Create the app and initialize all graphical elements :
        self._app = QtGui.QApplication(sys.argv)
        uiInit.__init__(self)

    def show(self):
        self.showMaximized()
        visapp.run()