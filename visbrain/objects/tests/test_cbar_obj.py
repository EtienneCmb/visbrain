"""Test ColorbarObj."""
import numpy as np

from visbrain.objects.tests._testing_objects import _TestObjects
from visbrain.objects import (SourceObj, ConnectObj, BrainObj, ImageObj,
                              ColorbarObj)

cbar_obj = ColorbarObj('cbar', cmap='inferno')


class TestColorbarObj(_TestObjects):
    """Test ColorbarObj."""

    OBJ = cbar_obj

    def test_definition(self):
        """Test definition."""
        ColorbarObj('cbar')

    def test_update_cbar_from_obj(self):
        """Test function update_cbar_from_obj."""
        xyz = np.random.rand(10, 3)
        edges = np.random.rand(10, 10)
        s_obj = SourceObj('S1', xyz)
        b_obj = BrainObj('B1')
        c_obj = ConnectObj('C1', xyz, edges)
        im_obj = ImageObj('IM1', np.random.rand(10, 10))
        ColorbarObj(s_obj)
        ColorbarObj(c_obj)
        ColorbarObj(b_obj)
        ColorbarObj(im_obj)
