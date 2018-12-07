"""Grid of eletrophysiological signals object."""
import numpy as np

from itertools import product

from vispy import scene

from .visbrain_obj import VisbrainObject
from ..visuals.grid_signal_visual import GridSignal
from ..io.dependencies import is_mne_installed


class GridSignalsObj(VisbrainObject):
    """Take a VisPy visual and turn it into a compatible Visbrain object.

    Parameters
    ----------
    name : string
        The name of the VisPy object.
    transform : VisPy.visuals.transforms | None
        VisPy transformation to set to the parent node.
    parent : VisPy.parent | None
        Hypnogram object parent.
    verbose : string
        Verbosity level.
    """

    def __init__(self, name, data, transform=None, parent=None,
                 verbose=None):
        """Init."""
        VisbrainObject.__init__(self, name, parent, transform, verbose)
        kw = dict()
        if isinstance(data, np.ndarray):
            pass
        elif is_mne_installed():
            import mne
            if isinstance(data, (mne.io.RawArray, mne.io.Raw)):
                kw['title'] = data.ch_names
                data = data.get_data()
            elif isinstance(data, mne.Epochs):
                channels = data.ch_names
                data = np.swapaxes(data.get_data(), 0, 1)
                n_channels, n_epochs, _ = data.shape
                kw['title'] = ['%s - Epoch %i' % (i, k + 1) for i, k in product(channels, np.arange(n_epochs))]
                kw['force_shape'] = (n_channels, n_epochs)
        self._grid = GridSignal(data, method='gl', width=2, parent=self._node, **kw)
        self._grid._txt.parent = self._node
        self._grid.tcolor = 'white'
        self._grid.method = 'gl'

    def _get_camera(self):
        return scene.cameras.PanZoomCamera((-1.01, -1.05, 2.03, 2.1))
