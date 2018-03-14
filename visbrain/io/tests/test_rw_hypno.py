"""Test functions in rw_hypno.py."""
import numpy as np

from visbrain.tests._tests_visbrain import _TestVisbrain
from visbrain.io.rw_hypno import (oversample_hypno, write_hypno_txt,
                                  write_hypno_hyp, read_hypno, read_hypno_hyp,
                                  read_hypno_txt)


class TestRwHypno(_TestVisbrain):
    """Test functions in rw_hypno.py."""

    @staticmethod
    def _get_hypno():
        return np.array([-1, 4, 2, 3, 0])

    def test_oversample_hypno(self):
        """Test function oversample_hypno."""
        hyp = self._get_hypno()
        hyp_over = oversample_hypno(hyp, 12)
        to_hyp = np.array([-1, -1, 4, 4, 2, 2, 3, 3, 0, 0, 0, 0])
        assert np.array_equal(hyp_over, to_hyp)

    def test_write_hypno_txt(self):
        """Test function write_hypno_txt."""
        hyp = self._get_hypno()
        write_hypno_txt(self.to_tmp_dir('hyp.txt'), hyp, 1000., 5000)

    def test_write_hypno_hyp(self):
        """Test function write_hypno_hyp."""
        hyp = self._get_hypno()
        write_hypno_hyp(self.to_tmp_dir('hyp.hyp'), hyp, 1000., 5000)

    def test_read_hypno(self):
        """Test function read_hypno."""
        # TXT version :
        hyp_txt, sf_txt = read_hypno(self.to_tmp_dir('hyp.txt'))
        # HYP version :
        hyp_hyp, sf_hyp = read_hypno(self.to_tmp_dir('hyp.hyp'))
        assert np.array_equal(hyp_txt, hyp_hyp)
        assert sf_txt == sf_hyp

    def test_read_hypno_hyp(self):
        """Test function read_hypno_hyp."""
        read_hypno_hyp(self.to_tmp_dir('hyp.hyp'))

    def test_read_hypno_txt(self):
        """Test function read_hypno_txt."""
        read_hypno_txt(self.to_tmp_dir('hyp.txt'))
