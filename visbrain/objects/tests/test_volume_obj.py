"""Test VolumeObj."""
import numpy as np

from visbrain.objects.tests._testing_objects import _TestVolumeObject
from visbrain.objects import VolumeObj


v_obj = VolumeObj('aal')


class TestVolumeObj(_TestVolumeObject):
    """Test BrainObj."""

    OBJ = v_obj

    def test_definition(self):
        """Test function definition."""
        for k in ['aal', 'brodmann', 'talairach']:
            VolumeObj(k)
        VolumeObj('vol', vol=np.random.rand(10, 20, 30))

    def test_properties(self):
        """Test function properties."""
        for k in ['mip', 'translucent', 'additive', 'iso']:
            self.assert_and_test('method', k)
        for k in ['OpaqueGrays', 'TransFire', 'OpaqueFire', 'TransGrays']:
            self.assert_and_test('cmap', k)
        self.assert_and_test('threshlod', 5)
