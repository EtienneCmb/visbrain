"""Test functions in transform.py."""
import numpy as np

from visbrain.utils.transform import (vprescale, vprecenter, vpnormalize,
                                      array_to_stt, stt_to_array)


class TestTransform(object):
    """Test functions in transform.py."""

    @staticmethod
    def _test_vpmean(mat, tr):
        """Test if the center of (x, y, z) is [0., 0., 0.]."""
        assert np.array_equal(tr.map(mat).mean(0), [0., 0., 0., 1.])

    @staticmethod
    def _test_vpdist(mat, tr, dist):
        """Test if Peak to Peak along (x, y, z) is equal to dist."""
        mat_ptp = np.round(np.ptp(tr.map(mat), axis=0))
        assert np.array_equal(mat_ptp, [float(dist)] * 3 + [0.])

    def test_vprescale(self):
        """Test function vprescale."""
        mat = np.arange(30).reshape(10, 3)
        dist = 100.
        self._test_vpdist(mat, vprescale(mat, dist=dist), dist)

    def test_vprecenter(self):
        """Test function vprecenter."""
        mat = np.arange(30).reshape(10, 3)
        self._test_vpmean(mat, vprecenter(mat))

    def test_vpnormalize(self):
        """Test function vpnormalize."""
        mat = np.arange(30).reshape(10, 3)
        dist = 5.
        tr = vpnormalize(mat, dist=dist)
        self._test_vpmean(mat, tr)
        self._test_vpdist(mat, tr, dist)

    def test_array_to_stt(self):
        """Test function array_to_stt."""
        scale = (4., 5., 3.)
        translate = (10., 25., 7.)
        mat = np.array([[scale[0], 0., 0., translate[0]],
                        [0., scale[1], 0., translate[1]],
                        [0., 0., scale[2], translate[2]],
                        [0., 0., 0., 1.]
                        ])
        tf = array_to_stt(mat)
        _mat = stt_to_array(tf)
        assert np.array_equal(mat, _mat)
