"""GUI interactions with pictures."""

from .ui_objects import _run_method_if_needed


class UiPictures(object):
    """GUI interactions with pictures."""

    def __init__(self):
        """Init."""
        self._pic_grp.clicked.connect(self._fcn_pic_visible)
        self._pic_width.valueChanged.connect(self._fcn_pic_width)
        self._pic_height.valueChanged.connect(self._fcn_pic_height)
        self._pic_alpha.valueChanged.connect(self._fcn_pic_alpha)
        self._pic_dx.valueChanged.connect(self._fcn_pic_translate)
        self._pic_dy.valueChanged.connect(self._fcn_pic_translate)
        self._pic_dz.valueChanged.connect(self._fcn_pic_translate)

    def _pic_to_gui(self):
        """Send pictures object properties to the GUI."""
        obj = self._get_select_object()
        self._pic_grp.setChecked(obj.visible_obj)
        self._pic_width.setValue(obj.pic_width)
        self._pic_height.setValue(obj.pic_height)
        self._pic_alpha.setValue(obj.alpha * 100.)
        dxyz = obj.translate
        self._pic_dx.setValue(dxyz[0])
        self._pic_dy.setValue(dxyz[1])
        self._pic_dz.setValue(dxyz[2])

    @_run_method_if_needed
    def _fcn_pic_visible(self):
        """Display / hide pictures."""
        self._get_select_object().visible_obj = self._pic_grp.isChecked()

    @_run_method_if_needed
    def _fcn_pic_width(self):
        """Update picture width."""
        self._get_select_object().pic_width = self._pic_width.value()

    @_run_method_if_needed
    def _fcn_pic_height(self):
        """Update picture height."""
        self._get_select_object().pic_height = self._pic_height.value()

    @_run_method_if_needed
    def _fcn_pic_alpha(self):
        """Update picture alpha."""
        self._get_select_object().alpha = self._pic_alpha.value() / 100.

    @_run_method_if_needed
    def _fcn_pic_translate(self):
        """Translate pictures."""
        tr = (self._pic_dx.value(), self._pic_dy.value(), self._pic_dz.value())
        self._get_select_object().translate = tr
