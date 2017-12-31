"""Test TimeFrequencyObj."""
import numpy as np

from visbrain.objects.tests._testing_objects import _TestObjects
from visbrain.objects import TimeFrequencyObj

tf_obj = TimeFrequencyObj('TF', np.random.rand(1000))


class TestTFObj(_TestObjects):
    """Test TimeFrequencyObj object."""

    OBJ = tf_obj

    def test_definition(self):
        """Test function definition."""
        TimeFrequencyObj('TF_None')
        TimeFrequencyObj('TF_Data1D', np.random.rand(100))

    def test_fourier(self):
        """Compute time-frequency using fourier method."""
        data = np.random.rand(200)
        tf_obj.set_data(data, method='fourier', nperseg=10, overlap=.5,
                        cmap='plasma', clim=(-1., 1.), vmin=-.8, vmax=.8,
                        under='orange', over='blue')

    def test_wavelet(self):
        """Compute time-frequency using wavelet method."""
        data = np.random.rand(200)
        tf_obj.set_data(data, method='wavelet', n_window=10, cmap='plasma',
                        clim=(-1., 1.), vmin=-.8, vmax=.8, under='orange',
                        over='blue', norm=3)

    def test_multitaper(self):
        """Compute time-frequency using multitaper method."""
        data = np.random.rand(200)
        tf_obj.set_data(data, method='multitaper', nperseg=10, overlap=.5,
                        cmap='plasma', clim=(-1., 1.), vmin=-.8, vmax=.8,
                        under='orange', over='blue')
