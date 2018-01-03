"""Test VectorObj."""
import numpy as np

from visbrain.objects.tests._testing_objects import _TestObjects
from visbrain.objects.vector_obj import VectorObj, CombineVectors


n_arrows = 10
arrows = [np.random.rand(n_arrows, 3), np.random.rand(n_arrows, 3)]
data = np.random.rand(n_arrows)

v_obj = VectorObj('V1', arrows, data=data)
v_comb = CombineVectors([v_obj, v_obj])


class TestVectorObj(_TestObjects):
    """Test vector object."""

    OBJ = v_obj

    def test_definition(self):
        """Test function definition."""
        # List of positions :
        VectorObj('V1_0', arrows, data=data)
        VectorObj('V1_1', arrows, inferred_data=True)
        # Dtype (start, end) :
        dt_se = np.dtype([('start', float, 3), ('end', float, 3)])
        arr = np.zeros(10, dtype=dt_se)
        arr['start'] = np.random.rand(10, 3)
        arr['end'] = np.random.rand(10, 3)
        VectorObj('V1_2', arr)
        # Dtype (vertices, normals) :
        dt_vn = np.dtype([('vertices', float, 3), ('normals', float, 3)])
        arrows_vn = np.zeros(10, dtype=dt_vn)
        arrows_vn['vertices'] = np.random.rand(10, 3)
        arrows_vn['normals'] = np.random.rand(10, 3)
        VectorObj('VN', arrows_vn, dynamic=(.3, .8))

    def test_builtin_methods(self):
        """Test function connect_builtin_methods."""
        assert len(v_obj) == n_arrows

    def test_attributes(self):
        """Test function connect_attributes."""
        from vispy.visuals.line.arrow import ARROW_TYPES
        self.assert_and_test('line_width', 4.4)
        for k in ARROW_TYPES:
            self.assert_and_test('arrow_type', k)
        self.assert_and_test('arrow_size', 21)


class TestCombineVector(object):
    """Test combine conectivity objects."""

    def test_definition(self):
        """Test object definition."""
        CombineVectors(v_obj)
        CombineVectors([v_obj, v_obj])
