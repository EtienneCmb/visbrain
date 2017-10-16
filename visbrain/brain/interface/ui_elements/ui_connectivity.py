"""This script make the bridge between the GUI and connectivity elements.

Control the line width, the connectivity mesure (strength / count), the
dynamic / static transparency.
"""
from .ui_objects import _run_method_if_needed


class UiConnectivity(object):
    """Initialize interactions between the GUI and deep functions."""

    def __init__(self,):
        """Init."""
        # Visibility :
        self._c_grp.clicked.connect(self._fcn_connect_visible)
        # Color :
        self._c_colorby.currentIndexChanged.connect(self._fcn_connect_colorby)
        self._c_dyn_meth.currentIndexChanged.connect(
            self._fcn_connect_transparency_meth)
        # Transparency :
        self._c_alpha.valueChanged.connect(self._fcn_connect_alpha)
        self._c_dyn_min.valueChanged.connect(self._fcn_connect_dyn_alpha)
        self._c_dyn_max.valueChanged.connect(self._fcn_connect_dyn_alpha)
        # Line width :
        self._c_line_width.valueChanged.connect(self._fcn_connect_lw)
        # # Line width :
        # self.uiConnect_lw.setValue(self.connect.lw)
        # self.uiConnect_lw.valueChanged.connect(self._fcn_connect_lw
        #                                        )

        # # ================== COLOR ==================
        # col = ['strength', 'count', 'density']
        # # Colorby :
        # self.uiConnect_colorby.setCurrentIndex(col.index(self.connect.colorby))
        # self._densityRadius.setValue(self.connect.dradius)
        # self._densityRadius.valueChanged.connect(self._fcn_connect_colorby)

        # # Dynamic / static control of transparency : :
        # self._dyn2send = self.connect.dynamic
        # self._connectStaDynTransp.currentIndexChanged.connect(
        #     self._fcn_connect_set_color)
        # if (self.connect.dynamic is not None) and isinstance(
        #         self.connect.dynamic, (tuple, list)):
        #     self.uiConnect_dynMin.setValue(self.connect.dynamic[0])
        #     self.uiConnect_dynMax.setValue(self.connect.dynamic[1])
        #     self.uiConnect_dynControl.setEnabled(True)
        #     self._connectStaDynTransp.setCurrentIndex(1)
        # else:
        #     self._connectStaDynTransp.setCurrentIndex(0)
        #     self.uiConnect_dynControl.setEnabled(False)
        # self.uiConnect_dynMin.valueChanged.connect(self._fcn_connect_set_color)
        # self.uiConnect_dynMax.valueChanged.connect(self._fcn_connect_set_color)

        # # ================== BUNDLING ==================
        # self._conBlRadius.setValue(self.connect.blradius)
        # self._conBlDxyz.setValue(self.connect.blxyz)
        # self._conBlRadius.valueChanged.connect(self._fcn_connect_bundle)
        # self._conBlDxyz.valueChanged.connect(self._fcn_connect_bundle)
        # self._conBlEnable.clicked.connect(self._fcn_connect_bundle)

    def _connect_to_gui(self):
        """Send connectivity object properties to the GUI."""
        obj = self._get_select_object()
        # Visible :
        self._c_grp.setChecked(obj.visible_obj)
        # Color method :
        self._c_colorby.setCurrentIndex(int(obj.color_by == 'count'))
        self._c_alpha.setValue(obj.alpha * 100.)
        # Transparency method :
        if obj._dynamic is None:  # static
            idx_meth, alpha, r_min, r_max = 0, obj.alpha * 100., 0., 1.
        else:                     # dynamic
            idx_meth, alpha = 1, 100.
            r_min, r_max = obj.dynamic
        self._c_dyn_meth.setCurrentIndex(idx_meth)
        self._c_alpha_stack.setCurrentIndex(idx_meth)
        self._c_alpha.setValue(alpha)
        self._c_dyn_min.setValue(r_min)
        self._c_dyn_max.setValue(r_max)
        # Line width :
        self._c_line_width.setValue(obj.line_width)

    @_run_method_if_needed
    def _fcn_connect_visible(self):
        """Set the connectivity object visible / hide."""
        obj = self._get_select_object()
        obj.visible_obj = self._c_grp.isChecked()

    @_run_method_if_needed
    def _fcn_connect_colorby(self):
        """Change the coloring method."""
        cby = self._c_colorby.currentText()
        self._get_select_object().color_by = cby

    @_run_method_if_needed
    def _fcn_connect_transparency_meth(self):
        """Update the transparency method."""
        idx_meth = int(self._c_dyn_meth.currentIndex())
        self._c_alpha_stack.setCurrentIndex(idx_meth)
        if idx_meth == 0:  # static alpha
            self._fcn_connect_alpha()
        else:              # dynamic alpha
            self._fcn_connect_dyn_alpha()

    @_run_method_if_needed
    def _fcn_connect_alpha(self):
        """Static alpha transparency."""
        obj = self._get_select_object()
        obj.alpha = self._c_alpha.value() / 100.
        obj._dynamic = None

    @_run_method_if_needed
    def _fcn_connect_dyn_alpha(self):
        """Dynamic alpha transparency."""
        dyn = (self._c_dyn_min.value(), self._c_dyn_max.value())
        self._get_select_object().dynamic = dyn

    @_run_method_if_needed
    def _fcn_connect_lw(self):
        """Update line width."""
        self._get_select_object().line_width = self._c_line_width.value()





















    # def _fcn_connect_lw(self):
    #     """Update line width of each connection.

    #     All line width in conectivity have the same size. I would rather have
    #     a dynamic size according to connectivity strength, but I didn't find
    #     how to do it without plotting multiple lines, which is very slow.
    #     """
    #     # Get line width (LW) from the button :
    #     self._lw = self.uiConnect_lw.value()
    #     # Set the LW :
    #     self.connect.lw = self._lw

    # def _fcn_connect_colorby(self):
    #     """Change colorby type."""
    #     # Get color type :
    #     col = str(self.uiConnect_colorby.currentText())
    #     if col == 'density':
    #         self._densityPanel.setVisible(True)
    #     else:
    #         self._densityPanel.setVisible(False)
    #     self.connect.needupdate = True
    #     self.cbobjs._objs['Connectivity']._vmin = None
    #     self.cbobjs._objs['Connectivity']._isvmin = False
    #     self.cbobjs._objs['Connectivity']._vmax = None
    #     self.cbobjs._objs['Connectivity']._isvmax = False
    #     self.connect._vmin = self.connect._vmax = None
    #     self.connect._isvmin = self.connect._isvmax = False
    #     # Get density radius :
    #     self.connect.dradius = self._densityRadius.value()
    #     # Update color :
    #     self._fcn_connect_set_color(update=True)

    def _fcn_connect_set_color(self, *args, update=False):
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
        self._get_minmax_dyn_connect()

        # Update color :
        self.connect._check_color()

        if update:
            self.cbqt._fcn_cbAutoscale(name='Connectivity')

    def _get_minmax_dyn_connect(self):
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
