"""Grid of eletrophysiological signals object."""
import numpy as np

from itertools import product

from vispy import scene

from .visbrain_obj import VisbrainObject
from ..visuals.grid_signal_visual import GridSignal
from ..io.dependencies import is_mne_installed
from ..utils.cameras import YScrollCam


class GridSignalsObj(VisbrainObject):
    """Take a VisPy visual and turn it into a compatible Visbrain object.

    Parameters
    ----------
    name : string
        The name of the GridSignals object.
    data : array_like
        Array of data. 1D, 2D or 3D datasets are supported. In addition, the
        following MNE-Python objects are also supported :

            * mne.io.Raw
            * mne.io.RawArray
            * mne.Epochs
    axis : int | -1
        Location of the time axis.
    lw : float | 2.
        Line width.
    title : list | None
        List of strings describing the title of each element. The length of
        this list depends on the shape of the provided data.

            * 1d = (n_times,) : len(title) = 1
            * 2d = (n_rows, n_times) : len(title) = n_rows
            * 3d = (n_rows, n_cols, n_times) : len(title) = n_rows * n_cols
        If an MNE-Python object is passed, titles are automatically inferred.
    title_size : float | 10.
        Size of the title text.
    title_color : string, list, tuple | 'white'
        Color of titles.
    title_bold : bool | True
        Specify if titles should be bold or not.
    title_visible : bool | True
        Specify if titles should be displayed.
    transform : VisPy.visuals.transforms | None
        VisPy transformation to set to the parent node.
    parent : VisPy.parent | None
        Hypnogram object parent.
    verbose : string
        Verbosity level.
    """

    def __init__(self, name, data, axis=-1, lw=2., title=None, title_size=10,
                 title_color='white', title_bold=True, title_visible=True,
                 transform=None, parent=None, verbose=None):
        """Init."""
        VisbrainObject.__init__(self, name, parent, transform, verbose)
        lw = max(lw, 1.)
        kw = dict(title=title, font_size=title_size, title_bold=title_bold,
                  title_color=title_color, width=lw, color='black')
        if isinstance(data, np.ndarray):
            pass
        elif is_mne_installed():
            import mne
            if isinstance(data, (mne.io.RawArray, mne.io.Raw)):
                kw['title'] = data.ch_names
                data = data.get_data()
                self._name = 'MNE-Raw'
            elif isinstance(data, mne.Epochs):
                channels = data.ch_names#[0:10]
                data = np.swapaxes(data.get_data(), 0, 1)[..., ::10]
                print(data.shape)
                # 0/0
                # data = data[0:10, 0:50, ...]
                n_channels, n_epochs, _ = data.shape
                kw['title'] = ['%s - Epoch %i' % (i, k + 1) for i, k in product(channels, np.arange(n_epochs))]
                # kw['force_shape'] = (n_channels * n_epochs, 1)
                kw['force_shape'] = (n_channels, n_epochs)
                print(data.shape, kw['force_shape'], len(channels), len(kw['title']))
                self._name = 'MNE-Epoch'
        self._grid = GridSignal(data, parent=self._node, **kw)
        self._grid._txt.parent = self._node
        self._grid._txt.visible = title_visible

    def _get_camera(self):
        return scene.cameras.PanZoomCamera((-1.01, -1.05, 2.03, 2.1))
        n_sig = np.prod(self._grid.g_size)
        d = 20 / (n_sig)
        # return scene.cameras.PanZoomCamera((-1.01, 1 - 2 * d, 2.03, 2 * d))
        return YScrollCam((-1.01, 1 - 2 * d, 2.03, 2.05 * d), ylim=(-1, 1 - 2 * d), smooth=n_sig)
