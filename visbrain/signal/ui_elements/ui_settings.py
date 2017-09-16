"""Interactions between user and Settings tab of QuickSettings."""
from ...utils import textline2color

__all__ = ('UiSettings')


class UiSettings(object):
    """Control axis and signal properties."""

    def __init__(self):
        """Init."""
        self._set_bgcolor.editingFinished.connect(self._fcn_set_bgcolor)

    def _fcn_set_bgcolor(self):
        """Change background color."""
        bgcolor = textline2color(str(self._set_bgcolor.text()))[1]
        self._grid_canvas.bgcolor = bgcolor
        self._signal_canvas.bgcolor = bgcolor
