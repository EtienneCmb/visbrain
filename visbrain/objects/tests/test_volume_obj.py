"""Test VolumeObj."""
import numpy as np

from visbrain.objects.tests._testing_objects import _TestVolumeObject
from visbrain.objects import VolumeObj
from visbrain.io import download_file, clean_tmp


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

    def test_extract_activity(self):
        """Test function extract_activity."""
        xyz = np.random.uniform(-20, 20, (100, 3))
        v_obj.extract_activity(xyz, radius=10.)

    def test_nii_definition(self):
        """Test function nii_definition."""
        VolumeObj(download_file('GG-853-GM-0.7mm.nii.gz',
                                astype='example_data'))

    def test_save(self):
        """Test function save."""
        v_obj = VolumeObj(download_file('GG-853-GM-0.7mm.nii.gz',
                                        astype='example_data'))
        v_obj.save()
        v_obj.save(tmpfile=True)

    def test_remove(self):
        """Test function remove."""
        v_obj = VolumeObj('GG-853-GM-0.7mm')
        v_obj.remove()
        clean_tmp()
