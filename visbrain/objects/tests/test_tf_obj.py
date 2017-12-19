"""Test TimeFrequencyMapObj."""
import numpy as np

from visbrain.objects.tests._testing_objects import _TestObjects
from visbrain.objects import TimeFrequencyMapObj, SpectrogramObj

tf_obj = TimeFrequencyMapObj('TF', np.random.rand(1000))
sp_obj = SpectrogramObj('Spec', np.random.rand(1000))


class TestTFObj(_TestObjects):
    """Test TimeFrequencyMapObj object."""

    OBJ = tf_obj

    def test_definition(self):
        """Test function definition."""
        TimeFrequencyMapObj('TF_None')
        TimeFrequencyMapObj('TF_Data1D', np.random.rand(100))

    def test_set_data(self):
        """Test set_data method."""
        data = np.random.rand(200)
        tf_obj.set_data(data, n_window=10, cmap='plasma', clim=(-1., 1.),
                        vmin=-.8, vmax=.8, under='orange', over='blue', norm=3)


class TestSpecObj(_TestObjects):
    """Test SpectrogramObj object."""

    OBJ = sp_obj

    def test_definition(self):
        """Test function definition."""
        SpectrogramObj('Spec_None')
        SpectrogramObj('Spec_Data1D', np.random.rand(1000))

    def test_set_data(self):
        """Test set_data method."""
        data = np.random.rand(200)
        sp_obj.set_data(data, nperseg=10, overlap=.5, cmap='plasma',
                        clim=(-1., 1.), vmin=-.8, vmax=.8, under='orange',
                        over='blue')
