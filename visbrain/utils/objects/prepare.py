"""Prepare data before plotting."""
import numpy as np
import scipy.signal as scpsig
from ..filtering import filt, ndmorlet


class PrepareData(object):
    """Prepare data before plotting.

    This class group a set of signal processing tools including :
        - De-meaning
        - De-trending
        - Filtering
        - Decomposition (filter / amplitude / power / phase)
    """

    def __init__(self, axis=0, demean=False, detrend=False, filt=False,
                 fstart=12., fend=16., forder=3, way='lfilter',
                 filt_meth='butterworth', btype='bandpass', dispas='filter'):
        """Init."""
        # Axis along which to perform preparation :
        self.axis = axis
        # Demean and detrend :
        self.demean = demean
        self.detrend = detrend
        # Filtering :
        self.filt = filt
        self.fstart, self.fend = fstart, fend
        self.forder, self.filt_meth = forder, filt_meth
        self.way, self.btype = way, btype
        self.dispas = dispas

    def __bool__(self):
        """Return if data have to be prepared."""
        return any([self.demean, self.detrend, self.filt])

    def _prepare_data(self, sf, data, time):
        """Prepare data before plotting."""
        # ============= DEMEAN =============
        if self.demean:
            mean = np.mean(data, axis=self.axis, keepdims=True)
            np.subtract(data, mean, out=data)

        # ============= DETREND =============
        if self.detrend:
            data = scpsig.detrend(data, axis=self.axis)

        # ============= FILTERING =============
        if self.filt:
            if self.dispas == 'filter':
                data = filt(sf, np.array([self.fstart, self.fend]), data,
                            btype=self.btype, order=self.forder, way=self.way,
                            method=self.filt_meth, axis=self.axis)
            else:
                # Compute ndwavelet :
                f = np.array([self.fstart, self.fend]).mean()
                data = ndmorlet(data, sf, f, axis=self.axis, get=self.dispas)

        return data

    def update(self):
        """Update object."""
        if self._fcn is not None:
            self._fcn()
