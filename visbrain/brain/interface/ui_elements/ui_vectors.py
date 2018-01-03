"""GUI interactions with pictures."""
from vispy.visuals.line.arrow import ARROW_TYPES

from .ui_objects import _run_method_if_needed


class UiVectors(object):
    """GUI interactions with vectors."""

    def __init__(self):
        """Init."""
        self._vec_grp.clicked.connect(self._fcn_vec_visible)
        self._vec_line_width.valueChanged.connect(self._fcn_vec_line_width)
        self._vec_arrow_size.valueChanged.connect(self._fcn_vec_arrow_size)
        self._vec_arrow_type.currentIndexChanged.connect(
            self._fcn_vec_arrow_type)

    def _vec_to_gui(self):
        """Send vectors object properties to the GUI."""
        obj = self._get_select_object()
        self._vec_grp.setChecked(obj.visible_obj)
        self._vec_line_width.setValue(obj.line_width)
        self._vec_arrow_size.setValue(obj.arrow_size)
        idx = ARROW_TYPES.index(obj.arrow_type)
        self._vec_arrow_type.setCurrentIndex(idx)

    @_run_method_if_needed
    def _fcn_vec_visible(self):
        """Display / hide pictures."""
        self._get_select_object().visible_obj = self._vec_grp.isChecked()

    @_run_method_if_needed
    def _fcn_vec_line_width(self):
        """Update line width."""
        self._get_select_object().line_width = self._vec_line_width.value()

    @_run_method_if_needed
    def _fcn_vec_arrow_size(self):
        """Update arrow size."""
        self._get_select_object().arrow_size = self._vec_arrow_size.value()

    @_run_method_if_needed
    def _fcn_vec_arrow_type(self):
        """Update arrow type."""
        arrow_type = self._vec_arrow_type.currentText()
        self._get_select_object().arrow_type = str(arrow_type)
