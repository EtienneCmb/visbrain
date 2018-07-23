"""Utility function for Visbrain tests."""
import os
import numpy as np

from visbrain.io import download_file, path_to_visbrain_data


class _TestVisbrain(object):
    """Visbrain testing utility methods."""

    OBJ = None
    NEEDED_FILES = {}

    def need_file(self, file):
        """Path to a needed file from visbrain-data."""
        return download_file(file, astype='example_data')

    def to_tmp_dir(self, file=None):
        """Path to a tmp dir in visbrain-data."""
        vb_path = os.path.join(path_to_visbrain_data(), 'tmp')
        if not os.path.exists(vb_path):
            os.makedirs(vb_path)
        return path_to_visbrain_data(file=file, folder='tmp')

    def assert_and_test(self, attr, to_set, to_test='NoAttr'):
        """Assert to obj and test."""
        # Set attribute :
        obj = 'self.OBJ'
        if isinstance(to_set, str):
            exec("{}.{}".format(obj, attr) + "='" + to_set + "'")
        else:
            exec("{}.{}".format(obj, attr) + ' = to_set')
        value = eval("{}.{}".format(obj, attr))
        # Test either to_set or to_test :
        value_to_test = to_set if to_test == 'NoAttr' else to_test
        # Test according to data type :
        if isinstance(value_to_test, np.ndarray):
            # Be sure that arrays have the same shape and dtype :
            value = value.reshape(*value_to_test.shape)
            value = value.astype(value_to_test.dtype)
            np.testing.assert_allclose(value, value_to_test)
        else:
            assert value == value_to_test

    def parent_testing(self, obj, parent):
        """Test setting parent."""
        obj.parent = parent
        assert obj.parent.name == parent.name
