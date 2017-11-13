"""Spectrogram object."""
import numpy as np
from scipy.signal import spectrogram

from .image_obj import ImageObj


class SpectrogramObj(ImageObj):
    """Create a spectrogram object.

    Parameters
    ----------
    name : string | None
        Name of the time-frequency object.
    data : array_like
        Array of data of shape (N,)
    sf : float | 1.
        The sampling frequency.
    nperseg : int | 256
        Length of each segment. Argument pass to the `scipy.signal.spectrogram`
        function.
    overlap : float | 0.
        Overlap between segemnts. Must be between 0. and 1.
    window : string | 'hamming'
        Desired window to use. Argument pass to the `scipy.signal.spectrogram`
        function.
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

    Examples
    --------
    >>> import numpy as np
    >>> from visbrain.objects import SpectrogramObj
    >>> n, sf = 512, 256  # number of time-points and sampling frequency
    >>> time = np.arange(n) / sf  # time vector
    >>> data = np.sin(2 * np.pi * 25. * time) + np.random.rand(n)
    >>> spec = SpectrogramObj('spec', data, sf)
    >>> spec.preview(axis=True)
    """

    def __init__(self, name, data, sf=1., nperseg=256, overlap=0.,
                 window='hamming', cmap='viridis', clim=None, vmin=None,
                 under='gray', vmax=None, over='red', interpolation='nearest',
                 max_pts=-1, parent=None, transform=None, verbose=None,
                 **kwargs):
        """Init."""
        # Initialize the image object :
        ImageObj.__init__(self, name, interpolation=interpolation,
                          max_pts=max_pts, parent=parent, transform=transform,
                          verbose=verbose)

        # Compute spectrogram and set data to the ImageObj :
        if isinstance(data, np.ndarray):
            self.set_data(data, sf, nperseg, overlap, window, clim, cmap,
                          vmin, under, vmax, over, **kwargs)

    def set_data(self, data, sf=1., nperseg=None, overlap=None,
                 window='hamming', clim=None, cmap=None, vmin=None, under=None,
                 vmax=None, over=None, **kwargs):
        """Compute spectrogram and set data to the ImageObj."""
        assert isinstance(data, np.ndarray) and data.ndim == 1
        assert isinstance(sf, (int, float))
        assert isinstance(nperseg, int)
        assert 0. <= overlap < 1.
        noverlap = int(round(overlap * nperseg))

        # Compute spectrogram :
        kwargs['nperseg'] = nperseg
        kwargs['noverlap'] = noverlap
        kwargs['window'] = window
        freqs, time, tf = spectrogram(data, sf, **kwargs)

        # Set data to the image object :
        ImageObj.set_data(self, tf, xaxis=time, yaxis=freqs, clim=clim,
                          cmap=cmap, vmin=vmin, vmax=vmax, under=under,
                          over=over)
