"""Test VispyObj."""
import numpy as np
from vispy.scene import visuals

from visbrain.objects.tests._testing_objects import _TestObjects
from visbrain.objects import VispyObj


pos = np.array([[0., 0., 0.], [10., 10., 10.]])
line = visuals.Line(pos=pos, method='agg')
vp_obj = VispyObj('v', line)


class TestVispyObj(_TestObjects):
    """Test ColorbarObj."""

    OBJ = vp_obj

    def test_definition(self):
        """Test definition."""
        pos = np.array([[0., 0., 0.], [10., 10., 10.]])
        line = visuals.Line(pos=pos, method='agg')
        VispyObj('v', line)
