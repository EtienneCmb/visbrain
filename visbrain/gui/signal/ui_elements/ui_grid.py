"""Interactions with the grid panel."""
import numpy as np

from visbrain.utils import textline2color, safely_set_spin
from visbrain.io import dialog_color, is_opengl_installed


class UiGrid(object):
    """Interactions with the grid panel."""

    def __init__(self):
        """Init."""
        # Grid settings :
        self._grid_lw.valueChanged.connect(self._fcn_grid_lw)
        self._grid_smooth.clicked.connect(self._fcn_grid_lw)
        # Grid organization :
        self._grid_nrows.valueChanged.connect(self._fcn_check_rows)
        self._grid_ncols.valueChanged.connect(self._fcn_check_cols)
        self._grid_reorg_apply.clicked.connect(self._fcn_reorganize_grid)
        # Grid appearance :
        self._grid_titles.clicked.connect(self._fcn_grid_tupdate)
        self._grid_titles_fz.valueChanged.connect(self._fcn_grid_tupdate)
        self._grid_titles_color.editingFinished.connect(self._fcn_grid_tupdate)
        self._grid_color_picker.clicked.connect(self._fcn_grid_color_picker)

    def _fcn_grid_lw(self):
        """Change grid line-width."""
        if hasattr(self, '_grid'):
            self._grid.width = self._grid_lw.value()
            if is_opengl_installed():
                method = 'agg' if self._grid_smooth.isChecked() else 'gl'
                if hasattr(self, '_grid'):
                    self._grid.method = method
            else:
                self._grid_smooth.setEnabled(False)

    def _fcn_check_rows(self):
        """Check the number of rows and update the number of columns."""
        n_rows = self._grid_nrows.value()
        is_int, n_cols = self._check_reorganize_grid(n_rows)
        if is_int:
            safely_set_spin(self._grid_ncols, n_cols, [self._fcn_check_cols])
        self._grid_reorg_apply.setEnabled(is_int)

    def _fcn_check_cols(self):
        """Check the number of columns and update the number of rows."""
        n_cols = self._grid_ncols.value()
        is_int, n_rows = self._check_reorganize_grid(n_cols)
        if is_int:
            safely_set_spin(self._grid_nrows, n_rows, [self._fcn_check_rows])
        self._grid_reorg_apply.setEnabled(is_int)

    def _check_reorganize_grid(self, n):
        """Check grid re-organization."""
        if hasattr(self, '_grid'):
            # Get grid size :
            g_size = np.prod(self._grid.g_size)
            return g_size % n == 0, int(g_size / n)

    def _fcn_reorganize_grid(self):
        """Re-organize the grid."""
        nshape = (self._grid_nrows.value(), self._grid_ncols.value())
        self._grid.set_data(self._data, self._axis, force_shape=nshape)

    def _fcn_grid_tupdate(self):
        """Update grid titles properties."""
        if hasattr(self, '_grid'):
            self._grid.font_size = float(self._grid_titles_fz.value())  # fz
            col = textline2color(str(self._grid_titles_color.text()))[1]
            self._grid.tcolor = col  # title color
            self._grid.tvisible = self._grid_titles.isChecked()  # title

    def _fcn_grid_color_picker(self):
        """Grid color picker."""
        color = dialog_color()
        self._grid_titles_color.setText(str(color))
        self._fcn_grid_tupdate()
