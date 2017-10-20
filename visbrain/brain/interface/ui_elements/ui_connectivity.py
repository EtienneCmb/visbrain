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
