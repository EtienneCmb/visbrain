"""This script make the bridge between the GUI and connectivity elements.

Control the line width, the connectivity mesure (strength / count), the
dynamic / static transparency.
"""


class uiConnectivity(object):
    """Initialize interactions between the GUI and deep functions."""

    def __init__(self,):
        """Init."""
        # Line width :
        self.uiConnect_lw.setValue(self.connect.lw)
        self.uiConnect_lw.valueChanged.connect(self._update_lw)

        # ================== COLOR ==================
        col = ['strength', 'count', 'density']
        # Colorby :
        self.uiConnect_colorby.setCurrentIndex(col.index(self.connect.colorby))
        self.uiConnect_colorby.currentIndexChanged.connect(self._fcn_conColor)
        self._densityRadius.setValue(self.connect.dradius)
        self._densityRadius.valueChanged.connect(self._fcn_conColor)

        # Dynamic / static control of transparency : :
        self._dyn2send = self.connect.dynamic
        self._connectStaDynTransp.currentIndexChanged.connect(self._set_color)
        if (self.connect.dynamic is not None) and isinstance(
                                        self.connect.dynamic, (tuple, list)):
            self.uiConnect_dynMin.setValue(self.connect.dynamic[0])
            self.uiConnect_dynMax.setValue(self.connect.dynamic[1])
            self.uiConnect_dynControl.setEnabled(True)
            self._connectStaDynTransp.setCurrentIndex(1)
        else:
            self._connectStaDynTransp.setCurrentIndex(0)
            self.uiConnect_dynControl.setEnabled(False)
        self.uiConnect_dynMin.valueChanged.connect(self._set_color)
        self.uiConnect_dynMax.valueChanged.connect(self._set_color)

        # ================== BUNDLING ==================
        self._conBlRadius.setValue(self.connect.blradius)
        self._conBlDxyz.setValue(self.connect.blxyz)
        self._conBlRadius.valueChanged.connect(self._fcn_applyBundle)
        self._conBlDxyz.valueChanged.connect(self._fcn_applyBundle)
        self._conBlEnable.clicked.connect(self._fcn_applyBundle)

    def _update_lw(self):
        """Update line width of each connection.

        All line width in conectivity have the same size. I would rather have
        a dynamic size according to connectivity strength, but I didn't find
        how to do it without plotting multiple lines, which is very slow.
        """
        # Get line width (LW) from the button :
        self._lw = self.uiConnect_lw.value()
        # Set the LW :
        self.connect.lw = self._lw

    def _fcn_conColor(self):
        """Change colorby type."""
        # Get color type :
        col = str(self.uiConnect_colorby.currentText())
        if col == 'density':
            self._densityPanel.setVisible(True)
        else:
            self._densityPanel.setVisible(False)
        self.connect.needupdate = True
        self.cbobjs._objs['Connectivity']._vmin = None
        self.cbobjs._objs['Connectivity']._isvmin = False
        self.cbobjs._objs['Connectivity']._vmax = None
        self.cbobjs._objs['Connectivity']._isvmax = False
        self.connect._vmin = self.connect._vmax = None
        self.connect._isvmin = self.connect._isvmax = False
        # Get density radius :
        self.connect.dradius = self._densityRadius.value()
        # Update color :
        self._set_color('', update=True)

    def _set_color(self, _, update=False):
        """Graphic control of color connectivity settings.

        This method is used to control the color code of connectivity (either
        by connectivity strength or by counting the number of connections per
        node). Then
        """
        # Set the dynamic control panel On / Off according to the dynamic
        # button :
        isdyn = int(self._connectStaDynTransp.currentIndex()) == 1
        self.uiConnect_dynControl.setEnabled(isdyn)

        # Get colorby (strength / count):
        colorby = str(self.uiConnect_colorby.currentText())
        self.connect.colorby = colorby

        # Get Min / Max (static or dynamic) :
        self._getMinMax_dyn()

        # Update color :
        self.connect._check_color()

        if update:
            self.cbqt._fcn_cbAutoscale(name='Connectivity')

    def _getMinMax_dyn(self):
        """Dynamic lines opacity.

        The dynamic parameter can be used to have a proportional alpha with
        the strength of connection.
        """
        idxdyn = int(self._connectStaDynTransp.currentIndex())
        # Static color :
        if idxdyn == 0:
            self.connect.dynamic = None
        # Dynamic color :
        elif idxdyn == 1:
            self.connect.dynamic = tuple([self.uiConnect_dynMin.value(),
                                         self.uiConnect_dynMax.value()])

    def _ShowHide(self):
        """Show or hide connections between nodes."""
        self.connect.mesh.visible = self.uiConnectShow.isChecked()

    def _fcn_applyBundle(self):
        """Apply line bundling."""
        viz = self._conBlEnable.isChecked()
        self.connect.bl = viz
        if viz:
            self._conBlPanel.setEnabled(True)
            self.connect.blradius = self._conBlRadius.value()
            self.connect.blxyz = self._conBlDxyz.value()
            self.connect.bundling()
        else:
            self._conBlPanel.setEnabled(False)
        self._set_color('')
