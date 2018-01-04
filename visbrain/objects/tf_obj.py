"""Time-frequency map object."""
import logging
import numpy as np
from scipy.signal import spectrogram

from .image_obj import ImageObj
from ..utils import (morlet, averaging, normalization)
from ..io.dependencies import is_lspopt_installed

logger = logging.getLogger('visbrain')


class TimeFrequencyObj(ImageObj):
    """Compute the time-frequency map (or spectrogram).

    The time-frequency decomposition can be assessed using :

        * The fourier transform
        * Morlet's wavelet
        * Multi-taper

    Parameters
    ----------
    name : string | None
        Name of the time-frequency object.
    data : array_like
        Array of data of shape (N,)
    sf : float | 1.
        The sampling frequency.
    method : {'fourier', 'wavelet', 'multitaper'}
        The method to use to compute the time-frequency decomposition.
    nperseg : int | 256
        Length of each segment. Argument pass to the `scipy.signal.spectrogram`
        function (for 'fourier' and 'multitaper' method).
    overlap : float | 0.
        Overlap between segments. Must be between 0. and 1.
    f_min : float | 1.
        Minimum frequency (for 'wavelet' method).
    f_max : float | 160.
        Maximum frequency (for 'wavelet' method).
    f_step : float | 2.
        Frequency step between two consecutive frequencies (for 'wavelet'
        method).
    baseline : array_like | None
        Baseline period (for 'wavelet' method).
    norm : int | None
        The normalization type (for 'wavelet' method).. See the `normalization`
        function.
    n_window : int | None
        If this parameter is an integer, the time-frequency map is going to be
        averaged into smaller windows (for 'wavelet' method).
    window : {'flat', 'hanning', 'hamming', 'bartlett', 'blackman'}
        Windowing method for averaging. By default, 'flat' is used for Wavelet
        and 'hamming' for Fourier.
    c_parameter : int | 20
        Parameter 'c' described in doi:10.1155/2011/980805 (for 'multitaper'
        method)
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
    over : string/tuple/array_like | None
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
    >>> from visbrain.objects import TimeFrequencyObj
    >>> n, sf = 512, 256  # number of time-points and sampling frequency
    >>> time = np.arange(n) / sf  # time vector
    >>> data = np.sin(2 * np.pi * 25. * time) + np.random.rand(n)
    >>> tf = TimeFrequencyObj('tf', data, sf)
    >>> tf.preview(axis=True)
    """

    def __init__(self, name, data=None, sf=1., method='fourier', nperseg=256,
                 f_min=1., f_max=160., f_step=1., baseline=None, norm=None,
                 n_window=None, overlap=0., window=None, c_parameter=20,
                 cmap='viridis', clim=None, vmin=None, under='gray', vmax=None,
                 over='red', interpolation='nearest', max_pts=-1, parent=None,
                 transform=None, verbose=None, **kw):
        """Init."""
        # Initialize the image object :
        ImageObj.__init__(self, name, interpolation=interpolation,
                          max_pts=max_pts, parent=parent, transform=transform,
                          verbose=verbose, **kw)

        # Compute TF and set data to the ImageObj :
        if isinstance(data, np.ndarray):
            self.set_data(data, sf, method, nperseg, f_min, f_max, f_step,
                          baseline, norm, n_window, overlap, window,
                          c_parameter, clim, cmap, vmin, under, vmax, over)

    def set_data(self, data, sf=1., method='fourier', nperseg=256, f_min=1.,
                 f_max=160., f_step=1., baseline=None, norm=None,
                 n_window=None, overlap=0., window=None, c_parameter=20,
                 clim=None, cmap='viridis', vmin=None, under=None, vmax=None,
                 over=None):
        """Compute TF and set data to the ImageObj."""
        # ======================= CHECKING =======================
        assert isinstance(data, np.ndarray) and data.ndim == 1
        assert isinstance(sf, (int, float))
        assert method in ('fourier', 'wavelet', 'multitaper')
        if not isinstance(window, str):
            window = 'hamming' if method is 'fourier' else 'flat'
        assert 0. <= overlap < 1.
        # Wavelet args :
        assert isinstance(f_min, (int, float))
        assert isinstance(f_max, (int, float))
        assert isinstance(f_step, (int, float))
        # Spectrogram and Multi-taper args :
        noverlap = int(round(overlap * nperseg))
        assert isinstance(nperseg, int)
        assert isinstance(c_parameter, int)

        # Update color arguments :
        self._update_cbar_args(cmap, clim, vmin, vmax, under, over)
        logger.info("Compute time-frequency decomposition using the"
                    " %s method" % method)

        if method == 'fourier':
            freqs, time, tf = spectrogram(data, sf, nperseg=nperseg,
                                          noverlap=noverlap, window=window)
        if method == 'wavelet':
            n_pts = len(data)
            freqs = np.arange(f_min, f_max, f_step)
            time = np.arange(n_pts) / sf
            tf = np.zeros((len(freqs), n_pts), dtype=data.dtype)
            # Compute TF and inplace normalization :
            logger.info("Compute the time-frequency map ("
                        "normalization=%r)" % norm)
            for i, k in enumerate(freqs):
                tf[i, :] = np.square(np.abs(morlet(data, sf, k)))
            normalization(tf, norm=norm, baseline=baseline, axis=1)

            # Averaging :
            if isinstance(n_window, int):
                logger.info("Averaging time-frequency map using windows of "
                            "size %i with a %f overlap" % (n_window, overlap))
                kw = dict(overlap=overlap, window=window)
                tf = averaging(tf, n_window, axis=1, **kw)
                time = averaging(time, n_window, **kw)
        elif method == 'multitaper':
            is_lspopt_installed(raise_error=True)
            from lspopt import spectrogram_lspopt
            freqs, time, tf = spectrogram_lspopt(data, sf, nperseg=nperseg,
                                                 noverlap=noverlap,
                                                 c_parameter=c_parameter)

        # Set data to the image object :
        ImageObj.set_data(self, tf, xaxis=time, yaxis=freqs,
                          **self.to_kwargs())
