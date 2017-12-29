"""Time-frequency maps visual base class.

Authors: Etienne Combrisson <e.combrisson@gmail.com>

License: BSD (3-clause)
"""
import numpy as np

import vispy.visuals.transforms as vist
from vispy.scene.visuals import Image

from ..visuals import CbarBase
from ..utils import (morlet, array2colormap, vispy_array, averaging,
                     normalization)


__all__ = ('TFmapsMesh')


class TFmapsMesh(CbarBase):
    """Visual class for time-frequency maps.

    Parameters
    ----------
    data : array_like
        Array of data of shape (N,)
    sf : float
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
        The normalization method.
    """

    def __init__(self, parent=None, interpolation='nearest'):
        """Init."""
        CbarBase.__init__(self)
        self._cblabel = 'Time-frequency map'
        # Visualization of large images can occur GL bugs. So we fix a limit
        # number of time points :
        self._n_limits = 4000
        # Initialize image object :
        pos = np.random.rand(2, 2, 4)
        self._image = Image(parent=parent, interpolation=interpolation)
        self._image.transform = vist.STTransform()
        self._image.set_data(pos)

    def __len__(self):
        """Return the number of time points."""
        return self._n

    def set_data(self, data, sf, f_min=1., f_max=160., f_step=1.,
                 baseline=None, norm=3, contrast=.1, n_window=None,
                 overlap=0., window='flat', **kwargs):
        """Set data to the time frequency map.

        Parameters
        ----------
        data : array_like
            Array of data of shape (N,)
        sf : float
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
        """
        # ======================= CHECKING =======================
        assert isinstance(data, np.ndarray) and data.ndim == 1
        assert isinstance(sf, (int, float))
        assert isinstance(f_min, (int, float))
        assert isinstance(f_max, (int, float))
        assert isinstance(f_step, (int, float))
        # assert isinstance(baseline)

        # ======================= PRE-ALLOCATION =======================
        self._n = len(data)
        freqs = np.arange(f_min, f_max, f_step)  # frequency vector
        time = np.arange(len(self)) / sf
        tf = np.zeros((len(freqs), len(self)), dtype=data.dtype)

        # ======================= COMPUTE TF =======================
        for i, k in enumerate(freqs):
            tf[i, :] = np.square(np.abs(morlet(data, sf, k)))

        # ======================= NORMALIZATION =======================
        normalization(tf, norm=norm, baseline=baseline, axis=1)

        # ======================= AVERAGING =======================
        if isinstance(n_window, int):
            tf = averaging(tf, n_window, axis=1, overlap=overlap,
                           window=window)

        # ======================= DOWNSAMPLE =======================
        # Downsample large images :
        if tf.shape[1] > self._n_limits:
            downsample = int(np.round(tf.shape[1] / self._n_limits))
            tf = tf[:, ::downsample]

        # ======================= CLIM // CMAP =======================
        # Get contrast (if defined) :
        self._clim = kwargs.get('clim', None)
        if isinstance(contrast, (int, float)) and (self._clim is None):
            self._clim = (tf.min() * contrast, tf.max() * contrast)
        if self._clim is None:
            self._clim = (tf.min(), tf.max())
        kwargs['clim'] = self._clim
        # Cmap :
        self._cmap = kwargs.get('cmap', 'viridis')

        # ======================= COLOR =======================
        cmap = array2colormap(tf, **kwargs)
        self._image.set_data(vispy_array(cmap))

        # ======================= SCALE // TRANSLATE =======================
        # Scale and translate TF :
        t_min, t_max = time.min(), time.max()
        fr_min, fr_max = freqs.min(), freqs.max()
        # Re-scale the mesh for fitting in time / frequency :
        fact = (fr_max - fr_min) / len(freqs)
        sc = (t_max / tf.shape[1], fact, 1)
        tr = [0., fr_min, 0.]
        self._image.transform.scale = sc
        self._image.transform.translate = tr

        # ======================= CAMERA =======================
        self.rect = (time[0], f_min, t_max - t_min, fr_max - fr_min)
        self.freqs = freqs

    def update(self):
        """Update image."""
        self._image.update()

    # ----------- VISIBLE -----------
    @property
    def visible(self):
        """Get the visible value."""
        return self._visible

    @visible.setter
    def visible(self, value):
        """Set visible value."""
        self._visible = value
        self._image.visible = value

    # ----------- INTERPOLATION -----------
    @property
    def interpolation(self):
        """Get the interpolation value."""
        return self._interpolation

    @interpolation.setter
    def interpolation(self, value):
        """Set interpolation value."""
        self._interpolation = value
        self._image.interpolation = value
