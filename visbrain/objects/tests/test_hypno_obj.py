"""Test the HypnogramObj."""
import numpy as np

from visbrain.objects.hypno_obj import HypnogramObj
from visbrain.objects.tests._testing_objects import _TestObjects
from visbrain.io import path_to_visbrain_data


data = np.repeat(np.arange(6), 100) - 1.
h_obj = HypnogramObj('hypno', data)
hypno_file = path_to_visbrain_data('Hypnogram_excerpt2.txt', 'example_data')


class TestHypnogramObj(_TestObjects):
    """Test connectivity object."""

    OBJ = h_obj

    def test_definition(self):
        """Test function definition."""
        HypnogramObj('hypno', data)
        HypnogramObj(hypno_file)

    def test_set_stage(self):
        """Test set stage."""
        h_obj.set_stage(-1, 45, 89)
        h_obj.set_stage('wake', 145, 189)

    def test_properties(self):
        """Test hypnogram object properties."""
        self.assert_and_test('line_width', 4.)
        self.assert_and_test('unicolor', True)
