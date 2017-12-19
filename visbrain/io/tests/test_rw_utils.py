"""Test functions in rw_utils.py."""
from visbrain.io.rw_utils import get_file_ext, safety_save
from visbrain.tests._tests_visbrain import _TestVisbrain


class TestRwUtils(_TestVisbrain):
    """Test functions in rw_utils.py."""

    def test_get_file_ext(self):
        """Test function get_file_ext."""
        file, ext = get_file_ext(self.to_tmp_dir('hyp.txt'))
        assert file[-1] != '.'
        assert ext == '.txt'

    def test_safety_save(self):
        """Test function safety_save."""
        file = safety_save(self.to_tmp_dir('hyp.txt'))
        file_txt, _ = get_file_ext(self.to_tmp_dir('hyp.txt'))
        assert file == file_txt + '(1).txt'
