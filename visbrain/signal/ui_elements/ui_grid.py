"""Interactions with Grid panel."""

__all__ = ('UiGrid')


class UiGrid(object):
    """Interactions with Grid panel."""

    def __init__(self):
        """Init."""
        # Scaling :
        self._grid_scalex.valueChanged.connect(self._fcn_grid_scale)
        self._grid_scaley.valueChanged.connect(self._fcn_grid_scale)
        # Space :
        self._grid_space.valueChanged.connect(self._fcn_grid_space)

    def _fcn_grid_scale(self):
        """Control grid scaling."""
        scale = (self._grid_scalex.value(), self._grid_scaley.value())
        self._grid.scale = scale
        self.update_cameras(update='grid')

    def _fcn_grid_space(self):
        """Control grid space."""
        self._grid.space = self._grid_space.value()
        self.update_cameras(update='grid')
