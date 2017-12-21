"""Test CrossSecObj."""
import numpy as np

from visbrain.objects import CrossSecObj
from visbrain.objects.tests._testing_objects import _TestObjects
from visbrain.io import download_file


cs_obj = CrossSecObj('brodmann')


class TestCrossSecObj(_TestObjects):
    """Test CrossSecObj."""

    OBJ = cs_obj

    def test_definition(self):
        """Test class definition."""
        for k in ['brodmann', 'aal', 'talairach']:
            CrossSecObj(k)
        CrossSecObj('test', vol=np.random.rand(100, 100, 100))

    def test_set_data(self):
        """Test method set_data."""
        cs_obj.set_data((14, 15, 50))

    def test_localize_source(self):
        """Test function localize_source."""
        cs_obj.localize_source((15., 12., 23.))

    def test_nii_definition(self):
        """Test function nii_definition."""
        CrossSecObj(download_file('GG-853-GM-0.7mm.nii.gz'))
