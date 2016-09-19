

class uiConnectivity(object):

    """docstring for uiConnectivity
    """

    def __init__(self,):
        # Show/hide connectivity :
        self.uiConnectShow.clicked.connect(self._ShowHide)

        # Line width :
        self.view.canvas.context.set_line_width(self._lw)
        self.uiConnect_lw.setValue(self._lw)
        self.uiConnect_lw.valueChanged.connect(self._update_lw)

        # Colorby :
        self.uiConnect_colorby.setCurrentIndex(self._colorby2index(self.connect.colorby))
        self.uiConnect_colorby.currentIndexChanged.connect(self._set_color)

        # Dynamic :
        self._dyn2send = self.connect.dynamic
        self.uiConnect_static.clicked.connect(self._static)
        self.uiConnect_dynamic.clicked.connect(self._dynamic)
        if (self.connect.dynamic is not None) and isinstance(self.connect.dynamic, (tuple, list)):
            self.uiConnect_dynMin.setValue(self.connect.dynamic[0])
            self.uiConnect_dynMax.setValue(self.connect.dynamic[1])
            self.uiConnect_dynControl.setEnabled(True)
            self.uiConnect_dynamic.setChecked(True)
        else:
            self.uiConnect_dynControl.setEnabled(False)
            self.uiConnect_static.setChecked(True)
        self.uiConnect_dynMin.valueChanged.connect(self._set_color)
        self.uiConnect_dynMax.valueChanged.connect(self._set_color)

    def _update_lw(self):
        """Update line width
        """
        self._lw = self.uiConnect_lw.value()
        self.view.canvas.context.set_line_width(self._lw)
        self.view.canvas.update()


    def _set_color(self):
        """Set color properties
        """
        # Get colorby :
        colorby = self.uiConnect_colorby.currentText()
        self.connect.colorby = colorby

        # Get dynamic :
        self._getMinMax_dyn()
        print(self.connect._cb)
        # Update color :
        self.connect.mesh.set_color(colorby=colorby, dynamic=self.connect.dynamic, **self.connect._cb)
        self.connect.mesh.update()


    def _getMinMax_dyn(self):
        """
        """
        if self.uiConnect_static.isChecked():
            self.connect.dynamic = None
        elif self.uiConnect_dynamic.isChecked():
            self.connect.dynamic = tuple([self.uiConnect_dynMin.value(),
                                   self.uiConnect_dynMax.value()])
            
            
    def _static(self):
        """
        """
        self.uiConnect_dynControl.setEnabled(False)
        self._set_color()


    def _dynamic(self):
        """
        """
        self.uiConnect_dynControl.setEnabled(True)
        self._set_color()



    def _colorby2index(self, colorby):
        """Transform a colorby string to index
        """ 
        if colorby == 'strength':
            return 0
        elif colorby == 'count':
            return 1
        else:
            raise ValueError('c_colorby not in ["strength", "count"]')


    def _ShowHide(self):
        """
        """
        self.connect.mesh.visible = self.uiConnectShow.isChecked()