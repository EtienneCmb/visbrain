"""GUI interactions with time-series."""

from .ui_objects import _run_method_if_needed
from ....io import dialog_color
from ....utils import textline2color


class UiTimeSeries(object):
    """GUI interactions with time-series."""

    def __init__(self):
        """Init."""
        self._ts_grp.clicked.connect(self._fcn_ts_visible)
        self._ts_width.valueChanged.connect(self._fcn_ts_width)
        self._ts_amp.valueChanged.connect(self._fcn_ts_amp)
        self._ts_line_width.valueChanged.connect(self._fcn_ts_line_width)
        self._ts_color.editingFinished.connect(self._fcn_ts_color)
        self._ts_color_p.clicked.connect(self._fcn_ts_color_p)
        self._ts_alpha.valueChanged.connect(self._fcn_ts_alpha)
        self._ts_dx.valueChanged.connect(self._fcn_ts_translate)
        self._ts_dy.valueChanged.connect(self._fcn_ts_translate)
        self._ts_dz.valueChanged.connect(self._fcn_ts_translate)

    def _ts_to_gui(self):
        """Send time-series object properties to the GUI."""
        obj = self._get_select_object()
        self._ts_grp.setChecked(obj.visible_obj)
        self._ts_width.setValue(obj.ts_width)
        self._ts_amp.setValue(obj.ts_amp)
        self._ts_line_width.setValue(obj.line_width)
        self._ts_color.setText(str(obj.color))
        self._ts_alpha.setValue(obj.alpha * 100.)
        dxyz = obj.translate
        self._ts_dx.setValue(dxyz[0])
        self._ts_dy.setValue(dxyz[1])
        self._ts_dz.setValue(dxyz[2])

    @_run_method_if_needed
    def _fcn_ts_visible(self):
        """Display / hide time-series."""
        self._get_select_object().visible_obj = self._ts_grp.isChecked()

    @_run_method_if_needed
    def _fcn_ts_width(self):
        """Time series width."""
        self._get_select_object().ts_width = self._ts_width.value()

    @_run_method_if_needed
    def _fcn_ts_amp(self):
        """Time series amplitude."""
        self._get_select_object().ts_amp = self._ts_amp.value()

    @_run_method_if_needed
    def _fcn_ts_line_width(self):
        """Time series line width."""
        self._get_select_object().line_width = self._ts_line_width.value()

    @_run_method_if_needed
    def _fcn_ts_color(self):
        """Time series color."""
        color = textline2color(str(self._ts_color.text()))[1]
        self._get_select_object().color = color

    def _fcn_ts_color_p(self):
        """Time series color picker."""
        color = dialog_color()
        self._ts_color.setText(color)
        self._fcn_ts_color()

    @_run_method_if_needed
    def _fcn_ts_alpha(self):
        """Time series alpha."""
        self._get_select_object().alpha = self._ts_alpha.value() / 100.

    @_run_method_if_needed
    def _fcn_ts_translate(self):
        """Time series translation."""
        tr = (self._ts_dx.value(), self._ts_dy.value(), self._ts_dz.value())
        self._get_select_object().translate = tr
