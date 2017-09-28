"""Interactions with the grid panel."""
from ...utils import textline2color


class UiGrid(object):
    """Interactions with the grid panel."""

    def __init__(self):
        """Init."""
        self._grid_titles.clicked.connect(self._fcn_grid_tupdate)
        self._grid_titles_fz.valueChanged.connect(self._fcn_grid_tupdate)
        self._grid_titles_color.editingFinished.connect(self._fcn_grid_tupdate)

    def _fcn_grid_tupdate(self):
        """Update grid titles properties."""
        if hasattr(self, '_grid'):
            self._grid.font_size = float(self._grid_titles_fz.value())  # fz
            col = textline2color(str(self._grid_titles_color.text()))[1]
            self._grid.tcolor = col  # title color
            self._grid.tvisible = self._grid_titles.isChecked()  # title
