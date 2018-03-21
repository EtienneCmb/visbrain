"""Test functions in rw_hypno.py."""
import numpy as np

from visbrain.tests._tests_visbrain import _TestVisbrain
from visbrain.io.rw_hypno import (hypno_time_to_sample, hypno_sample_to_time,
                                  oversample_hypno, write_hypno_txt,
                                  write_hypno_hyp, write_hypno_xlsx,
                                  read_hypno, read_hypno_hyp, read_hypno_txt)


class TestRwHypno(_TestVisbrain):
    """Test functions in rw_hypno.py."""

    @staticmethod
    def _get_hypno():
        return np.array([-1, 4, 2, 3, 0])

    def test_hypno_conversion(self):
        """Test conversion functions."""
        hyp = np.array([-1, -1, 4, 4, 2, 2, 3, 3, 0, 0, 0, 0, 1, 1, 1, -1, -1])
        sf = 100.
        time = np.arange(len(hyp)) / sf
        # Sample -> time :
        df = hypno_sample_to_time(hyp, time)
        # Time -> sample :
        hyp_new, time_new, sf_new = hypno_time_to_sample(df, len(hyp))
        # Test :
        np.testing.assert_array_equal(hyp, hyp_new)
        np.testing.assert_array_almost_equal(time, time_new)
        assert sf == sf_new

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

    def test_write_hypno_xlsx(self):
        """Test function write_hypno_xlsx."""
        hyp = self._get_hypno()
        time = np.arange(len(hyp)) / 100.
        write_hypno_xlsx(self.to_tmp_dir('hyp.xlsx'), hyp, time)

    def test_read_hypno(self):
        """Test function read_hypno."""
        # TXT version :
        hyp_txt, sf_txt = read_hypno(self.to_tmp_dir('hyp.txt'))
        # HYP version :
        hyp_hyp, sf_hyp = read_hypno(self.to_tmp_dir('hyp.hyp'))
        # XLSX version :
        time = np.arange(len(self._get_hypno())) / 100.
        hyp_xlsx, sf_xlsx = read_hypno(self.to_tmp_dir('hyp.xlsx'), time=time)
        assert np.array_equal(hyp_txt, hyp_hyp)
        assert np.array_equal(hyp_txt, hyp_xlsx)
        assert sf_txt == sf_hyp

    def test_read_hypno_hyp(self):
        """Test function read_hypno_hyp."""
        read_hypno_hyp(self.to_tmp_dir('hyp.hyp'))

    def test_read_hypno_txt(self):
        """Test function read_hypno_txt."""
        read_hypno_txt(self.to_tmp_dir('hyp.txt'))
