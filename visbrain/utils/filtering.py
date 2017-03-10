"""Set of tools to filter data."""

import numpy as np
from scipy.signal import butter, filtfilt, lfilter, bessel

__all__ = ['filt', 'morlet', 'ndmorlet']

#############################################################################
# FILTERING
#############################################################################


def filt(sf, f, x, btype='bandpass', order=3, method='butterworth',
         way='filtfilt', axis=0):
    """Filt data.

    Args:
        sf: float
            The sampling frequency

        f: np.ndarray
            Frequency vector (2,)

        x: np.ndarray
            The data to filt.

    Kargs:
        btype: string, optional, (def: 'bandpass')
            The filter type. Choose between bandpass, bandstop, highpass,
            lowpass. If highpass, the first value of f will be used. If lowpass
            the second value of f will be used.

        order: int, optional, (def: 3)
            The filter order.

        method: string, optional, (def: 'butterworth')
            The type of filter to use. Could be butterworth or bessel.

        way: string, optional, (def: 'filtfilt')
            Specify if the filter has to be one way ('lfilter') or two ways
            ('filtfilt').

        axis: int, optional, (def: 0)
            The axis along which the filter is applied.

    Returns:
        xfilt: np.ndarray
            Filtered data.
    """
    # Normalize frequency vector according to btype :
    if btype in ['bandpass', 'bandstop']:
        fnorm = np.divide(f, .5 * sf)
    elif btype == 'lowpass':
        fnorm = np.array(f[-1] / (.5 * sf))
    elif btype == 'highpass':
        fnorm = np.array(f[0] / (.5 * sf))

    # Get filter coefficients :
    if method == 'butterworth':
        b, a = butter(order, fnorm, btype=btype)
    elif method == 'bessel':
        b, a = bessel(order, fnorm, btype=btype)

    # Apply filter :
    if way == 'filtfilt':
        return filtfilt(b, a, x, axis=axis)
    elif way == 'lfilter':
        return lfilter(b, a, x, axis=axis)

#############################################################################
# MORLET
#############################################################################


def _morlet_wlt(sf, f, width=7.0):
    """Get a Morlet's wavelet.

    Args:
        sf: float
            Sampling frequency

        f: np.ndarray, shape (2,)
            Frequency vector

        width: float, optional, (def: 7.0)
            Width of the wavelet

    Kargs:
        wlt: np.ndarray
            Morlet wavelet
    """
    sf, f, width = float(sf), float(f), float(width)
    dt = 1 / sf
    sf = f / width
    st = 1 / (2 * np.pi * sf)

    # Build morlet wavelet :
    t = np.arange(-width * st / 2, width * st / 2, dt)
    A = 1 / np.sqrt((st * np.sqrt(np.pi)))
    wlt = A * np.exp(-np.square(t) / (2 * np.square(st))) * np.exp(
                                                       1j * 2 * np.pi * f * t)

    return wlt


def morlet(x, sf, f, width=7.0):
    """Complex decomposition of a signal x using the morlet wavelet.

    Args:
        x: np.ndarray, shape (N,)
            The signal to use for the complex decomposition. Must be
            a vector of length N.

        sf: float
            Sampling frequency

        f: np.ndarray, shape (2,)
            Frequency vector

    Kargs:
        width: float, optional, (def: 7.0)
            Width of the wavelet

    Returns:
        xout: np.ndarray, shape (N,)
            The complex decomposition of the signal x.
    """
    # Get the wavelet :
    m = _morlet_wlt(sf, f, width)

    # Compute morlet :
    y = np.convolve(x, m)
    xout = y[int(np.ceil(len(m) / 2)) - 1:int(len(y) - np.floor(len(m) / 2))]

    return xout


def ndmorlet(x, sf, f, axis=0, get=None, width=7.0):
    """Complex decomposition using Morlet's wlt for a multi-dimentional array.

    Args:
    x: array
        The signal to use for the complex decomposition.

    sf: float
        Sampling frequency

    f: array, shape (2,)
        Frequency vector

    axis: integer, optional, (def: 0)
        Specify the axis where is located the time dimension

    width: float, optional, (def: 7.0)
        Width of the wavelet

    Returns:
        xout: array, same shape as x
            Complex decomposition of x.
    """
    # Get the wavelet :
    m = _morlet_wlt(sf, f, width)

    # Define a morlet function :
    def morletFcn(xt):
        # Compute morlet :
        y = np.convolve(xt, m)
        return y[int(np.ceil(len(m) / 2)) - 1:int(len(y) - np.floor(
                                                                len(m) / 2))]

    return np.apply_along_axis(morletFcn, axis, x)
