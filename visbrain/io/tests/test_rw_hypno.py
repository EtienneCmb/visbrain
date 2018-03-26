"""Test functions in rw_hypno.py."""
import numpy as np

from visbrain.tests._tests_visbrain import _TestVisbrain
from visbrain.io.rw_hypno import (hypno_time_to_sample, hypno_sample_to_time,
                                  oversample_hypno, write_hypno, read_hypno)

versions = dict(time=['.txt', '.csv', '.xlsx'], sample=['.txt', '.hyp'])


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
        hyp_new, time_new, sf_new = hypno_time_to_sample(df.copy(), len(hyp))
        hyp_new_2, _, _ = hypno_time_to_sample(df.copy(), time)
        # Test :
        np.testing.assert_array_equal(hyp, hyp_new)
        np.testing.assert_array_equal(hyp_new, hyp_new_2)
        np.testing.assert_array_almost_equal(time, time_new)
        assert sf == sf_new

    def test_oversample_hypno(self):
        """Test function oversample_hypno."""
        hyp = self._get_hypno()
        hyp_over = oversample_hypno(hyp, 12)
        to_hyp = np.array([-1, -1, 4, 4, 2, 2, 3, 3, 0, 0, 0, 0])
        assert np.array_equal(hyp_over, to_hyp)

    def test_write_hypno(self):
        """Test function write_hypno_txt."""
        hyp = self._get_hypno()
        sf, npts = 1., len(hyp)
        time = np.arange(npts) / sf
        info = {'Info_1': 10, 'Info_2': 'coco', 'Info_3': 'veut_un_gateau'}
        for k in versions.keys():
            for e in versions[k]:
                filename = self.to_tmp_dir('hyp_test_' + k + e)
                write_hypno(filename, hyp, version=k, sf=sf, npts=npts,
                            window=1., time=time, info=info)

    def test_read_hypno(self):
        """Test function read_hypno."""
        hyp = self._get_hypno()
        sf, npts = 1., len(hyp)
        time = np.arange(npts) / sf
        for k in versions.keys():
            for e in versions[k]:
                filename = self.to_tmp_dir('hyp_test_' + k + e)
                hyp_new, _ = read_hypno(filename, time=time)
                np.testing.assert_array_equal(hyp, hyp_new)
