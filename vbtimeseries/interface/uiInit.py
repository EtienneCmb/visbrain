from PyQt4 import QtGui
from vispy import app
import sys


from PyQt4.QtCore import *

from vispy import scene
from vispy.scene.visuals import Line
import vispy.scene.cameras as viscam
import numpy as np

from .gui import Ui_MainWindow

from ...vbrain.utils import normalize
from ..visuals import CanvasTest

__all__ = ['uiInit']


class SubplotManagement(object):

    """docstring for SubplotManagement
    """

    def __init__(self):
        super(SubplotManagement, self).__init__()
        self.arg = arg

    def __getitem__(self, idx):
        subplot = self._rowcol2name(idx[0], idx[1])
        return self.subplot[subplot][idx[2]]


    def _add(self, row, col):
        # Create external vetical layout :
        # ----------------------------------------
        wExt = QtGui.QWidget()
        layOutExt = QtGui.QVBoxLayout(wExt)

        # Create then add a canvas inside :
        # ----------------------------------------
        # Create a widget :
        wInt = QtGui.QWidget()
        # Layout for canvas :
        layOutTime = QtGui.QVBoxLayout(wInt)
        # Create canvas and widget central :

        # ratio = wExt.height()/wExt.width()
        # print(wExt.width(), wExt.height())
        # wc.camera = viscam.PanZoomCamera()
        # wc.camera.set_range(x=(-1, 1), y=(-1, 1), z=(-10,10))
        # Add canvas to the layout widget :
        canvas = CanvasTest()
        # canvas2.parent = wc.scene

        layOutTime.addWidget(canvas.native) #canvas.native
        # Add widget to the layout :
        layOutExt.addWidget(wInt)
        # layOutExt.addStretch()

        # Create a slider and add it to the layout :
        # ----------------------------------------
        # Create slider :
        # sl = QtGui.QSlider(Qt.Horizontal)
        # layOutExt.addWidget(sl)
        # layOutExt.addStretch()

        # Save those objects in a dictionnary :
        # ----------------------------------------
        obj = {'canvas': canvas, 'wExt':wExt}

        # Add widget to grid and save it :
        # ----------------------------------------
        self.gridVbt.addWidget(wExt, row, col)
        self.subplot[self._rowcol2name(row, col)] = obj
        


    def _hide(self, row, col):
        self.subplot[self._rowcol2name(row, col)]['wExt'].hide()


    def _rowcol2name(self, row, col):
        return str(row)+'-'+str(col)


    def _set_data(self, data, time, row, col):
        # Check data and time :
        data, time = data.ravel(), time.ravel()
        data = normalize(data, -1, 1)
        time = normalize(time, -1, 1)
        print(data.min(), data.max())
        # data -= data.mean()
        # time -= time.mean()
        if len(data) != len(time):
            raise ValueError('Length of data and time must be the same')

        # Get parent widget central :
        wc = self[row, col, 'wc']

        # Create a plot :
        linePlt = Line(pos=np.array([time, data]).T,
                       parent=wc.scene, color='w')

        # Add a camera :
        # wc.camera = viscam.PanZoomCamera(rect=(-500, 500, 500, 500))


class uiInit(QtGui.QMainWindow, Ui_MainWindow, app.Canvas, SubplotManagement):

    """Load all ui elements for time series from pyqt
    """

    def __init__(self, bgcolor=(0.1,0.1,0.1)):
        # Create the main window :
        super(uiInit, self).__init__(None)
        super(SubplotManagement, self).__init__()
        self.setupUi(self)

        # Build a list of subplot :
        self.subplot = {}

        self._add(0, 0)
        print('SIZE : ', self[0,0,'wExt'].width(), self[0,0,'wExt'].height())
        print(self.gridVbt.columnCount())

        self._add(1, 0)
        # print('SIZE : ', self[0,1,'wExt'].width(), self[0,1,'wExt'].height())
        # print(self.gridVbt.columnStretch(0))

        # self._add(2, 2)
        # print('SIZE : ', self[1,0,'wExt'].width(), self[1,0,'wExt'].height())
        # print(self.gridVbt.columnStretch(0))

        # self._add(3, 0)
        # self._add(3, 2)
        # print('SIZE : ', self[1,1,'wExt'].width(), self[1,1,'wExt'].height())
        # print(self.gridVbt.columnStretch(0))


        data = 1000*np.sin(np.arange(100,))
        time = np.arange(len(data))

        print('SIZE : ', self[0,0,'wExt'].width(), self[0,0,'wExt'].height())

        for k in range(2):
            self[k,0,'canvas'].size = (1000,1000)



        
        