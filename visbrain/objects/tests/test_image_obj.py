"""Test ImageObj."""
import numpy as np

from visbrain.objects import ImageObj
from visbrain.objects.tests._testing_objects import _TestObjects

im_data = np.random.rand(10, 20)
im_obj = ImageObj('IM1', im_data)


class TestImageObj(_TestObjects):
    """Test image object."""

    OBJ = im_obj

    def test_definition(self):
        """Test function definition."""
        ImageObj('Im_Data_2D', np.random.rand(10, 20))
        ImageObj('Im_Data_3D_RGB', np.random.rand(10, 20, 3))
        ImageObj('Im_Data_3D_RGBA', np.random.rand(10, 20, 4))

    def test_preview(self):
        """Test function preview."""
        im_obj.preview(show=False, axis=False)

    def test_get_camera(self):
        """Test function get_camera."""
        im_obj._get_camera()

    def test_set_data(self):
        """Test set_data method."""
        data_1 = np.random.rand(10, 20)
        data_2 = np.random.rand(10, 20, 3)
        data_3 = np.random.rand(10, 20, 4)
        y_axis = np.arange(10) / 10.
        x_axis = np.arange(20) / 20.
        for data in (data_1, data_2, data_3):
            im_obj.set_data(data, xaxis=x_axis, yaxis=y_axis, cmap='plasma',
                            clim=(-1., 1.), vmin=-.8, vmax=.8, under='orange',
                            over='blue')

    def test_attributes(self):
        """Test image object attributes."""
        self.assert_and_test('interpolation', 'bicubic')
        self.assert_and_test('cmap', 'inferno')
        self.assert_and_test('vmin', -1.)
        self.assert_and_test('clim', (-2., 2.))
        self.assert_and_test('vmax', 1.)
        self.assert_and_test('under', np.array([0., 0., 0., 0.]))
        self.assert_and_test('over', np.array([1., 1., 1., 1.]))
