"""Time-frequency map object."""
import logging
import numpy as np

from .image_obj import ImageObj
from ..utils import (morlet, averaging, normalization)

logger = logging.getLogger('visbrain')


class TimeFrequencyMapObj(ImageObj):
    """Create a time-frequency map object.

    Parameters
    ----------
    name : string | None
        Name of the time-frequency object.
    data : array_like
        Array of data of shape (N,)
    sf : float | 1.
        The sampling frequency.
    f_min : float | 1.
        Minimum frequency.
    f_max : float | 160.
        Maximum frequency.
    f_step : float | 2.
        Frequency step between two consecutive frequencies.
    baseline : array_like | None
        Baseline period.
    norm : int | None
        The normalization method. See the `normalization` function.
    n_window : int | None
        If this parameter is an integer, the time-frequency map is going to be
        averaged into smaller windows.
    overlap : float | 0.
        Overlap between consecutive windows during averaging. `overlap` must be
        between 0. and 1.
    window : {'flat', 'hanning', 'hamming', 'bartlett', 'blackman'}
        Windowing method for averaging.
    clim : tuple | None
        Colorbar limits. If None, `clim=(data.min(), data.max())`
    cmap : string | None
        Colormap name.
    vmin : float | None
        Minimum threshold of the colorbar.
    under : string/tuple/array_like | None
        Color for values under vmin.
    vmax : float | None
        Maximum threshold of the colorbar.
    under : string/tuple/array_like | None
        Color for values over vmax.
    interpolation : string | 'nearest'
        Interpolation method for the image. See vispy.scene.visuals.Image for
        availables interpolation methods.
    max_pts : int | -1
        Maximum number of points of the image along the x or y axis. This
        parameter is essentially used to solve OpenGL issues with very large
        images.
    transform : VisPy.visuals.transforms | None
        VisPy transformation to set to the parent node.
    parent : VisPy.parent | None
        Markers object parent.
    verbose : string
        Verbosity level.
    kw : dict | {}
        Optional arguments are used to control the colorbar
        (See :class:`ColorbarObj`).

    Examples
    --------
    >>> import numpy as np
    >>> from visbrain.objects import TimeFrequencyMapObj
    >>> n, sf = 512, 256  # number of time-points and sampling frequency
    >>> time = np.arange(n) / sf  # time vector
    >>> data = np.sin(2 * np.pi * 25. * time) + np.random.rand(n)
    >>> tf = TimeFrequencyMapObj('tf', data, sf)
    >>> tf.preview(axis=True)
    """

    def __init__(self, name, data=None, sf=1., f_min=1., f_max=160., f_step=1.,
                 baseline=None, norm=None, n_window=None, overlap=0.,
                 window='flat', cmap='viridis', clim=None, vmin=None,
                 under='gray', vmax=None, over='red', interpolation='nearest',
                 max_pts=-1, parent=None, transform=None, verbose=None, **kw):
        """Init."""
        # Initialize the image object :
        ImageObj.__init__(self, name, interpolation=interpolation,
                          max_pts=max_pts, parent=parent, transform=transform,
                          verbose=verbose, **kw)

        # Compute TF and set data to the ImageObj :
        if isinstance(data, np.ndarray):
            self.set_data(data, sf, f_min, f_max, f_step, baseline, norm,
                          n_window, overlap, window, clim, cmap, vmin, under,
                          vmax, over)

    def set_data(self, data, sf=1., f_min=1., f_max=160., f_step=1.,
                 baseline=None, norm=None, n_window=None, overlap=0.,
                 window='flat', clim=None, cmap=None, vmin=None, under=None,
                 vmax=None, over=None):
        """Compute TF map and set data to the ImageObj."""
        # ======================= CHECKING =======================
        assert isinstance(data, np.ndarray) and data.ndim == 1
        assert isinstance(sf, (int, float))
        assert isinstance(f_min, (int, float))
        assert isinstance(f_max, (int, float))
        assert isinstance(f_step, (int, float))
        # assert isinstance(baseline)
        self._update_cbar_args(cmap, clim, vmin, vmax, under, over)

        # Predefined variables :
        n_pts = len(data)
        freqs = np.arange(f_min, f_max, f_step)
        time = np.arange(n_pts) / sf
        tf = np.zeros((len(freqs), n_pts), dtype=data.dtype)

        # Compute TF and inplace normalization :
        logger.info('Compute the time-frequency map (normalization=%r)' % norm)
        for i, k in enumerate(freqs):
            tf[i, :] = np.square(np.abs(morlet(data, sf, k)))
        normalization(tf, norm=norm, baseline=baseline, axis=1)

        # Averaging :
        if isinstance(n_window, int):
            logger.info("Averaging time-frequency map using windows of size %i"
                        " with a %f overlap" % (n_window, overlap))
            tf = averaging(tf, n_window, axis=1, overlap=overlap,
                           window=window)
            time = averaging(time, n_window, overlap=overlap, window=window)

        # Set data to the image object :
        ImageObj.set_data(self, tf, xaxis=time, yaxis=freqs,
                          **self.to_kwargs())
