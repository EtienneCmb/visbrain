"""Test PacmapObj."""
import numpy as np

from visbrain.objects.tests._testing_objects import _TestObjects
from visbrain.objects import PacmapObj


sig = np.random.rand(10000)
sf = 1024.
pac_obj = PacmapObj('pac', sig, sf=sf, f_pha=(2, 30, 5, 4),
                    f_amp=(60, 100, 10, 5))


class TestTFObj(_TestObjects):
    """Test TimeFrequencyObj object."""

    OBJ = pac_obj

    def test_definition(self):
        """Test function definition."""
        PacmapObj('pac')
        PacmapObj('pac', sig, sf=sf)

    def test_stable_phase(self):
        """Test stable phase."""
        PacmapObj('pac', sig, sf=sf, f_pha=[5, 7], f_amp=(60, 100, 10, 5),
                  n_window=1000)

    def test_stable_amplitude(self):
        """Test stable amplitude."""
        PacmapObj('pac', sig, sf=sf, f_pha=(2, 30, 5, 4), f_amp=[60, 100],
                  n_window=1000)
