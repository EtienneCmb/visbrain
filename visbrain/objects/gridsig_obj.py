"""Grid of eletrophysiological signals object."""
import logging

import numpy as np

from itertools import product

from vispy import scene

from .visbrain_obj import VisbrainObject
from ..visuals.grid_signal_visual import GridSignal
from ..io.dependencies import is_mne_installed
from ..utils.cameras import ScrollCamera

logger = logging.getLogger('visbrain')

N_LIMIT = 20000000  # Limit on the total number of points to display


class GridSignalsObj(VisbrainObject):
    """Take a VisPy visual and turn it into a compatible Visbrain object.

    Parameters
    ----------
    name : string
        The name of the GridSignals object.
    data : array_like
        The data to plot. The following types are supported :

            * NumPy array : a 1D, 2D or 3D array
            * mne.io.Raw
            * mne.io.RawArray
            * mne.Epochs
    axis : int | -1
        Location of the time axis.
    plt_as : {'grid', 'row', 'col'}
        Plotting type. By default data is presented as a grid. Use :

            * 'grid' : plot data as a grid of signals.
            * 'row' : plot data as a single row. Only horizontal camera
              movements are permitted
            * 'col' : plot data as a single column. Only vertical camera
              movements are permitted
    n_signals : int | 10
        Number of signals to display if `plt_as` is `row` or `col`.
    lw : float | 2.
        Line width.
    color : string, list, tuple | 'white'
        Line color.
    title : list | None
        List of strings describing the title of each element. The length of
        this list depends on the shape of the provided data.

            * 1d = (n_times,) : len(title) = 1
            * 2d = (n_rows, n_times) : len(title) = n_rows
            * 3d = (n_rows, n_cols, n_times) : len(title) = n_rows * n_cols
        If an MNE-Python object is passed, titles are automatically inferred.
    title_size : float | 10.
        Size of the title text.
    title_bold : bool | True
        Specify if titles should be bold or not.
    title_visible : bool | True
        Specify if titles should be displayed.
    decimate : string, bool, int | 'auto'
        Depending on your system, plotting a too large number of signals can
        possibly fail. To fix this issue, there's a limited number of points of
        (20 million) and if your data exceeds this number of points, data is
        decimated along the time axis. Use :

            * 'auto' : automatically find the most appropriate decimation
              factor
            * int : use a specific decimation ratio (e.g 2, 3 etc)
            * False : if you don't want to decimate
    transform : VisPy.visuals.transforms | None
        VisPy transformation to set to the parent node.
    parent : VisPy.parent | None
        Hypnogram object parent.
    verbose : string
        Verbosity level.
    """

    def __init__(self, name, data, axis=-1, plt_as='grid', n_signals=10, lw=2.,
                 color='white', title=None, title_size=10, title_bold=True,
                 title_visible=True, decimate='auto', transform=None,
                 parent=None, verbose=None):
        """Init."""
        VisbrainObject.__init__(self, name, parent, transform, verbose)
        # Checking :
        lw = max(lw, 1.)
        self._n_signals = n_signals
        kw = dict(title=title, font_size=title_size, title_bold=title_bold,
                  title_color=color, width=lw, color=color,
                  plt_as=plt_as, axis=axis)
        if isinstance(data, np.ndarray):
            logger.info('    data is a %iD NumPy array' % data.ndim)
        elif is_mne_installed():
            import mne
            if isinstance(data, (mne.io.RawArray, mne.io.Raw)):
                logger.info('    data is mne.io.Raw')
                kw['title'], kw['axis'] = data.ch_names, -1
                data = data.get_data()
                self._name = 'MNE-Raw'
            elif isinstance(data, mne.Epochs):
                logger.info('    data is mne.Epochs')
                channels = data.ch_names
                data = np.swapaxes(data.get_data(), 0, 1)
                n_channels, n_epochs, _ = data.shape
                prod = product(channels, np.arange(n_epochs))
                kw['title'] = ['%s - Epoch %i' % (i, k + 1) for i, k in prod]
                kw['axis'] = -1
                self._name = 'MNE-Epoch'
        # Decimate if needed :
        sh_ori = np.array(data.shape)
        if (np.prod(sh_ori) > N_LIMIT) and decimate:
            if decimate == 'auto':
                decimate, sh = 2, sh_ori.copy()
                while np.prod(sh) > N_LIMIT:
                    sh = sh_ori.copy()
                    sh[axis] = int(sh[axis] / decimate)
                    print(sh)
                    decimate += 1
                decimate -= 1
            assert isinstance(decimate, int)
            # decimate data and titles :
            dec_axis = [slice(None)] * data.ndim
            dec_axis[axis] = slice(0, -1, decimate)
            data = data[tuple(dec_axis)]
            logger.warning("data has been decimated with a factor of "
                           "%i. If you don't want to decimate use "
                           "`decimate`=False" % (decimate))

        self._grid = GridSignal(data, parent=self._node, **kw)
        self._grid._txt.parent = self._node
        self._grid._txt.visible = title_visible

    def _get_camera(self):
        """Get the camera according to the plotting type."""
        margin = .004
        r, d = -1. - margin, 2. * (1. + margin)
        off = .05 if self._grid._txt.visible else 0.  # title offset
        if self._grid._plt_as == 'grid':
            return scene.cameras.PanZoomCamera((r, r, d, d + off))
        elif self._grid._plt_as in ['row', 'col']:
            n_sig_tot = np.prod(self._grid.g_size)  # total number of signals
            n_sig = self._n_signals  # number of signals per window
            _off = .5  # additional margin
            s = 2. * (n_sig / n_sig_tot)  # nb sig per window
            limits = (-1. - n_sig / n_sig_tot, 1.)
            if self._grid._plt_as == 'row':
                rect = (r, r - _off, s + margin, d + 2 * _off)
                sc_axis = 'x'
            elif self._grid._plt_as == 'col':
                rect = (r - _off, 1 - s, d + 2 * _off, s)
                sc_axis = 'y'
            return ScrollCamera(rect=rect, sc_axis=sc_axis, limits=limits,
                                smooth=n_sig_tot)
