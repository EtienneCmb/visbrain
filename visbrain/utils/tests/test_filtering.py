"""Test functions in filetring.py."""
import numpy as np
import math
from itertools import product

from visbrain.utils.filtering import (filt, morlet, ndmorlet, morlet_power,
                                      welch_power, PrepareData)


class TestFiltering(object):
    """Test functions in filtering.py."""

    @staticmethod
    def _get_data(mean=False):
        if mean:
            return np.random.rand(2000), 3., 512.
        else:
            return np.random.rand(2000), [2., 4.], 512.

    def __iter__(self):
        """Iterate over filtering options."""
        btype = ['bandpass', 'bandstop', 'highpass', 'lowpass']
        order = [2, 3, 5]
        method = ['butterworth', 'bessel']
        way = ['filtfilt', 'lfilter']
        for k in product(btype, order, method, way):
            yield k

    def test_filt(self):
        """Test filt function."""
        x, f, sf = self._get_data()
        for k in self:
            filt(sf, f, x, *k)

    def test_morlet(self):
        """Test morlet function."""
        x, f, sf = self._get_data(True)
        morlet(x, sf, f)

    def test_ndmorlet(self):
        """Test ndmorlet function."""
        x, f, sf = self._get_data(True)
        for k in [None, 'amplitude', 'phase', 'power']:
            ndmorlet(x, sf, f, get=k)

    def test_morlet_power(self):
        """Test morlet_power function."""
        x, _, sf = self._get_data(True)
        f = [1., 2., 3., 4.]
        assert morlet_power(x, f, sf, norm=False).sum(0).max() > 1.
        assert math.isclose(morlet_power(x, f, sf, norm=True).sum(0).max(), 1.)

    def test_welch_power(self):
        """Test welch_power function."""
        x, _, _ = self._get_data(True)
        f = [5, 10., 15]
        sf = 100.
        assert math.isclose(welch_power(x, f, sf, norm=True).sum(0).max(), 1.)

    def test_prepare_data(self):
        """Test class PrepareData."""
        p = PrepareData(demean=True, detrend=True)
        x, f, sf = self._get_data()
        time = np.arange(len(x)) / sf
        for k in self:
            for i in ['filter', None, 'amplitude', 'phase', 'power']:
                p.btype = k[0]
                p.forder = k[1]
                p.filt_meth = k[2]
                p.way = k[3]
                p.dispas = i
                p._prepare_data(sf, x, time)
