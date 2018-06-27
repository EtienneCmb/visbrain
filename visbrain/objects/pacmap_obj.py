"""Pacmap object."""
import numpy as np

from .image_obj import ImageObj
from ..io.dependencies import is_tensorpac_installed


class PacmapObj(ImageObj):
    """Create a Phase-Amplitude Coupling (PAC) object.

    The PAC is computed using the tensorpac package.

    The Pacmap can be used to visualize :

        * PAC, across time for a fixed phase and several amplitude frequencies
        * PAC, across time for a fixed amplitude and several phase frequencies
        * PAC is computed across time for several amplitudes and phase.

    Parameters
    ----------
    name : string | None
        Name of the pacmap object.
    data : array_like
        Array of data of shape (N,)
    sf : float | 1.
        The sampling frequency.
    f_pha : list | [(2, 4), (5, 7), (8, 13)]
        The phase vector.
    f_amp : list | [(40, 60), (60, 100)]
        The amplitude vector.
    idpac : tuple | (4, 0, 0)
        The PAC method to use.
    n_window : int | None
        Number of time points to consider when computing pac for a fixed phase
        or amplitude.
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

    Notes
    -----
    List of supported shortcuts :

        * **s** : save the figure
        * **<delete>** : reset camera

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

    def __init__(self, name, data=None, sf=1., f_pha=[(2, 4), (5, 7), (8, 13)],
                 f_amp=[(40, 60), (60, 100)], idpac=(4, 0, 0), n_window=None,
                 cmap='viridis', clim=None, vmin=None, under='gray', vmax=None,
                 over='red', interpolation='nearest', max_pts=-1, parent=None,
                 transform=None, verbose=None, pac_kw={}, **kw):
        """Init."""
        # Initialize the image object :
        ImageObj.__init__(self, name, interpolation=interpolation,
                          max_pts=max_pts, parent=parent, transform=transform,
                          verbose=verbose, **kw)

        # Compute pacmap and set data to the ImageObj :
        if isinstance(data, np.ndarray):
            self.set_data(data, sf, f_pha, f_amp, idpac, n_window, clim, cmap,
                          vmin, under, vmax, over, **pac_kw)

    def set_data(self, data, sf=1., f_pha=[(2, 4), (5, 7), (8, 13)],
                 f_amp=[(40, 60), (60, 100)], idpac=(4, 0, 0), n_window=None,
                 clim=None, cmap=None, vmin=None, under=None, vmax=None,
                 over=None, **kwargs):
        """Compute pacmap and set data to the ImageObj."""
        # ======================= CHECKING =======================
        is_tensorpac_installed(raise_error=True)
        from tensorpac import Pac
        data = np.squeeze(data)
        assert isinstance(data, np.ndarray) and data.ndim == 1
        assert isinstance(sf, (int, float))
        time = np.arange(len(data))
        # Switch between several plotting capabilities :
        _pha = len(f_pha) == 2 and all([isinstance(k, (int,
                                                       float)) for k in f_pha])
        _amp = len(f_amp) == 2 and all([isinstance(k, (int,
                                                       float)) for k in f_amp])
        if _pha or _amp:
            assert isinstance(n_window, int)
            sections = time.copy()[::n_window][1::]
            time = np.array(np.array_split(time, sections)[0:-1]).mean(1).T
            time /= sf
            data = np.array(np.array_split(data, sections)[0:-1]).T
        # Define the pac object and compute pac :
        p = Pac(idpac=idpac, fpha=f_pha, famp=f_amp, **kwargs)
        pac = np.squeeze(p.filterfit(sf, data, njobs=1, axis=0))
        pac[np.isnan(pac)] = 0.
        assert pac.ndim == 2
        # Get x-axis and y-axis :
        if _pha:
            xaxis, yaxis = time, p.yvec
        elif _amp:
            xaxis, yaxis = time, p.xvec
        else:
            xaxis, yaxis = p.xvec, p.yvec
        # Update color arguments :
        self._update_cbar_args(cmap, clim, vmin, vmax, under, over)

        # Set data to the image object :
        ImageObj.set_data(self, pac, xaxis=xaxis, yaxis=yaxis,
                          **self.to_kwargs())
