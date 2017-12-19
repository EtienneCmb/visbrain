"""Test functions in detections.py."""
import numpy as np

from visbrain.utils.sleep.detection import (kcdetect, spindlesdetect,
                                            remdetect, slowwavedetect,
                                            mtdetect, peakdetect)


class TestDetections(object):
    """Test functions in detection.py."""

    @staticmethod
    def _get_eeg_dataset(n=10014, sf=100., sine=False, f=4., amp=1.,
                         offset=0.):
        """Generate a random eeg dataset."""
        if sine:
            time = np.arange(n) / sf
            data = np.sin(3 * np.pi * f * time)
            # data += .05 * np.random.rand(*data.shape)
        else:
            data = np.random.randn(n)
        data *= amp
        data += offset
        return data, sf

    @staticmethod
    def _get_eeg_hypno(n=10014):
        """Generate a random hypnogram."""
        if n % 6:
            n_per_seg = n / 6
            wake = np.zeros((n_per_seg,))
            n1 = np.ones((n_per_seg,))
            n2 = np.full((n_per_seg,), 2)
            n3 = np.full((n_per_seg,), 3)
            rem = np.full((n_per_seg,), 4)
            art = np.full((n_per_seg,), -1)
            return np.hstack((wake, n1, n2, n3, rem, art))
        else:
            return np.random.randint(-1, 4, n)

    def test_kcdetect(self):
        """Test function kcdetect."""
        # Get a dataset example :
        data, sf = self._get_eeg_dataset()
        hypno = self._get_eeg_hypno()
        kcdetect(data, sf, .8, 1., hypno, True, 100, 200, .2, .6)

    def test_spindlesdetect(self):
        """Test function spindlesdetect."""
        # Get a dataset example :
        data, sf = self._get_eeg_dataset()
        hypno = self._get_eeg_hypno()
        spindlesdetect(data, sf, .1, hypno, True)

    def test_remdetect(self):
        """Test function remdetect."""
        # Get a dataset example :
        data, sf = self._get_eeg_dataset()
        hypno = self._get_eeg_hypno()
        remdetect(data, sf, hypno, True, .1)

    def test_slowwavedetect(self):
        """Test function slowwavedetect."""
        # Get a dataset example :
        data, sf = self._get_eeg_dataset(n=10000, sine=True, offset=300., f=.7)
        slowwavedetect(data, sf, .8, min_duration_ms=5.)

    def test_mtdetect(self):
        """Test function mtdetect."""
        # Get a dataset example :
        data, sf = self._get_eeg_dataset()
        hypno = self._get_eeg_hypno()
        mtdetect(data, sf, .1, hypno, True)

    def test_peakdetect(self):
        """Test function peakdetect."""
        # Get a dataset example :
        data, sf = self._get_eeg_dataset(n=1000, sine=True, f=4., sf=128.)
        peakdetect(sf, data, get='min')
        peakdetect(sf, data, get='max')
        peakdetect(sf, data, get='minmax', threshold=.6)
