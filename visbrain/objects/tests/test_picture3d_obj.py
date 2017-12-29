"""Test Picture3DObj."""
import numpy as np

from visbrain.objects.picture3d_obj import Picture3DObj, CombinePictures
from visbrain.objects.tests._testing_objects import _TestObjects


n_sources = 20
pic_data = 100 * np.random.rand(n_sources, 10, 20)
pic_xyz = np.random.uniform(-20, 20, (n_sources, 3))
pic_select = np.random.randint(0, n_sources, (int(n_sources / 2),))

p_obj = Picture3DObj('P1', pic_data, pic_xyz, select=pic_select, pic_width=8.,
                     pic_height=5., alpha=.7, cmap='inferno', clim=(1., 90.),
                     vmin=5.1, vmax=84.1, under='orange', over='blue')

p_comb = CombinePictures([p_obj, p_obj])


class TestPicture3DObj(_TestObjects):
    """Test picture object."""

    OBJ = p_obj

    def test_definition(self):
        """Test function definition."""
        Picture3DObj('P1', pic_data, pic_xyz, select=pic_select)

    def test_builtin_methods(self):
        """Test function connect_builtin_methods."""
        assert len(p_obj) == n_sources

    def test_attributes(self):
        """Test function connect_attributes."""
        self.assert_and_test('width', 4.4)
        self.assert_and_test('height', 1.4)
        self.assert_and_test('translate', (1., 2., 3.))
        self.assert_and_test('alpha', 0.4)


class TestCombinePictures(object):
    """Test combine picture objects."""

    def test_definition(self):
        """Test object definition."""
        CombinePictures([p_obj, p_obj])
        CombinePictures(p_obj)
