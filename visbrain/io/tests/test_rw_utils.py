"""Test functions in rw_utils.py."""
import numpy as np
from visbrain.io.rw_utils import get_file_ext, safety_save
from visbrain.tests._tests_visbrain import _TestVisbrain


class TestRwUtils(_TestVisbrain):
    """Test functions in rw_utils.py."""

    def test_get_file_ext(self):
        """Test function get_file_ext."""
        np.savetxt(self.to_tmp_dir('test_rw_utils.txt'), np.arange(100))
        file, ext = get_file_ext(self.to_tmp_dir('test_rw_utils.txt'))
        assert file[-1] != '.'
        assert ext == '.txt'

    def test_safety_save(self):
        """Test function safety_save."""
        file = safety_save(self.to_tmp_dir('test_rw_utils.txt'))
        file_txt, _ = get_file_ext(self.to_tmp_dir('test_rw_utils.txt'))
        assert file == file_txt + '(1).txt'
