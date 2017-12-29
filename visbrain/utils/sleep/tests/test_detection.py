"""Test functions in detections.py."""
import numpy as np

from visbrain.utils.sleep.detection import (kcdetect, spindlesdetect,
                                            remdetect, slowwavedetect,
                                            mtdetect, peakdetect)
from visbrain.utils import generate_eeg

"""If tests continue to failed, one idea could be to save in a npz file the
signal to test.
"""
sf, n_pts, _rnd = 100., 10014, 1
signal = np.squeeze(generate_eeg(sf=sf, n_pts=n_pts, random_state=_rnd)[0])

n_per_seg = int(n_pts / 6)
wake = np.zeros((n_per_seg,))
n1 = np.ones((n_per_seg,))
n2 = np.full((n_per_seg,), 2)
n3 = np.full((n_per_seg,), 3)
rem = np.full((n_per_seg,), 4)
art = np.full((n_per_seg,), -1)
hypno = np.hstack((wake, n1, n2, n3, rem, art))


class TestDetections(object):
    """Test functions in detection.py."""

    def test_kcdetect(self):
        """Test function kcdetect."""
        kcdetect(signal, sf, .8, 1., hypno, True, 100, 200, .2, .6)

    def test_spindlesdetect(self):
        """Test function spindlesdetect."""
        spindlesdetect(signal, sf, .1, hypno, True)

    def test_remdetect(self):
        """Test function remdetect."""
        remdetect(signal, sf, hypno, True, .1)

    def test_slowwavedetect(self):
        """Test function slowwavedetect."""
        slowwavedetect(signal, sf, .8)

    def test_mtdetect(self):
        """Test function mtdetect."""
        mtdetect(signal, sf, .1, hypno, True)

    def test_peakdetect(self):
        """Test function peakdetect."""
        # Get a dataset example :
        data = np.sin(3 * np.pi * 1 * np.arange(100))
        peakdetect(sf, data, get='min')
        peakdetect(sf, data, get='max')
        peakdetect(sf, data, get='minmax', threshold=.6)
