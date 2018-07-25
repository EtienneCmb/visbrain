"""Test functions in sigproc.py."""
import numpy as np
from itertools import product

from vispy.visuals.transforms import STTransform, NullTransform

from visbrain.utils.sigproc import (normalize, derivative, tkeo, zerocrossing,
                                    power_of_ten, averaging, normalization,
                                    smoothing, smooth_3d)


class TestSigproc(object):
    """Test functions in sigproc.py."""

    def test_normalize(self):
        """Test normalize function."""
        mat = np.random.rand(10, 20)
        mat_n = normalize(mat, -10., 14.)
        assert (mat_n.min() == -10.) and (mat_n.max() == 14.)

    def test_derivative(self):
        """Test function derivative."""
        x, window, sf = np.random.rand(2000), 10., 512.
        derivative(x, window, sf)

    def test_tkeo(self):
        """Test function tkeo."""
        x = np.random.rand(2000)
        tkeo(x)

    def test_zerocrossing(self):
        """Test function zerocrossing."""
        x = np.array([1., -10, -4, 2., 4., -7., -1., 5.])
        assert np.array_equal(zerocrossing(x), [1, 3, 5, 7])

    def test_power_of_ten(self):
        """Test function power_of_ten."""
        assert np.allclose(power_of_ten(-57.), (-57., 0))
        assert np.allclose(power_of_ten(1024.), (1.024, 3))
        assert np.allclose(power_of_ten(-14517.2), (-1.45172, 4))

    def test_averaging(self):
        """Test function averaging."""
        data = np.random.rand(57, 103, 154)
        # Test axis
        for x in [0, 1, 2, -1]:
            ts_out = averaging(data, 5, axis=x, overlap=.5)
            assert ts_out.shape[x] < data.shape[x]
        # Test window :
        window = ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']
        for w in window:
            averaging(data, 5, axis=-1, overlap=.5, window=w)

    def test_normalization(self):
        """Test function normalization."""
        data = np.random.rand(10, 20)
        # Test the different normalizations using a baseline or not :
        for norm, base in product(range(5), [None, (2, 7)]):
            normalization(data, -1, norm, base)

    def test_smoothing(self):
        """Test function smoothing."""
        # Test small vector :
        x_3 = np.array([0, 1, 2])
        assert np.array_equal(smoothing(x_3, n_window=1), x_3)
        # Test windows :
        x_n = np.arange(127)
        window = ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']
        for w in window:
            x_ns = smoothing(x_n, window=w)
            assert len(x_ns) == len(x_n)

    def test_smooth_3d(self):
        """Test function smooth_3d."""
        x = np.random.rand(10, 20, 30)
        # Smoothing without correction :
        xm, tf_1 = smooth_3d(x, correct=False)
        assert isinstance(tf_1, NullTransform)
        # Smoothing with correction :
        xm, tf_2 = smooth_3d(x, correct=True)
        assert isinstance(tf_2, STTransform)
