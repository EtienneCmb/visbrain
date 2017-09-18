""""""
import numpy as np

import vispy.visuals.transforms as vist
from vispy.scene.visuals import Image

from visbrain.utils import morlet, array2colormap, vispy_array


__all__ = ('TFmapsMesh')


class TFmapsMesh(object):
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
    normalize : int | None
        The normalization method.
    """

    def __init__(self, parent=None):
        """Init."""
        # Visualization of large images can occur GL bugs. So we fix a limit
        # number of time points :
        self._n_limits = 6000
        # Initialize image object :
        pos = np.random.rand(2, 2, 4)
        self._image = Image(parent=parent, interpolation='bilinear')
        self._image.transform = vist.STTransform()
        self._image.set_data(pos)
        # Set data :
        # self.set_data(*args, **kwargs)

    def __len__(self):
        """Return the number of time points."""
        return self._n

    def set_data(self, data, sf, f_min=1., f_max=200., f_step=2.,
                 baseline=None, **kwargs):
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
        normalize : int | None
            The normalization method.
        """
        # ======================= CHECKING =======================
        assert isinstance(data, np.ndarray) and data.ndim == 1
        assert isinstance(sf, (int, float))
        assert isinstance(f_min, (int, float))
        assert isinstance(f_max, (int, float))
        assert isinstance(f_step, (int, float))
        # assert isinstance(baseline)
        self._n = len(data)
        # Define frequency vector :
        freqs = np.arange(f_min, f_max, f_step)
        # Pre-allocate TF data :
        tf = np.zeros((len(freqs), len(self)), dtype=np.float32)
        time = np.arange(len(self)) / sf
        # Compute TF :
        for i, k in enumerate(freqs):
            tf[i, :] = np.square(np.abs(morlet(data, sf, k)))
        # Downsample large images :
        if len(self) > self._n_limits:
            downsample = int(np.round(len(self) / self._n_limits))
            tf = tf[:, ::downsample]
        # Get then set color :
        cmap = array2colormap(tf, **kwargs)[..., 0:3]
        self._image.set_data(vispy_array(cmap))
        # Scale and translate TF :
        t_min, t_max = time.min(), time.max()
        fr_min, fr_max = freqs.min(), freqs.max()
        # Re-scale the mesh for fitting in time / frequency :
        fact = (fr_max - fr_min) / len(freqs)
        sc = (t_max / tf.shape[1], fact, 1)
        tr = [0., fr_min, 0.]
        self._image.transform.scale = sc
        self._image.transform.translate = tr
        self.rect = (time[0], f_min, t_max - t_min, fr_max - fr_min)

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
