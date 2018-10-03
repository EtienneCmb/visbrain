"""This script contains some usefull signal processing functions."""
import logging

import numpy as np
from scipy.signal import fftconvolve

from vispy.visuals.transforms import STTransform, NullTransform


__all__ = ('normalize', 'derivative', 'tkeo', 'zerocrossing', 'power_of_ten',
           'averaging', 'normalization', 'smoothing', 'smooth_3d')

logger = logging.getLogger('visbrain')


def normalize(x, tomin=0., tomax=1.):
    """Normalize the array x between tomin and tomax.

    Parameters
    ----------
    x : array_like
        The array to normalize
    tomin : int/float | 0.
        Minimum of returned array

    tomax : int/float | 1.
        Maximum of returned array

    Returns
    -------
    xn : array_like
        The normalized array
    """
    if x.size:
        x = np.float32(x)
        xm, xh = np.float32(x.min()), np.float32(x.max())
        if xm != xh:
            coef = (tomax - tomin) / (xh - xm)
            np.subtract(x, xh, out=x)
            np.multiply(x, coef, out=x)
            np.add(x, tomax, out=x)
            return x
            # return tomax - (((tomax - tomin) * (xh - x)) / (xh-xm))
        else:
            logger.debug("Normalization has been ignored because minimum and "
                         "maximum are both equal to " + str(xm))
            np.multiply(x, tomax, out=x)
            np.divide(x, xh, out=x)
            return x
    else:
        return x


def derivative(x, window, sf):
    """Compute first derivative of signal.

    Equivalent to np.gradient function

    Parameters
    ----------
    x : array_like
        Signal
    window : int
        Time (ms) window to compute first derivative
    sf : int
        Downsampling frequency
    """
    length = x.size
    step = int(window / (1000 / sf))
    tail = np.zeros(shape=(int(step / 2),))
    deriv = np.r_[tail, x[step:length] - x[0:length - step], tail]
    deriv = np.abs(deriv)
    # Check size
    if deriv.size < length:
        missing_pts = length - deriv.size
        tail = np.zeros(missing_pts)
        deriv = np.r_[deriv, tail]

    return deriv


def tkeo(x):
    """Calculate the TKEO of a given recording by using 2 samples.

    github.com/lvanderlinden/OnsetDetective/blob/master/OnsetDetective/tkeo.py

    Parameters
    ----------
    x : array_like
        Row vector of data.

    Returns
    -------
    a_tkeo : array_like
        Row vector containing the tkeo per sample.
    """
    # Create two temporary arrays of equal length, shifted 1 sample to the
    # right and left and squared:
    i = x[1:-1] * x[1:-1]
    j = x[2:] * x[:-2]

    # Calculate the difference between the two temporary arrays:
    a_tkeo = i - j
    return a_tkeo


def zerocrossing(data):
    """Find zero-crossings index of a signal.

    Parameters
    ----------
    x: array_like
        Data

    Returns
    -------
    index : array_like
        Row vector containing zero-crossing index.
    """
    pos = data > 0
    npos = ~pos
    return ((pos[:-1] & npos[1:]) | (npos[:-1] & pos[1:])).nonzero()[0] + 1


def power_of_ten(x, e=3):
    """Power of ten format.

    Parameters
    ----------
    x : float
        The floating point to transform.
    e : int | 2
        If x is over 10 ** -e and bellow 10 ** e, this function doesn't
        change the format.

    Returns
    -------
    xtronc: float
        The troncate version of x.
    power: int
        The power of ten to retrieve x.
    """
    sign = np.sign(x)
    x = np.abs(x)
    stx = str(x)
    if 0 < x <= 10 ** -e:  # x is a power of e- :
        if stx.find('e-') + 1:  # Format : 'xe-y'
            sp = stx.split('e-')
            return float(sp[0]), -int(sp[1])
        else:  # Format : 0.000x
            sp = stx.split('.')[1]
            id_l = 0
            while sp[id_l] == '0':
                id_l += 1
            id_l += 1
            return (sign * x) * (10 ** id_l), -id_l
    elif x >= 10 ** e:  # x is a power of e :
        if stx.find('e') + 1:  # Format : 'xey'
            sp = stx.split('e')
            return float(sp[0]), -int(sp[1])
        else:
            k = e
            while x % (10 ** k) != x:
                k += 1
            return (sign * x) / (10 ** (k - 1)), k - 1
    else:
        return sign * x, 0


def averaging(ts, n_window, axis=-1, overlap=0., window='flat'):
    """Take the mean of an ndarray.

    Parameters
    ----------
    ts : array_like
        Array of data to take the mean.
    n_window : int
        Number of sample per window.
    axis : int | -1
        Axis along which take the mean. By default, the last axis.
    overlap : float | None
        Overlap of successive window (0 <= overlap < 1). By default, no overlap
        is performed.
    window : {'flat', 'hanning', 'hamming', 'bartlett', 'blackman'}
        Windowing method.

    Returns
    -------
    average : array_like
        The averaged signal.
    """
    # Checking :
    assert isinstance(ts, np.ndarray)
    assert isinstance(axis, int) and axis <= ts.ndim - 1
    assert isinstance(n_window, int) and n_window < ts.shape[axis]
    assert isinstance(overlap, (float, int)) and 0. <= overlap < 1.
    assert window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']

    # Get axis :
    npts = ts.shape[axis]
    axis = ts.ndim - 1 if axis == -1 else axis

    # Get overlap step in samples :
    n_overlap = int(np.round(n_window * (1. - overlap)))

    # Build the index vector :
    ind = np.c_[np.arange(0, npts - n_window, n_overlap),
                np.arange(n_window, npts, n_overlap)]
    ind = np.vstack((ind, [npts - 1 - n_window, npts - 1]))  # add last window
    n_ind = ind.shape[0]

    # Get the window :
    if window == 'flat':  # moving average
        win = np.ones(n_window, 'd')
    else:
        win = eval('np.' + window + '(n_window)')

    rsh = tuple(1 if i != axis else -1 for i in range(ts.ndim))
    win = win.reshape(*rsh)

    # Define the averaging array :
    av_shape = tuple(k if i != axis else n_ind for i, k in enumerate(ts.shape))
    average = np.zeros(av_shape, dtype=float)

    # Compute averaging :
    sl_ts = [slice(None)] * ts.ndim
    sl_av = sl_ts.copy()
    for k in range(n_ind):
        sl_ts[axis], sl_av[axis] = slice(ind[k, 0], ind[k, 1]), slice(k, k + 1)
        average[tuple(sl_av)] += (ts[tuple(sl_ts)] * win).mean(axis=axis,
                                                               keepdims=True)

    return average


def normalization(data, axis=-1, norm=None, baseline=None):
    """Data normalization.

    Parameters
    ----------
    data : array_like
        Array of data.
    axis : int | -1
        Array along which to perform the normalization.
    norm : int | None
        The normalization type. Use :
            * 0 : no normalization
            * 1 : subtract the mean
            * 2 : divide by the mean
            * 3 : subtract then divide by the mean
            * 4 : subtract the mean then divide by deviation
    baseline : tuple | None
        Baseline period to consider. If None, the entire signal is used.

    Returns
    -------
    data_n : array_like
        The normalized array.
    """
    assert isinstance(data, np.ndarray)
    # assert norm in [None, ]

    # Take data in baseline (if defined) :
    if (baseline is not None) and (len(baseline) == 2):
        sl = [slice(None)] * data.ndim
        sl[axis] = slice(baseline[0], baseline[1])
        _data = data[tuple(sl)]
    else:
        _data = None

    if norm in [0, None]:  # don't normalize
        return data
    elif norm in [1, 2, 3, 4]:
        kw = {'axis': axis, 'keepdims': True}
        d_m = _data.mean(**kw) if _data is not None else data.mean(**kw)
        if norm == 1:  # subtract the mean
            data -= d_m
        elif norm == 2:  # divide by the mean
            d_m[d_m == 0] = 1.
            data /= d_m
        elif norm == 3:  # subtract then divide by the mean
            data -= d_m
            d_m[d_m == 0] = 1.
            data /= d_m
        elif norm == 4:  # z-score
            d_std = _data.mean(**kw) if _data is not None else data.mean(**kw)
            d_std[d_std == 0] = 1.
            data -= d_m
            data /= d_std


def smoothing(x, n_window=10, window='hanning'):
    """Smooth the data using a window with requested size.

    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.

    Parameters
    ----------
    x : array_like
        1-D array to smooth.
    n_window : int | 10
        Window length.
    window : string, array_like | 'hanning'
        Use either 'flat', 'hanning', 'hamming', 'bartlett', 'blackman' or pass
        a numpy array of length n_window.

    Returns
    -------
        The smoothed signal
    """
    n_window = int(n_window)
    assert isinstance(x, np.ndarray) and x.ndim == 1
    assert len(x) > n_window
    assert isinstance(window, (str, np.ndarray))
    if isinstance(window, str):
        assert window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']
    elif isinstance(window, np.ndarray):
        assert len(window) == n_window

    if n_window < 3:
        return x

    s = np.r_[2 * x[0] - x[n_window:1:-1], x, 2 * x[-1] - x[-1:-n_window:-1]]
    if window == 'flat':  # Moving average
        w = np.ones((n_window,))
    else:
        w = eval('np.' + window + '(n_window)')

    y = np.convolve(w / w.sum(), s, mode='same')
    return y[n_window - 1:-n_window + 1]


def smooth_3d(vol, smooth_factor=3, correct=True):
    """Smooth a 3-D volume.

    Parameters
    ----------
    vol : array_like
        The volume of shape (N, M, P)
    smooth_factor : int | 3
        The smoothing factor.

    Returns
    -------
    vol_smooth : array_like
        The smooth volume with the same shape as vol.
    """
    tf = NullTransform()
    # No smoothing :
    if (not isinstance(smooth_factor, int)) or (smooth_factor < 3):
        return vol, tf
    # Smoothing array :
    sz = np.full((3,), smooth_factor, dtype=int)
    smooth = np.ones([smooth_factor] * 3) / np.prod(sz)
    # Apply smoothing :
    sm = fftconvolve(vol, smooth, mode='same')
    if correct:
        # Get the shape of the vol and the one with 'full' convolution :
        vx, vy, vz = vol.shape
        vcx, vcy, vcz = np.array([vx, vy, vz]) + smooth_factor - 1
        # Define transform :
        sc = [vx / vcx, vy / vcy, vz / vcz]
        tr = .5 * np.array([smooth_factor] * 3)
        tf = STTransform(scale=sc, translate=tr)
    return sm, tf
