import numpy as np

from visbrain.objects import BrainObj
from visbrain.objects.tests._testing_objects import _TestObjects


b_obj = BrainObj('B1')
n_vertices, n_faces = 100, 50
vertices_x3 = 20. * np.random.rand(n_vertices, 3, 3)
vertices = 20. * np.random.rand(n_vertices, 3)
normals = (vertices >= 0).astype(float)
faces = np.random.randint(0, n_vertices, (n_faces, 3))


class TestBrainObj(_TestObjects):
    """Test BrainObj."""

    def _prepare_brain(self, name='inflated'):
        b_obj.set_data(name)
        b_obj.clean()

    def test_definition(self):
        """Test function definition."""
        BrainObj('B1')
        # Test default templates :
        for k, i in zip(['B1', 'B2', 'B3'], ['left', 'both', 'right']):
            b_obj.set_data(name=k, hemisphere=i)
        # Test downloadable templates :
        for k in ['inflated', 'white', 'sphere']:
            b_obj.set_data(k)
        # Test custom (vertices, faces) :

    def test_custom_templates(self):
        """Test passing vertices, faces and normals."""
        b_obj.set_data(name='Curstom', vertices=vertices, faces=faces)
        b_obj.set_data(name='Curstom', vertices=vertices, faces=faces,
                       normals=normals)

    def test_add_activation(self):
        pass

    def test_projection(self):
        pass

    # def test_properties(self):
    #     self._assert_and_test(b_obj, 'translucent', True)
    #     self._assert_and_test(b_obj, 'alpha', .03)
    #     self._assert_and_test(b_obj, 'hemisphere', 'both')
    #     self._assert_and_test(b_obj, 'scale', 1.)
        