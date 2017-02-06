"""This script make the bridge between the GUI and connectivity elements.

Control the line width, the connectivity mesure (strength / count), the
dynamic / static transparency.
"""


class uiConnectivity(object):
    """Initialize interactions between the GUI and deep functions."""

    def __init__(self,):
        """Init."""
        # Show/hide connectivity :
        self.uiConnectShow.clicked.connect(self._toggle_connect_visible)

        # Line width :
        self.view.canvas.context.set_line_width(self._lw)
        self.uiConnect_lw.setValue(self._lw)
        self.uiConnect_lw.valueChanged.connect(self._update_lw)

        # Colorby :
        self.uiConnect_colorby.setCurrentIndex(self._colorby2index(
                                                        self.connect.colorby))
        self.uiConnect_colorby.currentIndexChanged.connect(self._set_color)

        # Dynamic / static control of transparency : :
        self._dyn2send = self.connect.dynamic
        self.uiConnect_static.clicked.connect(self._set_color)
        self.uiConnect_dynamic.clicked.connect(self._set_color)
        if (self.connect.dynamic is not None) and isinstance(
                                        self.connect.dynamic, (tuple, list)):
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
        """Update line width of each connection.

        All line width in conectivity have the same size. I would rather have
        a dynamic size according to connectivity strength, but I didn't find
        how to do it without plotting multiple lines, which is very slow.
        """
        # Get line width (LW) from the button :
        self._lw = self.uiConnect_lw.value()
        # Set the LW to the canvas :
        self.view.canvas.context.set_line_width(self._lw)
        self.view.canvas.update()

    def _set_color(self):
        """Graphic control of color connectivity settings.

        This method is used to control the color code of connectivity (either
        by connectivity strength or by counting the number of connections per
        node). Then
        """
        # Set the dynamic control panel On / Off according to the dynamic
        # button :
        self.uiConnect_dynControl.setEnabled(self.uiConnect_dynamic.isChecked(
                                                                            ))

        # Get colorby (strength / count):
        colorby = self.uiConnect_colorby.currentText()
        self.connect.colorby = colorby

        # Get Min / Max (static or dynamic) :
        self._getMinMax_dyn()

        # Update color :
        self.connect.mesh.set_color(colorby=colorby,
                                    dynamic=self.connect.dynamic,
                                    **self.connect._cb)

        # Be sure to have the latest updated (Min, Max) :
        self.connect._MinMax = self.connect.mesh.get_MinMax

        # Update the mesh :
        self.connect.mesh.update()

    def _getMinMax_dyn(self):
        """Dynamic lines opacity.

        The dynamic parameter can be used to have a proportional alpha with
        the strength of connection.
        """
        # Static color :
        if self.uiConnect_static.isChecked():
            self.connect.dynamic = None
        # Dynamic color :
        elif self.uiConnect_dynamic.isChecked():
            self.connect.dynamic = tuple([self.uiConnect_dynMin.value(),
                                         self.uiConnect_dynMax.value()])

    def _colorby2index(self, colorby):
        """Get index from the selected connectivity mesure.

        There's two way of coloring connectivity:
            * strength : color code by strength of connection.
            * count : color code by the number of connection per node.
        This method return 0 for a connectivity by strength, 1 for count.
        """
        if colorby == 'strength':
            return 0
        elif colorby == 'count':
            return 1
        else:
            raise ValueError('c_colorby not in ["strength", "count"]')

        self.connect._MinMax = self.connect.mesh.get_MinMax

    def _ShowHide(self):
        """Show or hide connections between nodes."""
        self.connect.mesh.visible = self.uiConnectShow.isChecked()

    def _toggle_connect_visible(self):
        """Toggle to display / hide the brain."""
        viz = not self.connect.mesh.visible
        self.connect.mesh.visible = viz
        self.uiConnectShow.setChecked(viz)
        self.toolBox_5.setEnabled(viz)
